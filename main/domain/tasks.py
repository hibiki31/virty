from sqlalchemy.orm import Session
from time import time

from .models import *
from .schemas import *

from task.models import TaskModel
from node.models import NodeModel
from storage.models import StorageModel
from mixin.log import setup_logger

from module import virtlib
from module import xmllib
from module import sshlib


logger = setup_logger(__name__)


def update_domain_list(db: Session, model: TaskModel):
    nodes:NodeModel = db.query(NodeModel).all()
    token = time()

    for node in nodes:
        if node.status != 10:
            continue
        logger.info(f'ノードへ接続します: {node.user_name + "@" + node.domain}')
        try:
            manager = virtlib.VirtManager(node_model=node)
        except Exception as e:
            logger.error(f'{e}')
            continue

        domains = manager.domain_data()

        logger.info("ドメイン数：" + str(len(domains)))

        for domain in domains:
            editor = xmllib.XmlEditor("str",domain['xml'])
            editor.dump_file("domain")
            temp = editor.domain_parse()
            
            row = DomainModel(
                uuid = temp["uuid"],
                name = temp['name'],
                core = temp['vcpu'],
                memory = temp['memory'],
                status = domain['status'],
                node_name = node.name,
                update_token = token
            )
            db.merge(row)
        # ノードが変わる前に一度コミット
        db.commit()
    db.query(DomainModel).filter(DomainModel.update_token!=token).delete()
    db.commit()
    return model


def add_domain_base(db: Session, model: TaskModel):
    task_model:TaskModel = model
    model: DomainInsert = DomainInsert(**task_model.request)

    domains: DomainModel = db.query(DomainModel).filter(DomainModel.name==model.name).all()

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name==model.node_name).one()
    except:
        raise Exception("node not found")
    
    if domains != []:
        raise Exception("domain name is duplicated")

    manager = virtlib.VirtManager(node_model=node)
    editor = xmllib.XmlEditor("static","domain_base")

    editor.domain_emulator_edit(node.os_like)
    editor.domain_base_edit(
        domain_name=model.name,
        memory_mega_byte=model.memory_mega_byte,
        core=model.cpu,
        vnc_port=0,
        vnc_passwd=None
    )
    
    # ネットワークインターフェイス
    for interface in model.interface:
        interface: DomainInsertInterface
        editor.domain_interface_add(network_name=interface.network_name, mac_address=None)

    img_device_names = ["vda","vdb","vdc"]
    
    # ブロックデバイス
    for device, device_name in zip(model.disks, img_device_names):
        # 型定義
        device: DomainInsertDisk
        # 作成先のプールを参照
        try:
            new_pool: StorageModel = db.query(StorageModel).filter(StorageModel.uuid==device.save_pool_uuid).one()
        except:
            raise Exception("request pool uuid not found")
        # ファイル名決めてる
        create_image_path = new_pool.path +"/"+ model.name + "_" + device_name + '.img'
        # XMLに追加
        editor.domain_device_image_add(image_path=create_image_path, target_device=device_name)

        # 新規ディスクの場合
        if device.type == "empty":
            # 空のディスク作成
            ssh_manager = sshlib.SSHManager(user=node.user_name, domain=node.domain)
            ssh_manager.qemu_create(
                size_giga_byte=device.size_giga_byte,
                path=create_image_path
            )
        # 既存ディスクのコピー
        elif device.type == "copy":
            # コピー元のプール情報参照
            try:
                pool_model:StorageModel = db.query(StorageModel).filter(StorageModel.uuid==device.original_pool_uuid).one()
            except:
                raise Exception("request src pool uuid not found")
            pool_path = pool_model.path
            file_name = device.original_name
            from_image_path = pool_path + '/' + file_name

            logger.info(f'{from_image_path}を{create_image_path}へコピーします')
            ssh_manager = sshlib.SSHManager(user=node.user_name, domain=node.domain)
            ssh_manager.file_copy(
                from_path=from_image_path,
                to_path=create_image_path
            )

    # libvirtでXMLを登録
    manager.domain_define(xml_str=editor.dump_str())

    return task_model


def delete_domain_base(db: Session, model: TaskModel):
    request: DomainInsert = DomainDelete(**model.request)

    try:
        domain: DomainModel = db.query(DomainModel).filter(DomainModel.uuid == request.uuid).one()
    except:
        raise Exception("domain not found")

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == domain.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    manager.domain_undefine(request.uuid)

    update_domain_list(db=db, model=TaskModel())

    return model


def change_domain_base(db: Session, model: TaskModel):
    request: DomainPatch = DomainPatch(**model.request)

    try:
        domain: DomainModel = db.query(DomainModel).filter(DomainModel.uuid == request.uuid).one()
    except:
        raise Exception("domain not found")

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == domain.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)

    # 電源
    if request.status == "on":
        manager.domain_poweron(uuid=request.uuid)
    elif request.status == "off":
        manager.domain_destroy(uuid=request.uuid)
    
    # CDROM 
    if request.status == "mount":
        manager.domain_cdrom(request.uuid, request.target, request.path)
    elif request.status == "unmount":
        manager.domain_cdrom(request.uuid, request.target)

    update_domain_list(db=db, model=TaskModel())

    return model

def change_domain_network(db: Session, model: TaskModel):
    request: DomainNetworkChange = DomainNetworkChange(**model.request)

    try:
        domain: DomainModel = db.query(DomainModel).filter(DomainModel.uuid == request.uuid).one()
    except:
        raise Exception("domain not found")

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == domain.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    
    # CDROM 
    if request.status == "mount":
        manager.domain_cdrom(request.uuid, request.target, request.path)
    elif request.status == "unmount":
        manager.domain_cdrom(request.uuid, request.target)

    update_domain_list(db=db, model=TaskModel())

    return model