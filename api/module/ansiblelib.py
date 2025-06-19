import json
import os
from pprint import pformat

import ansible_runner

from mixin.log import setup_logger
from mixin.schemas import BaseModel
from settings import APP_ROOT, DATA_ROOT

logger = setup_logger(__name__)


class AnsibleRunResult(BaseModel):
    status: str
    rc: int
    events_ok: list
    events_failed: list
    playbook_on_stats: dict

class AnsibleManager():
    def __init__(self, user, domain):
        self.user = user
        self.domain = domain
        
    def run(self, playbook_name:str, extravars={}, timeout=60):
        hosts = f"{self.user}@{self.domain}"
        
        logger.info(f"Ansible playbook run: {hosts} name={playbook_name} extravars={extravars}")
        
        res = ansible_runner.run(
            timeout=timeout,
            private_data_dir=f'{DATA_ROOT}/ansible/',
            inventory={ 'all':{
                'hosts': hosts
                }
            },
            playbook=self.get_playbook_path(playbook_name),
            extravars=extravars,
            host_pattern='all',
            quiet=True
        )
        
        os.makedirs(f'{DATA_ROOT}/node/', exist_ok=True)
        runner_on_ok = []
        runner_on_failed = []
        playbook_on_stats = None
        for event in res.events:
            if event['event'] == 'runner_on_ok':
                runner_on_ok.append(event)
            if event['event'] == 'runner_on_failed':
                runner_on_failed.append(event)
            
            if event['event'] == 'playbook_on_stats':
                playbook_on_stats = event['event_data']
            
            logger.debug(first_n_lines(pformat(event),10))
                
        if res.rc == 0:
            logger.info(f"[Finish] BookName: {playbook_name} ReturnCode: {res.rc} Status: {res.status}")
            for event_ok in runner_on_ok:
                logger.info(first_n_lines(pformat(event_ok['event_data'],10)))
        else:
            msg = f"[Finish] BookName: {playbook_name} ReturnCode: {res.rc} Status: {res.status}"
            logger.error(msg)
            exe = Exception(msg)
            exe.add_note("------ addtional info ------")
            for event_error in runner_on_failed:
                exe.add_note(pformat(event_error['event_data']))
            if runner_on_failed == []:
                exe.add_note(pformat(res.events))
            raise exe
        
        with open(f'{DATA_ROOT}/node/{self.user}@{self.domain}.json', 'w') as f:
            json.dump({"ok": runner_on_ok, "failed": runner_on_failed, "status": playbook_on_stats}, f, indent=4)
    
        return AnsibleRunResult(status=res.status, rc=res.rc, events_ok=runner_on_ok, events_failed=runner_on_failed, playbook_on_stats=playbook_on_stats)


    def get_playbook_path(self, playbook_name:str):
        playbook_path = f"{APP_ROOT}/static/ansible/{playbook_name}.yml"
        if not os.path.exists(playbook_path):
            raise Exception(f"Playbook not found: {playbook_path}")
        return playbook_path
    
    def node_infomation(self):
        result  = self.run(playbook_name="test")
        try:
            node_info = result.events_ok[0]["event_data"]["res"]["ansible_facts"]
        except Exception:
            raise Exception("Failed get node information by Ansible")
        
        logger.info(f'Get node infomation successfull {self.user}@{self.domain}')
        return node_info


def first_n_lines(text: str, n: int = 10) -> str:
    # 行区切りで分割し、先頭 n 行だけ取り出して再結合
    return "\n".join(text.splitlines()[:n])