from email.mime import base
from json import loads
from sqlalchemy.orm import Session
from mixin.log import setup_logger

from .models import *
from .schemas import *
from task.models import TaskModel

import re
from time import time
from sqlalchemy import func, nullsfirst
from sqlalchemy.orm import Session

from task.functions import TaskManager
from network.models import NetworkModel, NetworkPoolModel, NetworkPortgroupModel, associations_networks, associations_networks_pools
from node.models import NodeModel
from storage.models import AssociationStoragePool, StorageModel, ImageModel, StorageMetadataModel, StoragePoolModel

from module import virtlib
from module import xmllib
from module import sshlib
from module import cloudinitlib
from module.ansiblelib import AnsibleManager

from task.functions import TaskBase
from task.schemas import TaskRequest


worker_task = TaskBase()
logger = setup_logger(__name__)



@worker_task(key="put.vm.list")
def put_vm_list(self: TaskBase, task: TaskModel, reqests: TaskRequest):
    nodes:NodeModel = self.db.query(NodeModel).filter(NodeModel.roles.any(role_name="libvirt"))
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
                db_image = self.db.query(ImageModel).filter(
                    ImageModel.storage.has(StorageModel.node_name==node.name),
                    ImageModel.path==disk.source).one_or_none()
                if db_image != None:
                    db_image.domain_uuid=temp.uuid
                row.drives.append(DomainDriveModel(domain_uuid=temp.uuid,**disk.dict()))
            self.db.merge(row)
        # ノードが変わる前に一度コミット
        self.db.commit()
    self.db.query(DomainModel).filter(DomainModel.update_token!=str(token)).delete()
    self.db.commit()

    task.message = "VM list updated has been successfull"


def post_vm_ticketd(db:Session, task: TaskModel):
    req = PostDomainTicket(**loads(task.request))
    issuance_model = db.query(IssuanceModel).filter(IssuanceModel.id==req.issuance_id).one()

    # メモリのアサインが少ない順で行く
    nodes = db.query(
        NodeModel.name.label('node_name'),
        func.sum(DomainModel.memory).label('memory'),
    ).outerjoin(DomainModel).group_by(NodeModel.name).order_by(
        nullsfirst(func.sum(DomainModel.memory).asc())
    ).all()
    
    found_node = False

    for node in nodes:
        logger.debug(f'{node.node_name} commit memory: {node.memory}')

        flavor_image_model = db.query(ImageModel).filter(
            ImageModel.flavor_id==req.flavor_id,
            StorageModel.node_name==node.node_name
        ).outerjoin(StorageModel).first()
        # flavorがnodeにないため次へ
        if flavor_image_model == None:
            logger.debug(f'{node.node_name} not found flavor {req.flavor_id}')
            continue

        logger.debug(f'{node.node_name} has flavor {req.flavor_id}')

        storage_pool = db.query(StorageModel).filter(
            StoragePoolModel.id==req.storage_pool_id,
            StorageModel.node_name==node.node_name
        ).outerjoin(
            AssociationStoragePool
        ).outerjoin(
            StoragePoolModel
        ).first()

        if storage_pool == None:
            logger.debug(f'{node.node_name} not found {storage_pool.name} in pool {req.storage_pool_id}')
            continue
        
        logger.debug(f'{node.node_name} has {storage_pool.name} in pool {req.storage_pool_id}')

        network_models = {}
        network_notfound_flag = False

        for net_pool_id in req.interfaces:
            network_model = db.query(NetworkModel).filter(
                NetworkPoolModel.id==net_pool_id.id,
                NetworkModel.node_name==node.node_name
            ).outerjoin(
                associations_networks
            ).outerjoin(
                NetworkPoolModel
            ).first()

            port_model = db.query(NetworkPortgroupModel).filter(
                NetworkPoolModel.id==net_pool_id.id,
                NetworkPortgroupModel.network.has(node_name=node.node_name)
            ).outerjoin(
                associations_networks_pools
            ).outerjoin(
                NetworkPoolModel
            ).first()

            if network_model != None:
                logger.debug(f'{node.node_name} has {network_model.name} in pool {net_pool_id.id}')
                network_models[net_pool_id.id] = network_model
            elif port_model != None:
                logger.debug(f'{node.node_name} has {port_model.network.name} port {port_model.name} in pool {net_pool_id.id}')
                network_models[net_pool_id.id] = port_model           
            else:
                network_notfound_flag = True
                logger.debug(f'{node.node_name} not found {net_pool_id.id}')
                break 
        if network_notfound_flag:
            continue

        logger.debug(network_models)

        logger.info(f'{node.node_name} is scheduling pass !! ')

        ## 情報がそろった

        disk = DomainInsertDisk(
            type="copy",
            save_pool_uuid=storage_pool.uuid,
            original_pool_uuid=flavor_image_model.storage_uuid,
            original_name=flavor_image_model.name,
            size_giga_byte=req.flavor_size_g
        )

        interfaces = []

        for i in req.interfaces:
            if  isinstance(network_models[i.id], NetworkModel):
                interfaces.append(DomainInsertInterface(
                type="network",
                mac=i.mac,
                network_name=network_models[i.id].name,
                port=None
                ))
            elif isinstance(network_models[i.id], NetworkPortgroupModel):
                interfaces.append(DomainInsertInterface(
                type="network",
                mac=i.mac,
                network_name=network_models[i.id].network.name,
                port=network_models[i.id].name
                ))
            else:
                raise Exception("Network class not found")

        res = DomainInsert(
            type="ticket",
            name=req.name,
            node_name=node.node_name,
            memory_mega_byte=req.memory,
            cpu=req.core,
            disks=[disk],
            interface=interfaces,
            cloud_init=req.cloud_init
        )
        return res

    raise Exception("avalilabel node not found")


