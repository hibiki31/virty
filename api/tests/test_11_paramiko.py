import random

from module.paramikolib import ParamikoManager


def test_sample(env):
    server = random.choice(env.servers)
    
    pm = ParamikoManager(user=server.username, domain=server.domain, port=22)
    pm.sample_ls()