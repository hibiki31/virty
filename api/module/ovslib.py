# from ryu.lib.ovs import vsctl

from mixin.log import setup_logger

import socket
import json

import ipaddress

logger = setup_logger(__name__)

"https://programtalk.com/python-examples/ryu.lib.ovs.vsctl.VSCtlCommand/?ipage=1"
class OVSManager():
    def __init__(self, domain):
        self.port = 6632
        self.address = f'tcp:{socket.gethostbyname(domain)}:{self.port}'
        self.vc =  vsctl.VSCtl(self.address)
        logger.debug(self.address)
    
    def get_info(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.node_model.domain, self.port))

        monitor_query = {
            "method":"monitor",
            "params":[
                "Open_vSwitch",
                "null",
                {"Open_vSwitch":{
                    "columns":[
                        "bridges",
                        "cur_cfg",
                        "db_version",
                        "external_ids",
                        "manager_options",
                        "next_cfg",
                        "other_config",
                        "ovs_version",
                        "ssl",
                        "statistics",
                        "system_type",
                        "system_version"
                    ]
                }}
            ],
            "id":0
        }
        s.send(json.dumps(monitor_query).encode())
        response = s.recv(8192)
        result = json.loads(response.decode())
        print(json.dumps(result, sort_keys=False, indent=1))


    def ovs_run(self, cmd, args=None):
        logger.info(f"{self.address} run {cmd} args {args}")
        command = vsctl.VSCtlCommand(command=cmd, args=args)
        self.vc.run_command([command])
        return command


    def ovs_runs(self, cmds):
        logger.info(f"{self.address} run {cmds}")
        command = [vsctl.VSCtlCommand(command=cmd[0], args=cmd[1]) for cmd in cmds]
        self.vc.run_command(command)
        return command


    def ovs_crean(self):
        cmd = self.ovs_run('list-br')

        for i in cmd.result:
            if i != "ovs-network" and i != "ovs-br-akane":
                self.ovs_del_br(i)
    
    def ovs_del_br(self, bridge):
        self.ovs_run('del-br', (bridge,))
    
    def ovs_add_br(self, bridge):
        self.ovs_run('add-br', (bridge,))
        self.ovs_run('set',('Bridge', bridge, 'stp_enable=true', ))
    
    def ovs_add_vxlan(self, bridge, remote, key):
        ip_hex = str(hex(int(ipaddress.ip_address(remote))))
        inf = f'{bridge}-{ip_hex}'
        bridge = f'{bridge}'

        cmds = [
            ['add-port', [bridge, inf, ]],
            ['set', ['Interface', inf, 'type=vxlan', f'options:key={key}', f'options:remote_ip={remote}']]
        ]
        self.ovs_runs(cmds)
    
    def ovs_list_br(self):
        cmd = self.ovs_run('list-br')
        return cmd.result
    
    def ovs_list_port(self, bridge):
        cmd = self.ovs_run('list-ports', [bridge,])
        return cmd.result

    def ovs_get_port(self):
        cmd = self.ovs_run('list', ['port'])