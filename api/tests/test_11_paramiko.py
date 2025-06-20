import random

from module.paramikolib import ParamikoManager


def test_get_info(env, installed_sshkeys):
    server = random.choice(env.servers)
    
    pm = ParamikoManager(user=server.username, domain=server.domain, port=22)
    
    core = pm.get_node_cpu_core()
    memory = int(pm.get_node_mem())
    cpu_gen = pm.get_node_cpu_name()
    os_like = pm.get_node_os_release()["ID_LIKE"]
    os_name = pm.get_node_os_release()["PRETTY_NAME"]
    os_version = pm.get_node_os_release()["VERSION_ID"]
    qemu_version = pm.get_node_qemu_version()
    libvirt_version = pm.get_node_libvirt_version()
    
    print(core, memory, cpu_gen, os_like, os_name, os_version, qemu_version, libvirt_version)
    

def test_get_copy_node_to_node(env, installed_sshkeys):
    if len(env.servers) < 2:
        return
    
    pm_1 = ParamikoManager(user=env.servers[0].username, domain=env.servers[0].domain, port=22)
    pm_2 = ParamikoManager(user=env.servers[1].username, domain=env.servers[1].domain, port=22)
    
    # テストファイルの作成
    
    test_file_path = "/tmp/virty_copy_test_file"
    pm_1.run_cmd(f"dd if=/dev/urandom of={test_file_path} bs=1M count=1")
    
    pm_1.scp_node_to_node(
        src_node=pm_1,
        dst_node=pm_2,
        src_path=test_file_path,
        dst_path="/tmp/virty_copy_test_file_dst"
    )