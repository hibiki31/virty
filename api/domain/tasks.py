import os
import re
from time import time

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from mixin.log import setup_logger
from module import cloudinitlib, virtlib, xmllib
from module.ansiblelib import AnsibleManager
from network.models import (
    NetworkModel,
)
from node.models import NodeModel
from storage.models import (
    ImageModel,
    StorageModel,
)
from task.functions import TaskBase
from task.models import TaskModel
from task.schemas import TaskRequest

from .models import DomainDriveModel, DomainInterfaceModel, DomainModel
from .schemas import (
    CdromForUpdateDomain,
    DomainForCreate,
    DomainForCreateDisk,
    DomainForCreateInterface,
    NetworkForUpdateDomain,
    PowerStatusForUpdateDomain,
)

worker_task = TaskBase()
logger = setup_logger(__name__)



@worker_task(key="put.vm.list")
def put_vm_list(db: Session, model: TaskModel, req: TaskRequest):
    nodes:NodeModel = db.query(NodeModel).filter(NodeModel.roles.any(role_name="libvirt"))
    token = str(time())

    for node in nodes:
        if node.status != 10:
            continue
        try:
            manager = virtlib.VirtManager(node_model=node)
        except Exception as e:
            logger.error(f'{e}')
            continue

        domains = manager.domain_data()

        for domain in domains:
            editor = xmllib.XmlEditor("str",domain['xml'])
            editor.dump_file("domain")
            temp = editor.domain_parse()
            
            row = DomainModel(
                uuid = temp.uuid,
                name = re.sub(r'(.*)@.*',r'\1', temp.name),
                core = temp.vcpu,
                memory = temp.memory,
                status = domain['status'],
                node_name = node.name,
                update_token = token,
                vnc_port = temp.vnc_port
            )
            for interface in temp.interface:
                row.interfaces.append(DomainInterfaceModel(**interface.dict(), domain_uuid=temp.uuid))
            
            for disk in temp.disk:
                db_image = db.query(ImageModel).filter(
                    ImageModel.storage.has(StorageModel.node_name==node.name),
                    ImageModel.path==disk.source).one_or_none()
                if db_image is not None:
                    logger.info(db_image)
                    db_image.domain_uuid=temp.uuid
                    db.merge(db_image)
                row.drives.append(DomainDriveModel(domain_uuid=temp.uuid,**disk.dict()))
            db.merge(row)
        # ノードが変わる前に一度コミット
        db.commit()
    db.query(DomainModel).filter(DomainModel.update_token!=str(token)).delete()
    db.commit()
    
    model.message = "VM list updated has been successfull"




