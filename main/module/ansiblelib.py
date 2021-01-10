import json
import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C


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


def test():
    play_source =  dict(
        name = "Ansible Play",
        hosts = 'all',
        gather_facts = 'no',
        tasks = [
            dict(action=dict(module='shell', args='ls -l /'), register='shell_out')
        ]
    )
    
    host_list = [ "user@192.168.0.1" ]

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
        become=False,
        become_method='Sudo', 
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
    pass