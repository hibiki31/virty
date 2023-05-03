from os import name, chmod, makedirs

from fastapi import APIRouter, Depends, Request
from sqlalchemy import true
from sqlalchemy.orm import Session


from .models import *
from .schemas import *

from auth.router import CurrentUser, get_current_user
from task.models import TaskModel
from task.schemas import TaskSelect
from task.functions import TaskManager
from mixin.database import get_db
from mixin.log import setup_logger
from mixin.exception import *

from node.models import NodeModel


app = APIRouter(prefix="/api")
logger = setup_logger(__name__)


@app.get("/nodes", response_model=List[GetNode], tags=["nodes"])
def get_api_nodes(
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    return db.query(NodeModel).all()


@app.post("/nodes/key", tags=["nodes"])
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


@app.get("/nodes/key", response_model=SSHKeyPair, tags=["nodes"])
def get_ssh_key_pair(current_user: CurrentUser = Depends(get_current_user)):
    private_key = ""
    public_key = ""
    try: 
        with open("/root/.ssh/id_rsa") as f:
            private_key = f.read()
        with open("/root/.ssh/id_rsa.pub") as f:
            public_key = f.read()
    except:
        pass

    return SSHKeyPair(private_key=private_key, public_key=public_key)


@app.post("/tasks/nodes", tags=["tasks-nodes"], response_model=List[TaskSelect])
def post_tasks_nodes(
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db),
        body: NodeInsert = None
    ):
    
    task = TaskManager(db=db)
    task.select(method='post', resource='node', object='root')
    task.commit(user=cu, req=req, body=body)

    if body.libvirt_role:
        body_libvirt = NodeRolePatch(node_name=body.name, role_name="libvirt")
        task_libvirt = TaskManager(db=db)
        task_libvirt.select(method="patch", resource="node", object="role")
        task_libvirt.commit(user=cu, req=req, body=body_libvirt,dep_uuid=task.model.uuid)
        dependence_uuid = task_libvirt.model.uuid

        return [task.model, task_libvirt.model]

    return [task.model]


@app.delete("/tasks/nodes/{name}", tags=["tasks-nodes"], response_model=List[TaskSelect])
def delete_tasks_nodes_name(
        name: str,
        req: Request,
        cu: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    task = TaskManager(db=db)
    task.select(method='delete', resource='node', object='root')
    task.commit(user=cu, req=req, param={"name": name})

    return [task.model]


@app.patch("/tasks/nodes/roles", tags=["tasks-nodes"], response_model=TaskSelect)
def patch_api_node_role(
        request: NodeRolePatch,
        current_user: CurrentUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    task = TaskManager(db=db)
    task.select('patch', 'node', 'role')
    task.commit(user=current_user, request=request)
    
    return task.model


# @app.get("/nodes/pools", tags=["nodes"])
# def get_api_nodes_pools(
#         db: Session = Depends(get_db)
#     ):

#     return db.query(PoolCpu).all()


# @app.post("/nodes/pools", tags=["nodes"])
# def post_api_nodes_pools(
#         model: NodeBase,
#         db: Session = Depends(get_db),
#     ):
#     pool_model = PoolCpu(name=model.name)
#     db.add(pool_model)
#     db.commit()
#     return True


# @app.patch("/nodes/pools", tags=["nodes"])
# def patch_api_nodes_pools(
#         model: PatchNodePool,
#         db: Session = Depends(get_db),
#     ):
#     ass = AssociationPoolsCpu(pool_id=model.pool_id, node_name=model.node_name, core=model.core)
#     db.add(ass)
#     db.commit()
#     return True


# @app.get("/nodes/{node_name}/facts", tags=["nodes"])
# def get_node_name_facts(
#         node_name: str,
#         current_user: CurrentUser = Depends(get_current_user),
#         db: Session = Depends(get_db),
#     ):

#     node = db.query(NodeModel).filter(NodeModel.name == node_name).one_or_none()
    
#     if node == None:
#         raise HTTPException(status_code=404, detail="Node not found")

#     return node.ansible_facts["result"]