@worker_task(key="post.vm.root")
def post_vm_root(db: Session, model: TaskModel, req: TaskRequest):
    req = DomainForCreate.model_validate(req.body)

    if req.type == "ticket":
        Exception("Ticket type is not allowed in this API")

    # データベースから情報とってきて確認も行う
    domains = db.query(DomainModel).filter(DomainModel.name==req.name).all()
    if domains != []:
        raise Exception("domain name is duplicated")
    
    try:
        node = db.query(NodeModel).filter(NodeModel.name==req.node_name).one()
    except NoResultFound:
        raise Exception("node not found")

    ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)

    # XMLのベース読み込んで編集開始
    editor = xmllib.XmlEditor("static","domain_base")

    domain_uuid = editor.domain_uuid_generate()

    editor.domain_emulator_edit(node.os_like)
    editor.domain_base_edit(
        domain_name=f'{req.name}@{model.user_id}#{domain_uuid}',
        memory_mega_byte=req.memory_mega_byte,
        core=req.cpu,
        vnc_port=0,
        vnc_passwd=None
    )
    
    # ネットワークインターフェイス
    for interface in req.interface:
        net = db.query(NetworkModel).filter(
            NetworkModel.uuid==interface.network_uuid
            ).one()

        interface: DomainForCreateInterface
        editor.domain_interface_add(
            network_name=net.name, 
            mac_address=None, 
            port=interface.port
        )

    img_device_names = ["vda","vdb","vdc"]
    
    # ブロックデバイス
    for device, device_name in zip(req.disks, img_device_names):
        device: DomainForCreateDisk

        try:
            new_pool = db.query(StorageModel).filter(
                StorageModel.uuid==device.save_pool_uuid
                ).one()
        except NoResultFound:
            raise Exception("request storage pool uuid not found")

        create_image_path = f'{new_pool.path}/{model.user_id}_{req.name}_{device_name}_{domain_uuid}.img'
        editor.domain_device_image_add(image_path=create_image_path, target_device=device_name)


        if device.type == "empty":
            ex_vars = {"path": create_image_path,  "size": f"{device.size_giga_byte}G"}
            ansible_manager.run(playbook_name="vms/qemu_image_create", extravars=ex_vars)

        elif device.type == "copy":
            try:
                pool_model:StorageModel = db.query(StorageModel).filter(StorageModel.uuid==device.original_pool_uuid).one()
            except NoResultFound:
                raise Exception("request src pool uuid not found")

            from_image_path = os.path.join(pool_model.path, device.original_name)
            
            ex_vars = {
                "src": from_image_path,
                "dst": create_image_path,
            }
            ansible_manager.run(playbook_name="commom/copy_node_internal", extravars=ex_vars)
            
            logger.info(f'{create_image_path}のサイズを変更します')
            ex_vars = {"path": create_image_path,  "size": f"{device.size_giga_byte}G"}
            ansible_manager.run(playbook_name="vms/qemu_image_resize", extravars=ex_vars)

    # Cloud-init
    if req.cloud_init is not None:
        # iso作成
        cloudinit_manager = cloudinitlib.CloudInitManager(domain_uuid,req.cloud_init.hostname)
        cloudinit_manager.custom_user_data(req.cloud_init.userData)
        iso_path = cloudinit_manager.make_iso()

        # cloud-initのisoを保存するpoolを探してたけどやめた
        # try:
        #     query = db.query(StorageModel).join(NodeModel).outerjoin(StorageMetadataModel)
        #     query = query.filter(NodeModel.name==node.name).filter(StorageMetadataModel.rool=="init-iso")
        #     init_pool_model:StorageModel = query.one()
        # except:
        #     raise Exception("cloud-init pool not found")
        # send_path = f"{init_pool_model.path}/{domain_uuid}.iso"
        
        # /var/virtyで固定
        send_path = f"/var/virty/cloud-init/{domain_uuid}.iso"

        ansible_manager.run(playbook_name="commom/make_dir_recurse",extravars={"path":"/var/virty/cloud-init/"})
        ansible_manager.run(
            playbook_name="commom/copy_virty_to_node",
            extravars={
                "src": iso_path,
                "dst":send_path
        })
        editor.domain_cdrom(target=None,path=send_path)


    # ノードに接続してlibvirtでXMLを登録
    node = virtlib.VirtManager(node_model=node)
    node.domain_define(xml_str=editor.dump_str())

    model.message = f"Virtual machine ({req.name}@{model.user_id}) has been added successfully"
    logger.info('task終了')


@worker_task(key="delete.vm.root")
def delete_vm_root(db: Session, model: TaskModel, req: TaskRequest):
    uuid = req.path_param["uuid"]

    domain, node = get_domain(db=db, uuid=uuid)

    manager = virtlib.VirtManager(node_model=node)
    manager.domain_destroy(uuid=uuid)
    manager.domain_undefine(uuid)
    
    db.delete(domain)

    model.message = f"{domain.name} virtual machine has been deleted successfully"


@worker_task(key="patch.vm.power")
def patch_vm_root(db: Session, model: TaskModel, req: TaskRequest):
    uuid = req.path_param["uuid"]
    body = PowerStatusForUpdateDomain.model_validate(req.body)

    domain, node = get_domain(db=db, uuid=uuid)

    manager = virtlib.VirtManager(node_model=node)

    # 電源
    if body.status == "on":
        manager.domain_poweron(uuid=uuid)
    elif body.status == "off":
        manager.domain_destroy(uuid=uuid)
        
    model.message = f"{domain.name} virtual machine has been {body.status}"


@worker_task(key="patch.vm.cdrom")
def patch_vm_cdrom(db: Session, model: TaskModel, req: TaskRequest):
    uuid = req.path_param["uuid"]
    body = CdromForUpdateDomain.model_validate(req.body)

    domain, node = get_domain(db=db, uuid=uuid)

    manager = virtlib.VirtManager(node_model=node)

    if body.path is None or body.path == "":
        manager.domain_cdrom(uuid, body.target)
    else:
        manager.domain_cdrom(uuid, body.target, body.path)


@worker_task(key="patch.vm.network")
def patch_vm_network(db: Session, model: TaskModel, req: TaskRequest):
    body = NetworkForUpdateDomain.model_validate(req.body)
    uuid = req.path_param["uuid"]

    domain, node = get_domain(db=db, uuid=uuid)

    try:
        network = db.query(NetworkModel).filter(NetworkModel.uuid == body.network_uuid).one()
    except NoResultFound:
        raise Exception("Network uuid is not found")
    
    manager = virtlib.VirtManager(node_model=node)
    manager.domain_network(uuid=uuid, network=network.name, port=body.port, mac=body.mac)
    
    
def get_domain(db: Session, uuid):
    try:
        domain: DomainModel = db.query(DomainModel).filter(DomainModel.uuid == uuid).one()
    except NoResultFound:
        raise Exception(f"VM({uuid}) not found")

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == domain.node_name).one()
    except NoResultFound:
        raise Exception(f"Node({domain.node_name}) not found")
    
    return domain, node