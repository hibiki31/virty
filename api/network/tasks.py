from ipaddress import ip_interface
from random import randint
from time import time

import httpx
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from mixin.log import setup_logger
from module import virtlib, xmllib
from network.create import create_network
from node.models import NodeModel
from task.functions import TaskBase, TaskRequest
from task.models import TaskModel

from .models import NetworkModel, NetworkPortgroupModel
from .schemas import (
    NetworkForCreate,
    NetworkOVSForCreate,
    NetworkProviderForCreate,
    PostVXLANInternal,
)

worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="put.network.list")
def put_network_list(db: Session, model: TaskModel, req: TaskRequest):
    nodes = db.query(NodeModel).all()
    token = str(time())

    for node in nodes:
        if node.status != 10:
            continue

        manager = virtlib.VirtManager(node_model=node)

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

    try:
        network: NetworkModel = db.query(NetworkModel).filter(NetworkModel.uuid == uuid).one()
    except NoResultFound:
        raise Exception("network not found")

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == network.node_name).one()
    except NoResultFound:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
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

    manager = virtlib.VirtManager(node_model=node)
    manager.network_ovs_add(uuid=network.uuid, name=body.name, vlan=body.vlan_id)
    

@worker_task(key="delete.network.ovs")
def delete_network_ovs(db: Session, model: TaskModel, req: TaskRequest):
    network_uuid = req.path_param["uuid"]
    ovs_name = req.path_param["name"]

    try:
        network = db.query(NetworkModel).filter(NetworkModel.uuid == network_uuid).one()
        port = db.query(
            NetworkPortgroupModel).filter(
            NetworkPortgroupModel.network_uuid==network_uuid
            ).filter(NetworkPortgroupModel.name==ovs_name).one()
    except NoResultFound:
        raise Exception("network not found")
    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == network.node_name).one()
    except NoResultFound:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    try:
        manager.network_ovs_delete(uuid=network.uuid, name=ovs_name)
    except virtlib.LibvirtPortNotfound:
        pass
    
    model.message = "Port is already deleted"
    db.delete(port)
    db.commit()
    

@worker_task(key="post.network.vxlan")
def post_network_vxlan_internal(db: Session, model: TaskModel, req: TaskRequest):
    body = PostVXLANInternal.model_validate(req.body)

    nodes = db.query(NodeModel).filter(NodeModel.roles.any(role_name="ovs")).all()

    for node in nodes:
        logger.info(node.extra_json)

    # manager = OVSManager(node_model=db.query(NodeModel).first())
    # manager.ovs_crean()
    # manager.ovs_add_br("br-test")
    # manager.ovs_add_vxlan(bridge="br-test", remote="10.254.4.12", key="test")
    return model


@worker_task(key="post.network.provider")
def post_network_provider(db: Session, model: TaskModel, req: TaskRequest):
    body = NetworkProviderForCreate.model_validate(req)
    
    vni = randint(1,2**24)
    # VNIの16新数ゼロ梅
    # 4桁:接頭辞 vbr-
    # 6桁:VNI 24bit
    # 4桁:ノード識別子 AXYZ
    net_id = str('{:06x}'.format(vni))
    gw_ip = ip_interface(f"{body.gateway_address}/{body.network_prefix}")

    # Network Node
    network_node:NodeModel = db.query(NodeModel).filter(NodeModel.name==body.network_node).one()
    editor = xmllib.XmlEditor("static","net_provider")
    editor.network_provider(
        name=f'vbr-{net_id}', bridge=f'vbr-{net_id}',
        address=str(gw_ip.ip),
        netmask=str(gw_ip.netmask),
        domain=str(body.dns_domain),
        start=body.dhcp_start,
        end=body.dhcp_end
        )
    xml = editor.dump_str()
   
    # ソイや！
    manager = virtlib.VirtManager(node_model=network_node)
    manager.network_define(xml_str=xml)

    
    nodes = db.query(NodeModel).filter(NodeModel.roles.any(role_name="vxlan_overlay")).order_by(NodeModel.name).all()

    find_role = lambda i: [ j for j in i if j.role_name=="vxlan_overlay"][0]

    # Network node to Worker node
    counter = 0
    for node in nodes:
        if node.name == body.network_node:
            continue
        node: NodeModel
        node_extra = find_role(node.roles).extra_json

        req_data = {
            "vni": vni,
            "node_id": counter,
            "remote_ip": node_extra['local_ip']
        }
        resp = httpx.post(url=f'http://{network_node.domain}:8766/vxlan', json=req_data)
        logger.info(resp)
        counter += 1

    # Worker node to Network node
    for node in nodes:
        if node.name == body.network_node:
            continue
        editor = xmllib.XmlEditor("static","net_internal")
        editor.network_internal(name=f'vbr-{net_id}')
        xml = editor.dump_str()
    
        manager = virtlib.VirtManager(node_model=node)
        manager.network_define(xml_str=xml)
        req_data = {
            "vni": vni,
            "node_id": 0,
            "remote_ip": node_extra['network_node_ip']
        }
        resp = httpx.post(url=f'http://{node.domain}:8766/vxlan', json=req_data)
        logger.info(resp)