import json

from ansible import context
from ansible.cli import CLI
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager

loader = DataLoader()


class ResultCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        print("callback init")

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result
        print(result)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        """Print a json representation of the result.

        Also, store the result in an instance attribute for retrieval later
        """
        host = result._host
        self.host_ok[host.get_name()] = result
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result
        print("aaaa")

results_callback = ResultCallback()

context.CLIARGS = ImmutableDict(tags={}, listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
                    module_path=None, forks=100, remote_user='', private_key_file=None,
                    ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=True,
                    become_method='Sudo', become_user='root', verbosity=True, check=False, start_at_task=None, stdout_callback=results_callback)

inventory = InventoryManager(loader=loader, sources=('10.0.0.27,'))

variable_manager = VariableManager(loader=loader, inventory=inventory, version_info=CLI.version_info(gitinfo=False))

pbex = PlaybookExecutor(playbooks=['./static/ansible/ls.yml'], inventory=inventory, variable_manager=variable_manager, loader=loader, passwords={})

results = pbex.run()

print(results)