import re
from time import time

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from mixin.log import setup_logger
from module import cloudinitlib, xmllib
from module.backends import create_ansible_backend, create_libvirt_backend
from network.models import (
    NetworkModel,
)
from node.models import NodeModel
from storage.models import (
    ImageModel,
    StorageModel,
)
from task.functions import TaskBase, is_agent_task
from task.models import TaskModel
from task.schemas import TaskRequest

from .models import DomainDriveModel, DomainInterfaceModel, DomainModel
from .schemas import (
    CdromForUpdateDomain,
    DomainForCreate,
    NetworkForUpdateDomain,
    PowerStatusForUpdateDomain,
)

worker_task = TaskBase()
logger = setup_logger(__name__)



@worker_task(key="put.vm.list")
def put_vm_list(db: Session, model: TaskModel, req: TaskRequest):
    nodes = db.query(NodeModel).filter(NodeModel.roles.any(role_name="libvirt"))
    token = str(time())

    for node in nodes:
        if node.status != 10:
            continue
        try:
            manager = create_libvirt_backend(node_model=node)
        except Exception as e:
            logger.error(f'{e}')
            continue

        domains = manager.domain_data()

        for domain in domains:
            safe_xml = xmllib.redact_domain_xml_secrets(domain['xml'])
            editor = xmllib.XmlEditor("str", safe_xml)
            editor.dump_file("domain")
            temp = editor.domain_parse()
            existing = (
                db.query(DomainModel)
                .filter(DomainModel.uuid == temp.uuid)
                .one_or_none()
            )
            
            row = DomainModel(
                uuid=temp.uuid,
                name=re.sub(r"(.*)@.*", r"\1", temp.name),
                core=temp.vcpu,
                memory=temp.memory,
                status=domain["status"],
                node_name=node.name,
                update_token=token,
            )
            row.vnc_port = (
                str(temp.vnc_port) if temp.vnc_port is not None else None
            )
            row.description = existing.description if existing is not None else None
            row.owner_user_id = (
                existing.owner_user_id if existing is not None else None
            )
            row.owner_project_id = (
                existing.owner_project_id if existing is not None else None
            )
            for interface in temp.interface:
                row.interfaces.append(
                    DomainInterfaceModel(
                        **interface.model_dump(),
                        domain_uuid=temp.uuid,
                    )
                )
            
            for disk in temp.disk:
                db_image = db.query(ImageModel).filter(
                    ImageModel.storage.has(StorageModel.node_name==node.name),
                    ImageModel.path==disk.source).one_or_none()
                if db_image is not None:
                    db_image.domain_uuid=temp.uuid
                    db.merge(db_image)
                row.drives.append(
                    DomainDriveModel(
                        domain_uuid=temp.uuid,
                        **disk.model_dump(),
                    )
                )
            db.merge(row)
        # ノードが変わる前に一度コミット
        db.commit()
    db.query(DomainModel).filter(DomainModel.update_token!=str(token)).delete()
    db.commit()
    
    model.message = "VM list updated has been successfull"




