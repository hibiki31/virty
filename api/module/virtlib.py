
import sys
import sqlite3
import subprocess
import xml.etree.ElementTree as ET
import libvirt
import pings
import os
import uuid

from module.xmllib import XmlEditor

from node.models import NodeModel
from module.model import ImageModel
from mixin.log import setup_logger
from storage.models import StorageModel, StorageMetadataModel
from network.models import NetworkModel

from typing import List, Optional


logger = setup_logger(__name__)


class VirtManager():
    def __init__(self,node_model:NodeModel):
        conn_ip = node_model.user_name + "@" + node_model.domain
        self.node = libvirt.open('qemu+ssh://' + conn_ip + '/system')
        self.node_model:NodeModel = node_model

    ### DATA
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
    
    def storage_data(self, token) -> List[StorageModel]:
        # GlustorFSが遅い
        pools = self.node.listAllStoragePools(0)
        if pools == None:
            return []
        data = []
        for pool in pools:
            if pool.info()[0] != 2 :
                storage = StorageModel(
                    uuid = pool.UUIDString(),
                    name = pool.name(),
                    node_name = self.node_model.name,
                    capacity = None,
                    available = None,
                    path = None,
                    active = pool.isActive(),
                    auto_start = pool.autostart(),
                    status = pool.info()[0],
                    update_token = token,
                )
                data.append({"storage":storage, "image": []})
                continue
                
            # GlustorFSが遅い
            pool.refresh()
            storage_xml = XmlEditor(type="str", obj=pool.XMLDesc())
            storage_xml = storage_xml.storage_pase()
            storage = StorageModel(
                uuid = pool.UUIDString(),
                name = pool.name(),
                node_name = self.node_model.name,
                capacity = storage_xml.capacity,
                available = storage_xml.available,
                path = storage_xml.path,
                active = pool.isActive(),
                auto_start = pool.autostart(),
                status = pool.info()[0],
                update_token = token,
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
        for network in networks:
            xml = XmlEditor(type="str", obj=network.XMLDesc())
            xml.dump_file("network")
            xml = xml.network_pase()
            model = NetworkModel(
                uuid = xml['uuid'],
                name = xml['name'],
                host_interface = xml['bridge'],
                type = xml['type'],
                active = network.isActive(),
                auto_start = network.autostart(),
                dhcp = None,
                update_token = token
            )
            data.append(model)
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

    def domain_cdrom(self, uuid, target=None, path=None):
        con = self.node.lookupByUUIDString(uuid)

        xml = XmlEditor(type="str",obj=con.XMLDesc())
        con.updateDeviceFlags(xml.domain_cdrom(target=target,path=path))
    
    def domain_network(self, uuid, network, port, mac):
        domain = self.node.lookupByUUIDString(uuid)

        xml = XmlEditor(type="str",obj=domain.XMLDesc())
        xml = xml.domain_network(mac=mac,network=network,port=port)
        try:
            domain.updateDeviceFlags(xml)
        except libvirt.libvirtError as e:
            raise Exception("Cannot switch the OVS while the VM is running" + str(e))
         
        

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
        res = net.update(command=3,section=9, xml=xml, parentIndex=1)
        if res == -1:
            raise Exception("An error occurred after updating the network with libvirt")

    def network_ovs_delete(self, uuid, name):
        net = self.node.networkLookupByUUIDString(uuid)
        editor = XmlEditor(type="str",obj=net.XMLDesc())
        xml = editor.network_ovs_find(name=name)

        # https://libvirt.org/html/libvirt-libvirt-network.html#virNetworkUpdateCommand
        net.update(command=2,section=9, xml=xml, parentIndex=1)