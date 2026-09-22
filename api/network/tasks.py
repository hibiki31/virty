from time import time

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from mixin.log import setup_logger
from module.backends import create_libvirt_backend
from module.virtlib import LibvirtPortNotfound
from network.create import create_network
from node.models import NodeModel
from resource_deletion import (
    ensure_network_deletable,
    ensure_network_port_deletable,
)
from task.functions import TaskBase, TaskRequest
from task.models import TaskModel

from .models import NetworkModel, NetworkPortgroupModel, associations_networks_pools
from .schemas import NetworkForCreate, NetworkOVSForCreate

worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="put.network.list")
def put_network_list(db: Session, model: TaskModel, req: TaskRequest):
    nodes = db.query(NodeModel).all()
    token = str(time())

    for node in nodes:
        if node.status != 10:
            continue

        manager = create_libvirt_backend(node_model=node)

        for network in manager.network_data():
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
                    is_default=port.is_default
                )
                port_model.vlan_id = port.vlan_id
                db.merge(port_model)
            db.commit()
        db.query(NetworkPortgroupModel).filter(
            NetworkPortgroupModel.network.has(NetworkModel.node_name == node.name),
            NetworkPortgroupModel.update_token!=token
        ).delete(synchronize_session=False)
        db.query(NetworkModel).filter(
            NetworkModel.node_name==node.name,
            NetworkModel.update_token!=token
        ).delete()
        
        db.commit()
    model.message = "Network list updated has been successfull"


@worker_task(key="post.network.root")
def post_network_root(db: Session, model: TaskModel, req: TaskRequest):
    body = NetworkForCreate.model_validate(req.body)

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == body.node_name).one()
    except NoResultFound:
        raise Exception("node not found")
    
    create_network(
        body=body,
        node=node
        )

    model.message = "Network add has been successfull"


@worker_task(key="delete.network.root")
def delete_network_root(db: Session, model: TaskModel, req: TaskRequest):
    uuid = req.path_param["uuid"]

    # 受付後にgrantやVM interfaceが変わっていても外部networkを削除しない。
    network = ensure_network_deletable(db, uuid)

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == network.node_name).one()
    except NoResultFound:
        raise Exception("node not found")

    manager = create_libvirt_backend(node_model=node)
    manager.network_undefine(uuid)    


@worker_task(key="post.network.ovs")
def post_network_ovs(db: Session, model: TaskModel, req: TaskRequest):

    body = NetworkOVSForCreate.model_validate(req.body)
    network_uuid = req.path_param["uuid"]

    try:
        network: NetworkModel = db.query(NetworkModel).filter(NetworkModel.uuid == network_uuid).one()
    except NoResultFound:
        raise Exception("network not found")
    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == network.node_name).one()
    except NoResultFound:
        raise Exception("node not found")

    manager = create_libvirt_backend(node_model=node)
    if body.vlan_id is None:
        raise ValueError("vlan_id is required")
    manager.network_ovs_add(uuid=str(network.uuid), name=body.name, vlan=body.vlan_id)
    

@worker_task(key="delete.network.ovs")
def delete_network_ovs(db: Session, model: TaskModel, req: TaskRequest):
    network_uuid = req.path_param["uuid"]
    ovs_name = req.path_param["name"]

    # port単位grantとdefault port利用も管理node操作の直前に再検査する。
    port = ensure_network_port_deletable(db, network_uuid, ovs_name)
    network = port.network
    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == network.node_name).one()
    except NoResultFound:
        raise Exception("node not found")

    manager = create_libvirt_backend(node_model=node)
    try:
        manager.network_ovs_delete(uuid=str(network.uuid), name=ovs_name)
    except LibvirtPortNotfound:
        pass
    
    model.message = "Port is already deleted"
    db.execute(
        associations_networks_pools.delete().where(
            associations_networks_pools.c.port_network_uuid == network_uuid,
            associations_networks_pools.c.port_name == ovs_name,
        )
    )
    db.delete(port)
    db.commit()
