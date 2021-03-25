import os
import subprocess

from mixin.settings import virty_root


class CloudInitManager():
    def __init__(self, uuid, hostname):
        self.uuid = uuid
        self.hostname = hostname
        os.makedirs(f'{virty_root}/data/cloud-init/{uuid}', exist_ok=True)
        with open(f'{virty_root}/data/cloud-init/{uuid}/meta-data',mode='w') as f:
            f.writelines([
                f'instance-id: {hostname}\n',
                f'local-hostname: {hostname}\n'
            ])
        with open(f'{virty_root}/data/cloud-init/{uuid}/user-data',mode='w') as f:
            f.writelines([
                "#cloud-config\n"
            ])

    def custom_user_data(self, data:bytes):
        with open(f'{virty_root}/data/cloud-init/{self.uuid}/user-data',mode='w') as f:
            f.write(data)

    def make_iso(self):
        user_data_path = f'{virty_root}/data/cloud-init/{self.uuid}/user-data'
        meta_data_path = f'{virty_root}/data/cloud-init/{self.uuid}/meta-data'
        network_config_path = f'{virty_root}/data/cloud-init/{self.uuid}/network-config'
        iso_path = f'{virty_root}/data/cloud-init/{self.uuid}/init.iso'
        if os.path.exists(network_config_path):
            cmd = f'genisoimage -output {iso_path} -volid cidata -joliet -rock {user_data_path} {meta_data_path} {network_config_path}'
        else:
            cmd = f'genisoimage -output {iso_path} -volid cidata -joliet -rock {user_data_path} {meta_data_path}'
        subprocess.run(cmd, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        return iso_path
        