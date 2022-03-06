from os import name
from sqlalchemy.orm import Session

from .models import *
from .schemas import *

from task.models import TaskModel
from node.models import NodeModel
from mixin.log import setup_logger

from module import virtlib
from module import xmllib

from time import time


logger = setup_logger(__name__)


def update_network_list(db: Session, model: TaskModel):
    nodes = db.query(NodeModel).all()

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
            db.merge(merge_model)
            for port in network.portgroups:
                port_model = NetworkPortgroupModel(
                    network_uuid = network.uuid, 
                    update_token=token,
                    name=port.name,
                    vlan_id=port.vlan_id,
                    is_default=port.is_default
                )
                db.merge(port_model)
            db.commit()
        db.query(NetworkPortgroupModel).filter(
            NetworkPortgroupModel.network_uuid==network.uuid, 
            NetworkPortgroupModel.update_token!=token
        ).delete()
        db.query(NetworkModel).filter(
            NetworkModel.node_name==node.name,
            NetworkModel.update_token!=token
        ).delete()
        
        db.commit()
    return model

def add_network_base(db: Session, model: TaskModel):
    request: NetworkInsert = NetworkInsert(**model.request)

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == request.node_name).one()
    except:
        raise Exception("node not found")

    if request.type == "bridge":
        # XMLを定義、設定
        editor = xmllib.XmlEditor("static","net_bridge")
        editor.network_bridge_edit(name=request.name, bridge=request.bridge_device)
        xml = editor.dump_str()
    elif request.type == "ovs":
        xml = f'''
        <network>
            <name>{request.name}</name>
            <forward mode="bridge" />
            <bridge name="{request.bridge_device}" />
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

    update_network_list(db=db, model=TaskModel())

    return model

def delete_network_base(db: Session, model: TaskModel):
    request: NetworkDelete = NetworkDelete(**model.request)

    try:
        network: NetworkModel = db.query(NetworkModel).filter(NetworkModel.uuid == request.uuid).one()
    except:
        raise Exception("network not found")

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == network.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    manager.network_undefine(request.uuid)

    update_network_list(db=db, model=TaskModel())

    return model

def add_network_ovs(db: Session, model: TaskModel):
    request: NetworkOVSAdd = NetworkOVSAdd(**model.request)

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

    return model

def delete_network_ovs(db: Session, model: TaskModel):
    request: NetworkOVSDelete = NetworkOVSDelete(**model.request)

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

    return model