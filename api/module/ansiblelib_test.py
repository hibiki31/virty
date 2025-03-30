
from module.ansiblelib import AnsibleManager
from tests.model import TestEnviroment


def main(env: TestEnviroment):
    am = AnsibleManager(user=env.servers[0].username, domain=env.servers[0].domain)
    am.run(playbook_name='test', extravars={})