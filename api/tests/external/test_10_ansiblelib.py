import random

from module.ansiblelib import AnsibleManager


def test_playbook(env, installed_sshkeys, run_prefix):
    server = random.choice(env.servers)
    
    am = AnsibleManager(user=server.username, domain=server.domain)
    assert am.run(playbook_name="commom/make_dir_recurse", extravars={"path": f"/tmp/{run_prefix}-virty-pytest"})


def test_make_dir_recurse(env, installed_sshkeys, run_prefix):
    server = random.choice(env.servers)
    
    am = AnsibleManager(user=server.username, domain=server.domain)
    assert am.run(playbook_name="commom/make_dir_recurse", extravars={"path": f"/var/lib/libvirt/test/{run_prefix}-unit"})


def test_qemu_image(env, installed_sshkeys, run_prefix):
    server = random.choice(env.servers)

    am = AnsibleManager(user=server.username, domain=server.domain)
    
    img_path = f"/tmp/{run_prefix}-virty-pytest.img"
    am.run(playbook_name="vms/qemu_image_create", extravars={ "path": img_path, "size": f"{16}G" })
    am.run(playbook_name="vms/qemu_image_resize", extravars={ "path": img_path, "size": f"{32}G" })
    
    
def test_node_infomation(env, installed_sshkeys):
    server = random.choice(env.servers)
    
    am = AnsibleManager(user=server.username, domain=server.domain)
    assert am.node_infomation()
