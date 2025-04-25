import json
import os

import ansible_runner

from mixin.log import setup_logger
from mixin.schemas import BaseModel
from settings import APP_ROOT, DATA_ROOT

logger = setup_logger(__name__)


class AnsibleRunResult(BaseModel):
    status: str
    rc: int
    events: list

class AnsibleManager():
    def __init__(self, user, domain):
        self.user = user
        self.domain = domain
        
    def run(self, playbook_name:str, extravars={}):
        r:ansible_runner.Runner = ansible_runner.run(
            inventory={ 'all':{
                'hosts': f"{self.user}@{self.domain}"
                }
            },
            playbook=self.get_playbook_path(playbook_name),
            extravars=extravars,
            host_pattern='all'
        )
        logger.info(f"{playbook_name} {r.rc} {r.status}")
        
        os.makedirs(f'{DATA_ROOT}/node/', exist_ok=True)
        result = []
        for event in r.events:
            if event['event'] == 'runner_on_ok':
                result.append(event)
        
        with open(f'{DATA_ROOT}/node/{self.user}@{self.domain}.json', 'w') as f:
            json.dump(result, f, indent=4)
        
        return AnsibleRunResult(status=r.status, rc=r.rc, events=result)
    
    def get_playbook_path(self, playbook_name:str):
        playbook_path = f"{APP_ROOT}/static/ansible/{playbook_name}.yml"
        if not os.path.exists(playbook_path):
            raise Exception(f"Playbook not found: {playbook_path}")
        return playbook_path
    
    def node_infomation(self):
        result  = self.run(playbook_name="test")
        try:
            node_info = result.events[0]["event_data"]["res"]["ansible_facts"]
        except Exception:
            raise Exception(result)
        
        logger.info(f'Get node infomation successfull{self.user}@{self.domain}')
        return node_info
