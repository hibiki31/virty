import json, yaml, shutil, os
from pytest import console_main

from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C

from settings import APP_ROOT, DATA_ROOT
from mixin.log import setup_logger

logger = setup_logger(__name__)

class AnsibleManager():
    def __init__(self, user, domain):
        self.user = user
        self.domain = domain
    
    def run_playbook(self, book, extra_vars={}):
        result = ansible_run(play_source=book, host_list=[f"{self.user}@{self.domain}"], extra_vars=extra_vars)
        summary = {
            "ok": 0,
            "failed": 0,
            "unreachable": 0
        }
        for i in result:
            if i["status"] == "ok":
                summary["ok"] += 1
            elif i["status"] == "failed":
                logger.error(i)
                raise Exception("ansible run failed ",str(i))
            elif i["status"] == "unreachable":
                summary["unreachable"] += 1
        
        logger.info(summary) 
        
        return {"summary": summary, "result": result}
    
    def node_infomation(self):
        run = self.run_playbook_file(yaml="test")
        result = run["result"][0]
        if result["status"] != "ok":
            raise Exception(result)

        # Gather_factsをjsonとして保存
        os.makedirs(f'{DATA_ROOT}/node/', exist_ok=True)
        with open(f'{DATA_ROOT}/node/{self.user}@{self.domain}.json', 'w') as f:
            json.dump(result, f, indent=4)
        
        logger.info(f'Get node infomation successfull{self.user}@{self.domain}')
        return result
    
    def run_playbook_file(self, yaml, extra_vars=[{}]):
        book = self.load_playbook_file(yaml_name=yaml)
        return self.run_playbook(book=book, extra_vars=extra_vars)

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
        return self.run_playbook(book=play_source)
    

    def create_dir(self, path):
        play_source = dict(
            name = "Ansible Play",
            hosts = 'all',
            gather_facts = 'no',
            tasks = [
                dict(
                    file = dict(
                        path = path,
                        state = "directory",
                    ),
                    become = "yes"
                )
            ]
        )
        return self.run_playbook(book=play_source)
    
    def load_playbook_file(self, yaml_name):
        with open(f'{APP_ROOT}/static/ansible/{yaml_name}.yml', 'r') as yml:
            config = yaml.safe_load(yml)
        return config[0]

class ResultCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.res = []

    def v2_runner_on_unreachable(self, result):
        host = result._host
        res = {
            "status": "unreachable",
            "host": host.name,
            "task_name": result.task_name,
            "result": result._result
        }
        # logger.debug(json.dumps(res, indent=4))
        self.res.append(res)
        self.host_unreachable[host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        host = result._host
        res = {
            "status": "ok",
            "host": host.name,
            "task_name": result.task_name,
            "result": result._result
        }
        # logger.debug(json.dumps(res, indent=4))
        self.res.append(res)
        self.host_ok[host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        res = {
            "status": "failed",
            "host": host.name,
            "task_name": result.task_name,
            "result": result._result
        }
        # logger.debug(json.dumps(res, indent=4))
        self.res.append(res)
        self.host_failed[host.get_name()] = result
    

def ansible_run(play_source, host_list, extra_vars={}):
    logger.info(json.dumps([play_source, host_list, extra_vars], indent=4))
    # ansible-playbookで指定できる引数と同じ
    context.CLIARGS = ImmutableDict(
        tags={}, 
        listtags=False, 
        listtasks=False, 
        listhosts=False, 
        syntax=False, 
        extra_vars=extra_vars,
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
        return results_callback.res


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
    pass


if __name__ == "__main__":
    test()