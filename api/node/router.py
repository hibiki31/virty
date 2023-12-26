from os import chmod, makedirs
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.router import CurrentUser, get_current_user
from mixin.database import get_db
from mixin.exception import HTTPException
from mixin.log import setup_logger
from module.sshlib import SSHManager

from .models import NodeModel
from .schemas import (
    Node,
    NodeForQuery,
    NodeInterface,
    NodeInterfaceIpv4Info,
    NodeInterfaceIpv6Info,
    NodePage,
    SSHKeyPair,
)

app = APIRouter(prefix="/api/nodes", tags=["nodes"])
logger = setup_logger(__name__)


@app.get("", response_model=NodePage, operation_id="get_nodes")
def get_api_nodes(
        param: NodeForQuery = Depends(),
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    
    query = db.query(NodeModel)
    if param.name_like:
        query = query.filter(NodeModel.name.like(f'%{param.name_like}%'))
    
    count = query.count()
    query = query.limit(param.limit).offset(int(param.limit * param.page))


    return {"count": count, "data": query.all()}


@app.post("/key", operation_id="update_ssh_key_pair")
def post_ssh_key_pair(
        model: SSHKeyPair,
        current_user: CurrentUser = Depends(get_current_user)
    ):
    makedirs('/root/.ssh/', exist_ok=True)
    
    with open("/root/.ssh/id_rsa", "w") as f:
        f.write(model.private_key.rstrip('\r\n') + '\n')
    with open("/root/.ssh/id_rsa.pub", "w") as f:
        f.write(model.public_key)
    
    chmod('/root/.ssh/', 0o700)
    chmod('/root/.ssh/id_rsa', 0o600)
    chmod('/root/.ssh/id_rsa.pub', 0o600)

    return {}


@app.get("/key", response_model=SSHKeyPair, operation_id="get_ssh_key_pair")
def get_ssh_key_pair(current_user: CurrentUser = Depends(get_current_user)):
    private_key = ""
    public_key = ""
    try: 
        with open("/root/.ssh/id_rsa") as f:
            private_key = f.read()
        with open("/root/.ssh/id_rsa.pub") as f:
            public_key = f.read()
    except FileNotFoundError:
        pass

    return SSHKeyPair(private_key=private_key, public_key=public_key)


@app.get("/{name}", response_model=Node, operation_id="get_node")
def get_api_node(
        name: str,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    node = db.query(NodeModel).filter(NodeModel.name==name).one_or_none()
    if node is None:
        raise HTTPException(status_code=404, detail="node is not found")

    return node


@app.get("/{name}/facts")
def get_node_name_facts(
        name: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

    node = db.query(NodeModel).filter(NodeModel.name == name).one_or_none()
    
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")

    return node.ansible_facts


@app.get("/{name}/network",response_model=List[NodeInterface])
def get_node_name_network(
        name: str,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

    node:NodeModel = db.query(NodeModel).filter(NodeModel.name == name).one_or_none()
    
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    


    ssh_manager = SSHManager(user=node.user_name, domain=node.domain, port=node.port)
    interfaces = ssh_manager.run_cmd_json(["ip", "-j", "a"])

    res = []

    for i in interfaces:
        tmp = NodeInterface(
            ifname = i["ifname"],
            operstate = i["operstate"],
            mtu = i["mtu"],
            master = i["master"] if ("master" in i) else None,
            link_type = i["link_type"],
            mac_address = i["address"] if ("address" in i) else None,
            ipv4_info = [],
            ipv6_info = [],
        )
        for j in i["addr_info"]:
            if j["family"] == "inet6":
                tmp.ipv6_info.append(
                    NodeInterfaceIpv6Info(
                        address=j["local"],
                        prefixlen=j["prefixlen"]
                    )
                )
            if j["family"] == "inet4":
                tmp.ipv6_info.append(
                    NodeInterfaceIpv4Info(
                        address=j["local"],
                        prefixlen=j["prefixlen"],
                        label=j["label"]
                    )
                )
        res.append(tmp)

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