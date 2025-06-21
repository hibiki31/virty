import os
import subprocess

from cryptography.hazmat.primitives import serialization
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import HTTPException, raise_forbidden
from mixin.log import setup_logger
from module.paramikolib import ParamikoManager

from .funcstion import delete_ssh_keys
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


@app.get("", response_model=NodePage)
def get_nodes(
        param: NodeForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    
    query = db.query(NodeModel)
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
    if not current_user.verify_scope(scopes=["admin"]):
        raise_forbidden()
    
    if model.generate:
        delete_ssh_keys()
        
        cmd = [
            "ssh-keygen",
            "-t", "ed25519",
            "-f", "/root/.ssh/id_ed25519",
            "-N", "",
            "-q"
        ]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("Key generation failed:", e)
            raise e
            
    else:
        os.makedirs('/root/.ssh/', exist_ok=True)
        
        try:
            private_key = serialization.load_ssh_private_key(model.private_key.encode(), password=None)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Unknown or unsupported key format")
        
        key_type = type(private_key).__name__
        if "RSA" in key_type:
            key_name = "id_rsa"
        elif "Ed25519" in key_type:
            key_name = "id_ed25519"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Unknown or unsupported key format")
        
        delete_ssh_keys()
        
        with open(f"/root/.ssh/{key_name}", "w") as f:
            f.write(model.private_key.rstrip('\r\n') + '\n')
        with open(f"/root/.ssh/{key_name}.pub", "w") as f:
            f.write(model.public_key)
        
        os.chmod('/root/.ssh/', 0o700)
        os.chmod(f"/root/.ssh/{key_name}", 0o600)
        os.chmod(f"/root/.ssh/{key_name}.pub", 0o600)

    return {}


@app.get("/key", response_model=SSHPublicKey)
def get_ssh_key_pair(current_user: CurrentUser = Depends(get_current_user)):
    home = os.path.expanduser("~")
    keys = {
        "id_rsa.pub": os.path.join(home, ".ssh", "id_rsa.pub"),
        "id_ed25519.pub": os.path.join(home, ".ssh", "id_ed25519.pub"),
    }

    for name, path in keys.items():
        if os.path.isfile(path):
            pub_key_path = path
        else:
            pub_key_path = path
    
    with open(pub_key_path) as f:
        public_key = f.read()

    return SSHPublicKey(public_key=public_key)


@app.get("/{name}", response_model=Node)
def get_node(
        name: str,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    node = db.query(NodeModel).filter(NodeModel.name==name).one_or_none()
    if node is None:
        raise HTTPException(status_code=404, detail="node is not found")

    return node


@app.get("/{name}/facts")
def get_node_facts(
        name: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

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

    node:NodeModel = db.query(NodeModel).filter(NodeModel.name == name).one_or_none()
    
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    
    ssh_manager = ParamikoManager(user=node.user_name, domain=node.domain, port=node.port)
    
    
    res = NodeInfo(
        ip_address = ssh_manager.run_cmd("ip a").stdout,
        ip_route   = ssh_manager.run_cmd("ip r").stdout,
        ip_neigh   = ssh_manager.run_cmd("ip neigh").stdout,
        df_h       = ssh_manager.run_cmd("df -h").stdout,
        lsblk      = ssh_manager.run_cmd("lsblk").stdout,
        uptime     = ssh_manager.run_cmd("uptime -p").stdout,
        free       = ssh_manager.run_cmd("free -h").stdout,
        top        = ssh_manager.run_cmd("top -b -n 1|head -n 20").stdout
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