import secrets

from module.virtlib import VirtManager
from module.xmllib import XmlEditor
from network.schemas import NetworkForCreate
from node.models import NodeModel


def create_network(body: NetworkForCreate, node: NodeModel):
    editor = XmlEditor("static","net_base")
    
    if not body.bridge_name:
        body.bridge_name = f"v-{secrets.token_hex(4)}"

    editor.network_base(name=body.name, bridge=body.bridge_name)

    if body.forward_mode == "isorated":
        editor.network_forward(None)
    elif body.forward_mode == "ovs":
        editor.network_ovs()
        editor.network_forward("bridge")
    else:
        editor.network_forward(body.forward_mode)
    
    if body.ip:
        editor.network_ip(address=str(body.ip.address), netmask=str(body.ip.netmask))
        if body.dhcp:
            editor.network_dhcp(start=str(body.dhcp.start), end=str(body.dhcp.end))
        else:
            editor.network_dhcp_delete()
    else:
        editor.network_ip_delete()

    xml = editor.dump_str()

    # ソイや！
    manager = VirtManager(node_model=node)
    manager.network_define(xml_str=xml)