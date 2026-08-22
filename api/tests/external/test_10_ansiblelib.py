import json

from module.ansiblelib import AnsibleManager
from tests.external.support.remote_inventory import remote_inventory_manager


def test_playbook(env, installed_sshkeys, run_prefix):
    for server in env.servers:
        manager = AnsibleManager(user=server.username, domain=server.domain)
        result = manager.run(
            playbook_name="commom/make_dir_recurse",
            extravars={"path": f"/tmp/{run_prefix}-virty-pytest"},
        )
        assert result.rc == 0
        assert result.status == "successful"


def test_make_dir_recurse(env, installed_sshkeys, run_prefix):
    for server in env.servers:
        manager = AnsibleManager(user=server.username, domain=server.domain)
        result = manager.run(
            playbook_name="commom/make_dir_recurse",
            extravars={"path": f"/var/lib/libvirt/test/{run_prefix}-unit"},
        )
        assert result.rc == 0
        assert result.status == "successful"


def test_qemu_image(env, installed_sshkeys, run_prefix):
    img_path = f"/tmp/{run_prefix}-virty-pytest.img"
    for server_index, server in enumerate(env.servers):
        ansible = AnsibleManager(user=server.username, domain=server.domain)
        created = ansible.run(
            playbook_name="vms/qemu_image_create",
            extravars={"path": img_path, "size": "16G"},
        )
        assert created.rc == 0
        with remote_inventory_manager(
            user=server.username,
            domain=server.domain,
            server_index=server_index,
        ) as ssh:
            created_info = json.loads(
                ssh.run_cmd(f"qemu-img info --output=json {img_path}").stdout
            )
            assert created_info["virtual-size"] == 16 * 1024**3
            resized = ansible.run(
                playbook_name="vms/qemu_image_resize",
                extravars={"path": img_path, "size": "32G"},
            )
            assert resized.rc == 0
            resized_info = json.loads(
                ssh.run_cmd(f"qemu-img info --output=json {img_path}").stdout
            )
            assert resized_info["virtual-size"] == 32 * 1024**3


def test_node_information(env, installed_sshkeys):
    for server in env.servers:
        manager = AnsibleManager(user=server.username, domain=server.domain)
        facts = manager.node_infomation()
        assert isinstance(facts, dict)
        assert facts
