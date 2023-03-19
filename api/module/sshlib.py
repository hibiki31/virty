import subprocess

from mixin.log import setup_logger

logger = setup_logger(__name__)


class SSHManager():
    def __init__(self, user, domain, port):
        self.user = user
        self.domain = domain
        self.port = port
        self.base_cmd = ["ssh" , f"{user}@{domain}", "-p", str(port)]

        self.add_known_hosts()

    def add_known_hosts(self):
        fo = open('/root/.ssh/known_hosts', 'ab')

        cmd = [ "ssh-keyscan", self.domain, ">> " ]
        
        subprocess.run(cmd, stdout=fo, stderr=subprocess.PIPE)


    
    def run_cmd(self, cmd):
        cmd = self.base_cmd + cmd
        return subprocess.run(cmd, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    
    def get_node_mem(self):
        res = self.run_cmd(["cat /proc/meminfo |grep MemTotal"])
        # Ex. MemTotal:       131957404 kB
        words = float(str(res.stdout).split()[1])
        memory = words/1024000
        return memory # GB


    def get_node_cpu_core(self):
        res = self.run_cmd(["grep processor /proc/cpuinfo | wc -l"])
        words = str(res.stdout).rstrip("\\n'").lstrip("'b")
        return words


    def get_node_libvirt_version(self):
        res = self.run_cmd(["virsh version --daemon|grep libvirt|grep Using"])
        try:
            version = str(res.stdout)
        except:
            return "error"
        return version.rstrip("\\n'").lstrip("'b").split()[3]
        
        
    def get_node_qemu_version(self):
        res = self.run_cmd(["virsh version --daemon|grep hypervisor:"])
        try:
            version = str(res.stdout)
        except:
            return "error"
        return version.rstrip("\\n'").lstrip("'b").split()[3]


    def get_node_cpu_name(self):
        res = self.run_cmd(["grep 'model name' /proc/cpuinfo|uniq"])
        words = str(res.stdout).split(":")[1].rstrip("\\n'")
        return words


    def get_node_os_release(self):
        res = self.run_cmd(["cat" ,"/etc/os-release"])
        result = {}
        # １行ずつ処理
        for line in res.stdout.splitlines():
            key = line.split("=")[0]
            value = line.split("=")[1]
            result[key] = value
        
        '''
        NAME="Ubuntu"
        VERSION="20.04.5 LTS (Focal Fossa)"
        ID=ubuntu
        ID_LIKE=debian
        PRETTY_NAME="Ubuntu 20.04.5 LTS"
        VERSION_ID="20.04"
        HOME_URL="https://www.ubuntu.com/"
        SUPPORT_URL="https://help.ubuntu.com/"
        BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
        PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
        VERSION_CODENAME=focal
        UBUNTU_CODENAME=focal
        '''
        return result


    def qemu_create(self, path:str, size_giga_byte:int):
        check_res = self.run_cmd(["sudo", "test -e", path, "; echo $?"])

        if check_res.returncode != 0:
            raise Exception(check_res.stderr)

        # ファイルが存在しないか確認
        if check_res.stdout == "1\n":
            # そもそもコマンドが正常に通るか確認
            create_res = self.run_cmd(["sudo", "qemu-img create -f qcow2 " ,path, str(size_giga_byte)+"G"])

            # 終了結果が正常か判定
            if create_res.stdout.splitlines()[0].split(" ")[0] == "Formatting":
                return True
            else:
                logger.error(create_res.stdout)
                logger.error(create_res.stderr)
                raise Exception("qemu-img command output is illegal")
        else:
            raise Exception("request disk is already exists")
    

    def file_copy(self, from_path:str, to_path:str):
        check_res = self.run_cmd(["sudo", "test -e", to_path, "; echo $?"])

        if check_res.returncode != 0:
            raise Exception(check_res.stderr)

        # ファイルが存在しないか確認
        if check_res.stdout == "1\n":
            # コマンド実行
            create_res = self.run_cmd(["sudo", "cp" ,from_path, to_path])
            # 終了結果が正常か判定
            if create_res.stderr.split() == []:
                return True
            else:
                logger.error(create_res.stderr)
                raise Exception("cp command output is illegal")
        else:
            raise Exception("request disk is already exists")

    def scp_other_node(self, from_node, from_path, to_node, to_path):
        # cmd = ([
        #     "ssh",
        #     "-t",
        #     f"{from_node.user_name}@{from_node.domain}",
        #     f"sudo tar cv {from_path}",
        #     "|",
        #     "ssh",
        #     "-t",
        #     f"{to_node.user_name}@{to_node.domain}",
        #     f"'sudo tar xv {from_path}'",

        # ])

        cmd = (
            "scp",
            "-3",
            f"{from_node.user_name}@{from_node.domain}:{from_path}",
            f"{to_node.user_name}@{to_node.domain}:{to_path}"
        )
        # proc = subprocess.Popen(cmd, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)