@worker_task(key="post.vm.root")
def post_vm_root(self: TaskBase, task: TaskModel, request: TaskRequest):

    db = self.db
    if request.body["type"] == "ticket":
        req = post_vm_ticketd(db=db, task=task)
    else:
        req = DomainInsert(**request.body)

    # データベースから情報とってきて確認も行う
    domains: DomainModel = db.query(DomainModel).filter(DomainModel.name==req.name).all()
    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name==req.node_name).one()
    except:
        raise Exception("node not found")

    if domains != []:
        raise Exception("domain name is duplicated")

    ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)

    # XMLのベース読み込んで編集開始
    editor = xmllib.XmlEditor("static","domain_base")

    editor.domain_emulator_edit(node.os_like)
    editor.domain_base_edit(
        domain_name=f'{req.name}@{task.user_id}',
        memory_mega_byte=req.memory_mega_byte,
        core=req.cpu,
        vnc_port=0,
        vnc_passwd=None
    )

    domain_uuid = editor.domain_uuid_generate()
    
    # ネットワークインターフェイス
    for interface in req.interface:
        interface: DomainInsertInterface
        editor.domain_interface_add(
            network_name=interface.network_name, 
            mac_address=None, 
            port=interface.port
        )

    img_device_names = ["vda","vdb","vdc"]
    
    # ブロックデバイス
    for device, device_name in zip(req.disks, img_device_names):
        # 型定義
        device: DomainInsertDisk
        # 作成先のプールを参照
        try:
            new_pool: StorageModel = db.query(StorageModel).filter(StorageModel.uuid==device.save_pool_uuid).one()
        except:
            raise Exception("request storage pool uuid not found")
        # ファイル名決めてる
        create_image_path = f'{new_pool.path}/{task.user_id}_{req.name}_{device_name}_{domain_uuid}.img'
        # XMLに追加
        editor.domain_device_image_add(image_path=create_image_path, target_device=device_name)

        # 新規ディスクの場合
        if device.type == "empty":
            # 空のディスク作成
            ssh_manager = sshlib.SSHManager(user=node.user_name, domain=node.domain, port=node.port)
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
            ssh_manager = sshlib.SSHManager(user=node.user_name, domain=node.domain, port=node.port)
            ssh_manager.file_copy(
                from_path=from_image_path,
                to_path=create_image_path
            )

            if req.cloud_init != None:

                play_source = dict(
                    hosts = 'all',
                    gather_facts = 'no',
                    tasks = [dict(
                        qemu_img = dict(
                            dest = create_image_path,
                            size = f"{device.size_giga_byte}G",
                            state = "resize"
                        ),
                        become = "yes"
                )])

                res = ansible_manager.run_playbook(book=play_source)

    # Cloud-init
    if req.cloud_init != None:
        # iso作成
        cloudinit_manager = cloudinitlib.CloudInitManager(domain_uuid,req.cloud_init.hostname)
        cloudinit_manager.custom_user_data(req.cloud_init.userData)
        iso_path = cloudinit_manager.make_iso()

        # cloud-initのisoを保存するpoolを探す
        # try:
        #     query = db.query(StorageModel).join(NodeModel).outerjoin(StorageMetadataModel)
        #     query = query.filter(NodeModel.name==node.name).filter(StorageMetadataModel.rool=="init-iso")
        #     init_pool_model:StorageModel = query.one()
        # except:
        #     raise Exception("cloud-init pool not found")

        # 生成したisoをノードに転送
        # send_path = f"{init_pool_model.path}/{domain_uuid}.iso"
        send_path = f"/var/virty/cloud-init/{domain_uuid}.iso"
        ansible_manager = AnsibleManager(user=node.user_name, domain=node.domain)
        ansible_manager.create_dir(path="/var/virty/cloud-init/")
        ansible_manager.file_copy_to_node(src=iso_path,dest=send_path)
        editor.domain_cdrom(target=None,path=send_path)


    # ノードに接続してlibvirtでXMLを登録
    node = virtlib.VirtManager(node_model=node)
    node.domain_define(xml_str=editor.dump_str())

    task.message = f"Virtual machine ({req.name}@{task.user_id}) has been added successfully"


