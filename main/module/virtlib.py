
import sys
import sqlite3
import subprocess
import xml.etree.ElementTree as ET
import libvirt
import pings
import os
import uuid
from module import setting

from module.xmllib import XmlEditor

from node.models import NodeModel
from module.model import ImageModel
from mixin.log import setup_logger
from storage.models import StorageModel
from network.models import NetworkModel

from typing import List, Optional


logger = setup_logger(__name__)


class VirtManager():
    def __init__(self,node_model:NodeModel):
        conn_ip = node_model.user_name + "@" + node_model.domain
        self.node = libvirt.open('qemu+ssh://' + conn_ip + '/system')
        self.node_model:NodeModel = node_model
    
    def storage_data(self, token) -> List[StorageModel]:
        # GlustorFSが遅い
        pools = self.node.listAllStoragePools(0)
        if pools == None:
            return []
        data = []
        for pool in pools:
            logger.info(f'プールのステータス{pool.info()}')
            if pool.info()[0] != 2 :
                storage = StorageModel(
                    uuid = pool.UUIDString(),
                    name = pool.name(),
                    node_name = self.node_model.name,
                    capacity = None,
                    available = None,
                    type = None,
                    protocol = None,
                    path = None,
                    active = pool.isActive(),
                    auto_start = pool.autostart(),
                    status = pool.info()[0],
                    update_token = token
                )
                data.append({"storage":storage, "image": []})
                continue
                
            logger.debug("ストレージのリフレッシュを開始")
            # GlustorFSが遅い
            pool.refresh()
            logger.debug("ストレージのリフレッシュが完了")
            storage_xml = XmlEditor(type="str", obj=pool.XMLDesc())
            storage_xml = storage_xml.storage_pase()
            storage = StorageModel(
                uuid = pool.UUIDString(),
                name = pool.name(),
                node_name = self.node_model.name,
                capacity = storage_xml.capacity,
                available = storage_xml.available,
                type = "",
                protocol = "",
                path = storage_xml.path,
                active = pool.isActive(),
                auto_start = pool.autostart(),
                status = pool.info()[0],
                update_token = token
            )
            image = []
            for image_obj in pool.listAllVolumes():
                xml_pace = XmlEditor(type="str", obj=image_obj.XMLDesc())
                xml_pace = xml_pace.image_pase()
                xml_pace.update_token = token
                image.append(xml_pace)
            data.append({"storage":storage, "image": image})
        return data
    
    def network_data(self, token):
        networks = self.node.listAllNetworks()
        data = []
        for net in networks:
            xml = XmlEditor(type="str", obj=net.XMLDesc())
            xml = xml.network_pase()
            data.append(NetworkModel(
                uuid = xml['uuid'],
                name = xml['name'],
                host_interface = xml['bridge'],
                type = xml['type'],
                active = net.isActive(),
                auto_start = net.autostart(),
                dhcp = None,
                update_token = token
            ))
            
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

    def domain_autostart(self,is_enable):
        con = self.node.lookupByUUIDString(uuid)
        # Enable
        if  con.autostart() == 1 and is_enable:
            con.setAutostart(0)
        # Disable
        elif con.autostart() == 0 and not is_enable:
            con.setAutostart(1)

    def domain_cdrom(self, uuid, target, path=None):
        con = self.node.lookupByUUIDString(uuid)

        xml = XmlEditor(type="str",obj=con.XMLDesc())
        con.updateDeviceFlags(xml.domain_cdrom(target=target,path=path))

    def storage_define(self,xml_str):
        sp = self.node.storagePoolDefineXML(xml_str,0)
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
        net.autostart(1)
