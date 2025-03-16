
from module.ansiblelib import AnsibleManager
from tests.model import TestEnviroment


def main(env: TestEnviroment):
    play_source =  dict(
        name = "Ansible Play",
        hosts = 'all',
        gather_facts = 'no',
        tasks = [
            dict(action=dict(module='shell', args='ls -l'), register='shell_out')
        ]
    )
    

    am = AnsibleManager(user=env.servers[0].username, domain=env.servers[0].domain)
    am.run_playbook(book=play_source)