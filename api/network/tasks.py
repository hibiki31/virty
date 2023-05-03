from json import loads
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from mixin.log import setup_logger

from .models import *
from .schemas import *
from task.models import TaskModel
from node.models import NodeModel

from mixin.log import setup_logger

from module import virtlib
from module import xmllib
from module.ovslib import OVSManager

from task.functions import TaskBase, TaskRequest

from time import time


worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="put.network.list")
def put_network_list(self: TaskBase, task: TaskModel, reqest: TaskRequest):

    nodes = self.db.query(NodeModel).all()

    token = str(time())

    for node in nodes:
        if node.status != 10:
            continue

        manager = virtlib.VirtManager(node_model=node)

        for network in manager.network_data():
            network:PaseNetwork
            merge_model = NetworkModel(
                uuid = network.uuid,
                name = network.name,
                type = network.type,
                bridge = network.bridge,
                update_token = token,
                node_name = node.name,
            )
            self.db.merge(merge_model)
            for port in network.portgroups:
                port_model = NetworkPortgroupModel(
                    network_uuid = network.uuid, 
                    update_token=token,
                    name=port.name,
                    vlan_id=port.vlan_id,
                    is_default=port.is_default
                )
                self.db.merge(port_model)
            self.db.commit()
        self.db.query(NetworkPortgroupModel).filter(
            NetworkPortgroupModel.network_uuid==network.uuid, 
            NetworkPortgroupModel.update_token!=token
        ).delete()
        self.db.query(NetworkModel).filter(
            NetworkModel.node_name==node.name,
            NetworkModel.update_token!=token
        ).delete()
        
        self.db.commit()
    task.message = "Network list updated has been successfull"


@worker_task(key="post.network.root")
def post_network_root(self: TaskBase, task: TaskModel, request: TaskRequest):
    db = self.db
    body: NetworkInsert = NetworkInsert(**request.body)

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == body.node_name).one()
    except:
        raise Exception("node not found")

    if body.type == "bridge":
        # XMLを定義、設定
        editor = xmllib.XmlEditor("static","net_bridge")
        editor.network_bridge_edit(name=body.name, bridge=body.bridge_device)
        xml = editor.dump_str()
    elif body.type == "ovs":
        xml = f'''
        <network>
            <name>{body.name}</name>
            <forward mode="bridge" />
            <bridge name="{body.bridge_device}" />
            <virtualport type="openvswitch" />
            <portgroup name="untag" default="yes">
            </portgroup>
        </network>
        '''
    else:
        raise Exception("Type is incorrect")

    # ソイや！
    manager = virtlib.VirtManager(node_model=node)
    manager.network_define(xml_str=xml)

    task.message = "Network add has been successfull"


@worker_task(key="delete.network.root")
def delete_network_root(self: TaskBase, task: TaskModel, request: TaskRequest):
    db = self.db
    uuid = request.path_param["uuid"]

    try:
        network: NetworkModel = db.query(NetworkModel).filter(NetworkModel.uuid == uuid).one()
    except:
        raise Exception("network not found")

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == network.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    manager.network_undefine(uuid)    


def post_network_ovs(db:Session, bg: BackgroundTasks, task: TaskModel):
    request: NetworkOVSAdd = NetworkOVSAdd(**loads(task.request))

    try:
        network: NetworkModel = db.query(NetworkModel).filter(NetworkModel.uuid == request.uuid).one()
    except:
        raise Exception("network not found")
    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == network.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    manager.network_ovs_add(uuid=network.uuid, name=request.name, vlan=request.vlan_id)
    

def delete_network_ovs(db:Session, bg: BackgroundTasks, task: TaskModel):
    request: NetworkOVSDelete = NetworkOVSDelete(**loads(task.request))

    try:
        network: NetworkModel = db.query(NetworkModel).filter(NetworkModel.uuid == request.uuid).one()
    except:
        raise Exception("network not found")
    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == network.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    manager.network_ovs_delete(uuid=network.uuid, name=request.name)
    


def post_network_vxlan_internal(db:Session, bg: BackgroundTasks, task: TaskModel):
    request: PostVXLANInternal = PostVXLANInternal(**model.request)

    nodes = db.query(NodeModel).filter(NodeModel.roles.any(role_name="ovs")).all()

    for node in nodes:
        logger.info(node.extra_json)

    # manager = OVSManager(node_model=db.query(NodeModel).first())
    # manager.ovs_crean()
    # manager.ovs_add_br("br-test")
    # manager.ovs_add_vxlan(bridge="br-test", remote="10.254.4.12", key="test")
    return model