@worker_task(key="delete.vm.root")
def delete_vm_root(self: TaskBase, task: TaskModel, request: TaskRequest):
    db = self.db
    uuid = request.path_param["uuid"]

    try:
        domain: DomainModel = self.db.query(DomainModel).filter(DomainModel.uuid == uuid).one()
    except:
        raise Exception("domain not found")

    try:
        node: NodeModel = self.db.query(NodeModel).filter(NodeModel.name == domain.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    manager.domain_destroy(uuid=uuid)
    manager.domain_undefine(uuid)

    task.message = f"{domain.name} virtual machine has been deleted successfully"


@worker_task(key="patch.vm.power")
def patch_vm_root(self: TaskBase, task: TaskModel, request: TaskRequest):
    uuid = request.path_param["uuid"]
    body: PatchDomainPower = PatchDomainPower(**request.body)

    try:
        domain: DomainModel = self.db.query(DomainModel).filter(DomainModel.uuid == uuid).one()
    except:
        raise Exception("domain not found")

    try:
        node: NodeModel = self.db.query(NodeModel).filter(NodeModel.name == domain.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)

    # 電源
    if body.status == "on":
        manager.domain_poweron(uuid=uuid)
    elif body.status == "off":
        manager.domain_destroy(uuid=uuid)
    

@worker_task(key="patch.vm.cdrom")
def patch_vm_cdrom(self: TaskBase, task: TaskModel, request: TaskRequest):
    uuid = request.path_param["uuid"]
    body: PatchDominCdrom = PatchDominCdrom(**request.body)

    try:
        domain: DomainModel = self.db.query(DomainModel).filter(DomainModel.uuid == uuid).one()
    except:
        raise Exception("domain not found")

    try:
        node: NodeModel = self.db.query(NodeModel).filter(NodeModel.name == domain.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)

    if body.status == "mount":
        manager.domain_cdrom(uuid, body.target, body.path)
    elif body.status == "unmount":
        manager.domain_cdrom(uuid, body.target)


@worker_task(key="patch.vm.network")
def patch_vm_network(self: TaskBase, task: TaskModel, request: TaskRequest):
    db = self.db
    body: DomainNetworkChange = DomainNetworkChange(**request.body)


    try:
        domain: DomainModel = db.query(DomainModel).filter(DomainModel.uuid == body.uuid).one()
    except:
        raise Exception("domain not found")

    try:
        node: NodeModel = db.query(NodeModel).filter(NodeModel.name == domain.node_name).one()
    except:
        raise Exception("node not found")

    manager = virtlib.VirtManager(node_model=node)
    manager.domain_network(uuid=body.uuid, network=body.network_name, port=body.port, mac=body.mac)