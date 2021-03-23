import json
import shutil
import os
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C

from mixin.settings import virty_root
from mixin.log import setup_logger

logger = setup_logger(__name__)

class AnsibleManager():
    def __init__(self, user, domain):
        self.user = user
        self.domain = domain
    
    def node_test(self):
        play_source = dict(
            name = "Node test",
            hosts = 'all',
            gather_facts = 'yes',
        )
        result = ansible_runner(play_dict=play_source, host=f"{self.user}@{self.domain}")
        os.makedirs(f'{virty_root}/data/node/', exist_ok=True)
        with open(f'{virty_root}/data/node/{self.user}@{self.domain}.json', 'w') as f:
            json.dump(result, f, indent=4)
        logger.info(f'{self.user}@{self.domain} SSH: {result["status"]}')
    
    def node_infomation(self):
        play_source = dict(
            name = "Node test",
            hosts = 'all',
            gather_facts = 'yes',
        )
        result = ansible_runner(play_dict=play_source, host=f"{self.user}@{self.domain}")
        os.makedirs(f'{virty_root}/data/node/', exist_ok=True)
        with open(f'{virty_root}/data/node/{self.user}@{self.domain}.json', 'w') as f:
            json.dump(result, f, indent=4)
        logger.info(f'{self.user}@{self.domain} SSH: {result["status"]}')
        return result
    
    def run_playbook(self, book):
        result = ansible_runner(play_dict=book, host=f"{self.user}@{self.domain}")
        print(json.dumps(result, indent=4))
        return result

    def file_copy_to_node(self, src, dest):
        play_source = dict(
            name = "Ansible Play",
            hosts = 'all',
            gather_facts = 'no',
            tasks = [
                dict(
                    synchronize = dict(
                        src = src,
                        dest = dest,
                        compress = "no"
                    ),
                    become = "yes"
                )
            ]
        )
        result = ansible_runner(play_dict=play_source, host=f"{self.user}@{self.domain}")
        print(json.dumps(result, indent=4))
        return result
    
    

class ResultCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        host = result._host
        self.host_ok[host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result

def debug():
    play_source =  dict(
        name = "Ansible Play",
        hosts = 'all',
        gather_facts = 'no',
        tasks = [
            dict(action=dict(module='shell', args='lssss -l'), register='shell_out')
        ]
    )
    
    host_list = [ "akane@192.168.144.31" ]

    results = ansible_run(play_source=play_source, host_list=host_list)

    for host, result in results.host_ok.items():
        print(host)
        print(json.dumps(result._result, indent=4))
    
    for host, result in results.host_failed.items():
        print(host)
        print(json.dumps(result._result, indent=4))
    
    for host, result in results.host_unreachable.items():
        print(host)
        print(json.dumps(result._result, indent=4))

def test():
    play_source =  dict(
        name = "Ansible Play",
        hosts = 'all',
        gather_facts = 'no',
        tasks = [
            dict(action=dict(module='shell', args='lssss -l'), register='shell_out')
        ]
    )

    result = ansible_runner(play_dict=play_source, host="akane@192.168.144.31")
    print(json.dumps(result, indent=4))


def ansible_runner(play_dict, host):
    play_source =  play_dict
    
    host_list = [ host ]

    results = ansible_run(play_source=play_source, host_list=host_list)

    for host, result in results.host_ok.items():
        return {
            "status": "ok",
            "host": host,
            "result": result._result
        }
    for host, result in results.host_failed.items():
        return {
            "status": "failed",
            "host": host,
            "result": result._result
        }
    for host, result in results.host_unreachable.items():
        return {
            "status": "unreachable",
            "host": host,
            "result": result._result
        }
    

def ansible_run(play_source, host_list):
    # ansible-playbookで指定できる引数と同じ
    context.CLIARGS = ImmutableDict(
        tags={}, 
        listtags=False, 
        listtasks=False, 
        listhosts=False, 
        syntax=False, 
        connection='ssh',                
        module_path=None, 
        forks=100, 
        private_key_file=None,
        ssh_common_args=None, 
        ssh_extra_args=None, 
        sftp_extra_args=None, 
        scp_extra_args=None, 
        become=True,
        become_method='sudo', 
        become_user='root', 
        verbosity=True, 
        check=False, 
        start_at_task=None
    )

    # 鍵認証が優先され、パスワードを聞かれた場合のみ利用する。書きたくない場合は適当でOK
    passwords = dict(vault_pass='secret')

    # コールバックのインスタンス化
    results_callback = ResultCallback()

    # インベントリを１ライナー用フォーマットに変換
    sources = ','.join(host_list)
    if len(host_list) == 1:
        sources += ','
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=sources)

    # 値をセット
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # 実行
    tqm = None
    try:
        tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                passwords=passwords,
                stdout_callback=results_callback, 
            )
        result = tqm.run(play)
    finally:
        # 終了後に一時ファイルを削除している
        if tqm is not None:
            tqm.cleanup()
        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
        return results_callback

if __name__ == "__main__":
    test()