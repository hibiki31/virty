from sqlalchemy.orm import Session

from mixin.log import setup_logger
from task.functions import TaskBase, TaskRequest
from task.models import TaskModel
from user.models import UserModel

from .models import ProjectModel
from .schemas import ProjectForCreate

worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="post.project.root")
def post_project_root(db: Session, model: TaskModel, req: TaskRequest):

    body = ProjectForCreate.model_validate(req.body)
    user_ids = set(body.user_ids)
    if model.user_id is None:
        raise ValueError("taskの実行userが見つかりません")
    user_ids.add(model.user_id)
    users = db.query(UserModel).filter(UserModel.username.in_(user_ids)).all()
    if {user.username for user in users} != user_ids:
        raise ValueError("指定されたユーザーが見つかりません")

    project = ProjectModel(name=body.project_name)
    project.users = users
    db.add(project)
    db.commit()
    
    # nodes = db.query(NodeModel).filter(NodeModel.roles.any(role_name="ovs")).all()

    # node_list = []

    # for node in nodes:
    #     for role in node.roles:
    #         if role.role_name == "ovs":
    #             node_list.append({"node": node.domain, "local": role.extra_json["localIp"]})
    
    # logger.info(node_list)

    # bridge_name = f"vy-{project.id}"

    # for node in node_list:
    #     ovs_mg = OVSManager(domain=node["node"])
    #     # mg.ovs_crean()
    #     ovs_mg.ovs_add_br(f'{bridge_name}')
    #     for remote in node_list:
    #         if node["local"] == remote["local"]:
    #             continue
    #         ovs_mg.ovs_add_vxlan(bridge=bridge_name, remote=remote["local"], key=int(project.id,16))

    # for node in nodes:
    #     request_network = NetworkForCreate(name=bridge_name, node_name=node.name,type="ovs", bridge_device=bridge_name)
    #     net_add = TaskManager(db=db, bg=bg)
    #     net_add.select('post', 'network', 'root')
    #     net_add.folk(task=task, dependence_uuid=None, request=request_network)


@worker_task(key="delete.project.root")
def delete_project_root(db: Session, model: TaskModel, req: TaskRequest):
    project_id = req.path_param["project_id"]

    
    db.query(ProjectModel).filter(ProjectModel.id==project_id).delete()
    # project.users = []
    
    # bridge_name = f"vy-{project.id}"

    # for node in db.query(NodeModel).filter(NodeModel.roles.any(role_name="ovs")).all():
    #     ovs_mg = OVSManager(domain=node.domain)
    #     ovs_mg.ovs_del_br(bridge=bridge_name)
    
    # for net in db.query(NetworkModel).filter(NetworkModel.name==bridge_name):
    #     net_delete_req = NetworkForDelete(uuid=net.uuid)
    #     net_delete = TaskManager(db=db, bg=bg)
    #     net_delete.select('delete', 'network', 'root')
    #     net_delete.folk(task=task, dependence_uuid=None, request=net_delete_req)

    # db.delete(project)
    db.commit()
    
    model.message = "Project has been deleted successfully"