@worker_task(key="post.vm.root")
def post_vm_root(db: Session, model: TaskModel, req: TaskRequest):
    body: DomainForCreate
    if is_agent_task(model):
        from agent.input_models import AgentDomainForCreate

        body = AgentDomainForCreate.model_validate(req.body)
    else:
        body = DomainForCreate.model_validate(req.body)

    if body.type != "manual":
        raise ValueError("このendpointではmanual作成だけを利用できます")

    owner_project_id = getattr(body, "project_id", None)
    if is_agent_task(model):
        from project.models import ProjectModel

        if db.get(ProjectModel, owner_project_id) is None:
            raise ValueError("VM owner projectがありません")

    # データベースから情報とってきて確認も行う
    domains = db.query(DomainModel).filter(DomainModel.name==body.name).all()
    if domains != []:
        raise Exception("domain name is duplicated")
    
    try:
        node = db.query(NodeModel).filter(NodeModel.name==body.node_name).one()
    except NoResultFound:
        raise Exception("node not found")

    ansible_manager = create_ansible_backend(user=node.user_name, domain=node.domain)

    # XMLのベース読み込んで編集開始
    editor = xmllib.XmlEditor("static","domain_base")

    domain_uuid = editor.domain_uuid_generate()

    editor.domain_emulator_edit(node.os_like)
    editor.domain_base_edit(
        domain_name=f'{body.name}@{model.user_id}#{domain_uuid}',
        memory_mega_byte=body.memory_mega_byte,
        core=body.cpu,
        vnc_port=0,
    )
    
    # ネットワークインターフェイス
    for interface_model in body.interface:
        net = db.query(NetworkModel).filter(
            NetworkModel.uuid==interface_model.network_uuid
            ).one()
        if net.node_name != node.name:
            raise Exception("request network belongs to another node")

        editor.domain_interface_add(
            network_name=str(net.name),
            mac_address=None, 
            port=interface_model.port
        )

    img_device_names = ["vda","vdb","vdc"]
    
    # ブロックデバイス
    for device_model, device_name in zip(body.disks, img_device_names):
        try:
            new_pool = db.query(StorageModel).filter(
                StorageModel.uuid==device_model.save_pool_uuid
                ).one()
        except NoResultFound:
            raise Exception("request storage pool uuid not found")
        if new_pool.node_name != node.name:
            raise Exception("request destination storage belongs to another node")

        create_image_path = f'{new_pool.path}/{model.user_id}_{body.name}_{device_name}_{domain_uuid}.img'
        editor.domain_device_image_add(image_path=create_image_path, target_device=device_name)


        if device_model.type == "empty":
            ex_vars = {"path": create_image_path,  "size": f"{device_model.size_giga_byte}G"}
            ansible_manager.run(playbook_name="vms/qemu_image_create", extravars=ex_vars)

        elif device_model.type == "copy":
            if device_model.original_name is None:
                raise ValueError("copy diskにはoriginal_nameが必要です")
            try:
                source_image = db.query(ImageModel).filter(
                    ImageModel.storage_uuid == device_model.original_pool_uuid,
                    ImageModel.name == device_model.original_name,
                ).one()
            except NoResultFound:
                raise Exception("request source image not found")
            if source_image.storage.node_name != node.name:
                raise Exception("request source image belongs to another node")

            from_image_path = source_image.path
            
            ex_vars = {
                "src": from_image_path,
                "dst": create_image_path,
            }
            ansible_manager.run(playbook_name="commom/copy_node_internal", extravars=ex_vars)
            
            logger.info(f'{create_image_path}のサイズを変更します')
            ex_vars = {"path": create_image_path,  "size": f"{device_model.size_giga_byte}G"}
            ansible_manager.run(playbook_name="vms/qemu_image_resize", extravars=ex_vars)

    # Cloud-init
    if body.cloud_init is not None:
        cloudinit_manager = cloudinitlib.CloudInitManager(domain_uuid,body.cloud_init.hostname)
        try:
            cloudinit_manager.custom_user_data(body.cloud_init.userData)
            iso_path = cloudinit_manager.make_iso()

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
        finally:
            cloudinit_manager.cleanup()


    # ノードに接続してlibvirtでXMLを登録
    libvirt_backend = create_libvirt_backend(node_model=node)
    libvirt_backend.domain_define(xml_str=editor.dump_str())

    # 後続inventory refreshでも所有者を失わないよう、定義直後にmetadataを残す。
    created_domain = DomainModel(
        uuid=domain_uuid,
        name=body.name,
        core=body.cpu,
        memory=body.memory_mega_byte,
        status=5,
        node_name=body.node_name,
    )
    created_domain.owner_user_id = model.user_id
    created_domain.owner_project_id = owner_project_id
    created_domain.vnc_port = "0"
    db.merge(created_domain)

    model.message = f"Virtual machine ({body.name}@{model.user_id}) has been added successfully"


@worker_task(key="delete.vm.root")
def delete_vm_root(db: Session, model: TaskModel, req: TaskRequest):
    uuid = req.path_param["uuid"]

    domain, node = get_domain(db=db, uuid=uuid)

    manager = create_libvirt_backend(node_model=node)
    manager.domain_destroy(uuid=uuid)
    manager.domain_undefine(uuid)
    
    db.delete(domain)

    model.message = f"{domain.name} virtual machine has been deleted successfully"


@worker_task(key="patch.vm.power")
def patch_vm_root(db: Session, model: TaskModel, req: TaskRequest):
    uuid = req.path_param["uuid"]
    body = PowerStatusForUpdateDomain.model_validate(req.body)

    domain, node = get_domain(db=db, uuid=uuid)

    manager = create_libvirt_backend(node_model=node)

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

    manager = create_libvirt_backend(node_model=node)

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
    
    manager = create_libvirt_backend(node_model=node)
    manager.domain_network(uuid=uuid, network=str(network.name), port=body.port, mac=body.mac)
    
    
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
