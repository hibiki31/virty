import fcntl
import os
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import HTTPException
from mixin.log import setup_logger
from module.paramikolib import ParamikoManager
from resource_authorization import allowed_node_names, require_admin

from .models import NodeModel
from .schemas import (
    Node,
    NodeForQuery,
    NodeInfo,
    NodePage,
    SSHKeyPair,
    SSHPublicKey,
)

app = APIRouter(prefix="/api/nodes", tags=["nodes"])
logger = setup_logger(__name__)

SSH_DIRECTORY = Path("/root/.ssh")
SSH_KEY_NAMES = ("id_rsa", "id_ed25519")


def _fsync_path(path: Path) -> None:
    """鍵dataとrenameを永続化し、電源断後の片方だけの消失を避ける。"""

    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextmanager
def _ssh_key_install_lock() -> Iterator[None]:
    """RESTとAgent workerをまたいでSSH鍵pairの交換を直列化する。"""

    SSH_DIRECTORY.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(SSH_DIRECTORY, 0o700)
    flags = os.O_CREAT | os.O_RDWR | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(SSH_DIRECTORY / ".virty-key-install.lock", flags, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _install_ssh_key_pair(
    *,
    key_name: str,
    private_key: str,
    public_key: str,
) -> None:
    """既存の利用可能な鍵を、新しい鍵pairの検証完了まで保持する。"""

    with _ssh_key_install_lock():
        with tempfile.TemporaryDirectory(
            prefix=".virty-key-",
            dir=SSH_DIRECTORY,
        ) as temp:
            temporary = Path(temp)
            private_path = temporary / key_name
            public_path = temporary / f"{key_name}.pub"
            private_path.write_text(
                private_key.rstrip("\r\n") + "\n",
                encoding="utf-8",
            )
            public_path.write_text(
                public_key.rstrip("\r\n") + "\n",
                encoding="utf-8",
            )
            os.chmod(private_path, 0o600)
            os.chmod(public_path, 0o600)
            _fsync_path(private_path)
            _fsync_path(public_path)
            # SSH接続に使うprivate keyを最後に切り替える。
            os.replace(public_path, SSH_DIRECTORY / f"{key_name}.pub")
            os.replace(private_path, SSH_DIRECTORY / key_name)
            _fsync_path(SSH_DIRECTORY)

        for stale_name in SSH_KEY_NAMES:
            if stale_name == key_name:
                continue
            (SSH_DIRECTORY / stale_name).unlink(missing_ok=True)
            (SSH_DIRECTORY / f"{stale_name}.pub").unlink(missing_ok=True)
        _fsync_path(SSH_DIRECTORY)


@app.get("", response_model=NodePage)
def get_nodes(
        param: NodeForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    current_user.verify_scope(["node.read"])
    query = db.query(NodeModel)
    allowed_nodes = allowed_node_names(db, current_user)
    if allowed_nodes is not None:
        query = query.filter(NodeModel.name.in_(allowed_nodes))
    if param.name_like:
        query = query.filter(NodeModel.name.like(f'%{param.name_like}%'))
    
    count = query.count()
    if param.limit > 0:
        query = query.limit(param.limit).offset(int(param.limit * param.page))


    return {"count": count, "data": query.all()}


@app.post("/key")
def create_ssh_key_pair(
        model: SSHKeyPair,
        current_user: CurrentUser = Depends(get_current_user)
):
    current_user.verify_scope(["node.credentials"])
    require_admin(current_user)
    
    if model.generate:
        SSH_DIRECTORY.mkdir(mode=0o700, parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".virty-generate-", dir=SSH_DIRECTORY) as temp:
            generated_path = Path(temp) / "id_ed25519"
            cmd = [
                "ssh-keygen",
                "-t", "ed25519",
                "-f", str(generated_path),
                "-N", "",
                "-q",
            ]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError:
                logger.error("SSH鍵の生成に失敗しました", exc_info=True)
                raise
            _install_ssh_key_pair(
                key_name="id_ed25519",
                private_key=generated_path.read_text(encoding="utf-8"),
                public_key=generated_path.with_suffix(".pub").read_text(encoding="utf-8"),
            )
            
    else:
        if not model.private_key or not model.public_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Private and public keys are required",
            )
        try:
            private_key = serialization.load_ssh_private_key(model.private_key.encode(), password=None)
        except (TypeError, ValueError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Unknown or unsupported key format")

        if isinstance(private_key, rsa.RSAPrivateKey):
            key_name = "id_rsa"
        elif isinstance(private_key, ed25519.Ed25519PrivateKey):
            key_name = "id_ed25519"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Unknown or unsupported key format")

        derived_public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        ).decode("ascii")
        supplied_parts = model.public_key.strip().split()
        if supplied_parts[:2] != derived_public_key.split()[:2]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Public key does not match the private key",
            )
        _install_ssh_key_pair(
            key_name=key_name,
            private_key=model.private_key,
            public_key=derived_public_key,
        )

    return {}


