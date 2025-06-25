
import re
from typing import Final, List

import libvirt

from mixin.log import setup_logger
from module.xmllib import StorageXmlEditor, XmlEditor
from network.schemas import PaseNetwork
from node.models import NodeModel
from storage.schemas import ImageForLibvirt, StorageForLibvirt

logger = setup_logger(__name__)

class LibvirtPortNotfound(Exception):
    pass

class StoragePoolAlreadyExistsError(RuntimeError):
    """プールが既に存在するとき専用の例外"""

# libvirt が返す「操作失敗」のエラーコード
OP_FAILED: Final[int] = libvirt.VIR_ERR_OPERATION_FAILED

class VirtManager():
    def __init__(self,node_model:NodeModel):
        conn_ip = f'{node_model.user_name}@{node_model.domain}'
        self.node = libvirt.open(f'qemu+ssh://{conn_ip}/system')
        self.lib_version = self.node.getLibVersion()
        logger.info(f"Connected: {f'qemu+ssh://{conn_ip}/system'}")
        self.node_model:NodeModel = node_model


    def domain_data(self):
        if self.node == None:
            return
        domains = self.node.listAllDomains()
        DATA = []
        for domain in domains:
            temp = {}
            temp['status'] = domain.state()[0]
            temp['auto'] = domain.autostart()
            temp['xml'] = domain.XMLDesc()
            DATA.append(temp)
        return DATA


    def storages_data(self, token:str, uuids:List[str]=[]) -> List[StorageForLibvirt]:
        data = []
        
        if len(uuids) == 0:
            pools = self.node.listAllStoragePools(0)
            if pools is None:
                return
            for pool in pools:
                data.append(self.storage_data(pool=pool, token=token))
        else:
            for uuid in uuids:
                pool = self.node.storagePoolLookupByUUIDString(uuid)
                data.append(self.storage_data(pool=pool, token=token))
        return data
    
    def storage_data(self, pool: libvirt.virStoragePool, token:str) -> List[StorageForLibvirt]:
        pool.refresh()
        storage_editor = StorageXmlEditor(type="str", obj=pool.XMLDesc())
        storage_xml = storage_editor.storage_pase()

        storage = StorageForLibvirt(
            **storage_xml.model_dump(),
            node_name = self.node_model.name,
            active = pool.isActive(),
            auto_start = pool.autostart(),
            status = pool.info()[0],
            update_token = token,
            images=[],
        )
        for image_obj in pool.listAllVolumes():
            image_editor = StorageXmlEditor(type="str", obj=image_obj.XMLDesc())
            image_xml = image_editor.image_pase()
            image = ImageForLibvirt(
                **image_xml.model_dump(),
                storage_uuid = storage.uuid,
                update_token = token,
            )
            storage.images.append(image)
        
        return storage

    def image_delete(self, storage_uuid, image_name, secure:bool = False):
        pool = self.node.storagePoolLookupByUUIDString(storage_uuid)
        pool.refresh(0)
        vol = pool.storageVolLookupByName(image_name)
        
        if secure:
            vol.delete(flags=libvirt.VIR_STORAGE_VOL_DELETE_ZEROED)
        else:
            vol.delete(flags=libvirt.VIR_STORAGE_VOL_DELETE_NORMAL)


    def network_data(self) -> list[PaseNetwork]:
        networks = self.node.listAllNetworks()
        data = []
        for network in networks:
            xml = XmlEditor(type="str", obj=network.XMLDesc())
            xml.dump_file("network")
            xml = xml.network_pase()
            data.append(xml)
        return data


    def domain_define(self, xml_str):
        self.node.defineXML(xml_str)


    def domain_undefine(self, uuid):
        con = self.node.lookupByUUIDString(uuid)
        con.undefine()


    def domain_destroy(self, uuid):
        con = self.node.lookupByUUIDString(uuid)
        if con.state()[0] != 5:
            con.destroy()


    def domain_shutdown(self, uuid):
        con = self.node.lookupByUUIDString(uuid)
        if con.state()[0] != 5:
            con.shutdown()


    def domain_poweron(self, uuid):
        con = self.node.lookupByUUIDString(uuid)
        if con.state()[0] != 1:
            con.create()


    def domain_autostart(self, uuid, is_enable):
        con = self.node.lookupByUUIDString(uuid)
        # Enable
        if  con.autostart() == 1 and is_enable:
            con.setAutostart(0)
        # Disable
        elif con.autostart() == 0 and not is_enable:
            con.setAutostart(1)


    def domain_rename(self, uuid, new_name):
        con = self.node.lookupByUUIDString(uuid)
        con.rename(new_name=new_name)


    def domain_core(self, uuid, core):
        con = self.node.lookupByUUIDString(uuid)
        con.setVcpusFlags(nvcpus=core, flags=2)


    def domain_cdrom(self, uuid, target=None, path=""):
        con = self.node.lookupByUUIDString(uuid)

        xml = XmlEditor(type="str",obj=con.XMLDesc())
        con.updateDeviceFlags(xml.domain_cdrom(target=target,path=path))
    

    def domain_network(self, uuid, network, port, mac):
        domain = self.node.lookupByUUIDString(uuid)

        xml = XmlEditor(type="str",obj=domain.XMLDesc())
        xml = xml.domain_network(mac=mac,network=network,port=port)
        
        # Flagが0 CURRENT, 1 LIVEだとVM停止すると元に戻る
        domain.updateDeviceFlags(xml,flags=0)
        # 2 CONFIGも同時に変更して、永続化＋ライブ更新を入れている
        domain.updateDeviceFlags(xml,flags=2)
        
        

    def storage_define(self,xml_str):
        try:
            sp = self.node.storagePoolDefineXML(xml_str,0)
            
        except libvirt.libvirtError as e:
            # 1) libvirt 側で「操作失敗」扱いか確認
            is_op_failed = e.get_error_code() == OP_FAILED

            # 2) エラーメッセージに already exists を含むか確認（大文字小文字を無視）
            is_already_exists = bool(re.search(r"already\s+exists", e.get_error_message(), re.I))

            if is_op_failed and is_already_exists:
                # 専用例外に変換してエスカレーション
                raise StoragePoolAlreadyExistsError(e.get_error_message()) from e

            # それ以外は元の例外をそのまま投げ直す
            raise
    
        sp.create()
        sp.setAutostart(1)


    def storage_undefine(self, uuid):
        sp = self.node.storagePoolLookupByUUIDString(uuid)
        if sp.info()[0] == 2:
            sp.destroy()
        sp.undefine()


    def network_define(self,xml_str):
        net = self.node.networkDefineXML(xml_str)
        net.create()
        net.autostart()


    def network_undefine(self, uuid):
        net = self.node.networkLookupByUUIDString(uuid)
        try:
            net.destroy()
        except:
            pass
        net.undefine()

    def network_ovs_add(self, uuid, name, vlan):
        net = self.node.networkLookupByUUIDString(uuid)
        xml = f'''
        <portgroup name="{name}">
            <vlan>
            <tag id="{str(vlan)}" />
            </vlan>
        </portgroup>
        '''
        # https://libvirt.org/html/libvirt-libvirt-network.html#virNetworkUpdateCommand
        # command: VIR_NETWORK_UPDATE_COMMAND_ADD_LAST	=	3
        # section: VIR_NETWORK_SECTION_PORTGROUP	=	9 (0x9)	
        # parentIndex: 1先頭, -1適当末尾 
        res = self.network_update(net=net, command=3, section=9, xml=xml, parentIndex=1, flags=1) #LIVE
        res = self.network_update(net=net, command=3, section=9, xml=xml, parentIndex=1, flags=2) #CONFIG
        logger.info(res)


    def network_ovs_delete(self, uuid, name):
        net = self.node.networkLookupByUUIDString(uuid)
        editor = XmlEditor(type="str",obj=net.XMLDesc())
        xml = editor.network_ovs_find(name=name)
        if xml is None:
            raise LibvirtPortNotfound(f"Port is alredy deleted {uuid}, {name}")

        # https://libvirt.org/html/libvirt-libvirt-network.html#virNetworkUpdateCommand
        res = self.network_update(net=net, command=2, section=9, xml=xml, parentIndex=1, flags=1) #LIVE
        res = self.network_update(net=net, command=2, section=9, xml=xml, parentIndex=1, flags=2) #CONFIG
        logger.info(res)
    
    def network_update(self, net, command, section, xml, parentIndex, flags=0):
        # 新しいlibvirtでセクションとコマンドが逆のバグが直った
        # https://github.com/digitalocean/go-libvirt/pull/148#issue-1234093981
        # 6.0.0では逆、少なくとも8.0.0で直ってる
        if self.lib_version == 10000000:
            res = net.update(command=section,section=command, xml=xml, parentIndex=parentIndex, flags=flags)
        else:
            res = net.update(command=command,section=section, xml=xml, parentIndex=parentIndex, flags=flags)
        if res == -1:
            raise Exception("An error occurred after updating the network with libvirt")

        return res