@app.get("/key", response_model=SSHPublicKey)
def get_ssh_key_pair(current_user: CurrentUser = Depends(get_current_user)):
    current_user.verify_scope(["node.read"])
    require_admin(current_user)
    home = os.path.expanduser("~")
    keys = {
        "id_rsa.pub": os.path.join(home, ".ssh", "id_rsa.pub"),
        "id_ed25519.pub": os.path.join(home, ".ssh", "id_ed25519.pub"),
    }

    pub_key_path = None
    for path in keys.values():
        if os.path.isfile(path):
            pub_key_path = path
            break

    if pub_key_path is None:
        raise HTTPException(status_code=404, detail="SSH public key is not configured")

    with open(pub_key_path) as f:
        public_key = f.read()

    return SSHPublicKey(public_key=public_key)


@app.get("/{name}", response_model=Node)
def get_node(
        name: str,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    cu.verify_scope(["node.read"])
    node = db.query(NodeModel).filter(NodeModel.name==name).one_or_none()
    allowed_nodes = allowed_node_names(db, cu)
    if node is None or (allowed_nodes is not None and name not in allowed_nodes):
        raise HTTPException(status_code=404, detail="node is not found")

    return node


@app.get("/{name}/facts")
def get_node_facts(
        name: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    current_user.verify_scope(["node.read"])
    require_admin(current_user)
    node = db.query(NodeModel).filter(NodeModel.name == name).one_or_none()
    
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")

    return node.ansible_facts


@app.get("/{name}/info",response_model=NodeInfo)
def get_node_info(
        name: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    current_user.verify_scope(["node.read"])
    require_admin(current_user)
    node:NodeModel = db.query(NodeModel).filter(NodeModel.name == name).one_or_none()
    
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    
    ssh_manager = ParamikoManager(user=node.user_name, domain=node.domain, port=node.port)
    
    
    res = NodeInfo(
        ip_address     = ssh_manager.run_cmd("ip a").stdout,
        ip_route       = ssh_manager.run_cmd("ip r").stdout,
        ip_neigh       = ssh_manager.run_cmd("ip neigh").stdout,
        df_h           = ssh_manager.run_cmd("df -h").stdout,
        lsblk          = ssh_manager.run_cmd("lsblk").stdout,
        uptime         = ssh_manager.run_cmd("uptime -p").stdout,
        free           = ssh_manager.run_cmd("free -h").stdout,
        top            = ssh_manager.run_cmd("top -b -n 1|head -n 20").stdout,
        iptables_nat   = ssh_manager.run_cmd("sudo iptables -L -t nat").stdout,
        iptables       = ssh_manager.run_cmd("sudo iptables -L").stdout,
        netplan_get    = ssh_manager.run_cmd("sudo netplan get").stdout,
    )

    return res



# @app.get("/nodes/pools", tags=["nodes"])
# def get_api_nodes_pools(
#         db: Session = Depends(get_db)
#     ):

#     return db.query(PoolCpuModel).all()


# @app.post("/nodes/pools", tags=["nodes"])
# def post_api_nodes_pools(
#         model: NodeBase,
#         db: Session = Depends(get_db),
#     ):
#     pool_model = PoolCpuModel(name=model.name)
#     db.add(pool_model)
#     db.commit()
#     return True


# @app.patch("/nodes/pools", tags=["nodes"])
# def patch_api_nodes_pools(
#         model: NodePoolForUpdate,
#         db: Session = Depends(get_db),
#     ):
#     ass = AssociationPoolsCpuModel(pool_id=model.pool_id, node_name=model.node_name, core=model.core)
#     db.add(ass)
#     db.commit()
#     return True
