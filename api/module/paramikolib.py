import time
from typing import Self

import paramiko

from mixin.log import setup_logger
from mixin.schemas import BaseSchema

logger = setup_logger(__name__)

BUFFER_SIZE = 32 * 1024 * 1024     # 32MiB
WIN_SIZE    = 32 * 1024 * 1024     # 32MiB (SSH channel window)
PKT_SIZE    = 32 * 1024 


class RemoteCommandFailed(Exception):
    pass

class RemoteCommandResult(BaseSchema):
    stdout: str
    stderr: str
    rc: int


class ParamikoManager():
    def __init__(
        self,
        user: str,
        domain: str,
        port: int,
        connect_timeout: float = 10,
        operation_timeout: float = 60,
    ) -> None:
        self.user = user
        self.domain = domain
        self.port = port
        self.operation_timeout = operation_timeout
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=domain,
            username=user,
            port=port,
            timeout=connect_timeout,
            banner_timeout=connect_timeout,
            auth_timeout=connect_timeout,
        )

        t = self.client.get_transport()
        t.window_size = WIN_SIZE
        t.packet_size = PKT_SIZE
    
    
    def run_cmd(self, command: str) -> RemoteCommandResult:
        _stdin, stdout, _stderr = self.client.exec_command(
            command,
            timeout=self.operation_timeout,
        )
        channel = stdout.channel
        deadline = time.monotonic() + self.operation_timeout
        stdout_chunks: list[bytes] = []
        stderr_chunks: list[bytes] = []

        while True:
            while channel.recv_ready():
                stdout_chunks.append(channel.recv(64 * 1024))
            while channel.recv_stderr_ready():
                stderr_chunks.append(channel.recv_stderr(64 * 1024))

            if channel.exit_status_ready():
                exit_status = channel.recv_exit_status()
                while channel.recv_ready():
                    stdout_chunks.append(channel.recv(64 * 1024))
                while channel.recv_stderr_ready():
                    stderr_chunks.append(channel.recv_stderr(64 * 1024))
                break

            if time.monotonic() >= deadline:
                channel.close()
                raise TimeoutError(
                    f"SSH command timed out after {self.operation_timeout:.1f}s: "
                    f"{self.user}@{self.domain} => {command}"
                )
            time.sleep(0.05)

        out = b"".join(stdout_chunks).decode(errors="replace")
        err = b"".join(stderr_chunks).decode(errors="replace")

        if exit_status != 0:
            logger.error(err)
            raise RemoteCommandFailed(f"Failed Command: {self.user}@{self.domain} => {command}")

        return RemoteCommandResult(stdout=out, stderr=err, rc=exit_status)

    
    def get_node_mem(self):
        res = self.run_cmd("cat /proc/meminfo |grep MemTotal")
        # Ex. MemTotal:       131957404 kB
        words = float(res.stdout.split()[1])
        memory = words/1024000
        return memory # GB


    def get_node_cpu_core(self):
        res = self.run_cmd("grep processor /proc/cpuinfo | wc -l")
        words = res.stdout.rstrip("\\n'").lstrip("'b")
        return words


    def get_node_libvirt_version(self):
        res = self.run_cmd("virsh version --daemon|grep libvirt|grep Using")

        return res.stdout.rstrip("\\n'").lstrip("'b").split()[3]
        
        
    def get_node_qemu_version(self):
        res = self.run_cmd("virsh version --daemon|grep hypervisor:")

        return res.stdout.split()[3]


    def get_node_cpu_name(self):
        res = self.run_cmd("grep 'model name' /proc/cpuinfo|uniq")
        words = res.stdout.split(":")[1].rstrip("\\n'")
        return words


    def get_node_os_release(self):
        res = self.run_cmd("cat /etc/os-release")
        result = {}
        # １行ずつ処理
        for line in res.stdout.splitlines():
            key = line.split("=")[0]
            value = line.split("=")[1]
            result[key] = value.replace('"', '')
        
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
    
    def scp_node_to_node(
        self,
        src_node: Self,
        dst_node: Self,
        src_path: str,
        dst_path: str,
    ) -> None:
        sftp_src = src_node.client.open_sftp()
        sftp_dst = dst_node.client.open_sftp()
        sftp_src.get_channel().settimeout(self.operation_timeout)
        sftp_dst.get_channel().settimeout(self.operation_timeout)
        
        
        # コピー元サイズを取得
        st = sftp_src.stat(src_path)
        total_bytes = st.st_size

        # 転送開始
        t0 = time.perf_counter()
        
        
        with sftp_src.open(src_path, "rb") as src_f:
            with sftp_dst.open(dst_path, "wb") as dst_f:
                while True:
                    chunk = src_f.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    dst_f.write(chunk)
        
        # 統計表示
        t1 = time.perf_counter()
        elapsed = t1 - t0
        mb     = total_bytes / (1024 * 1024)
        speed  = mb / elapsed if elapsed else 0
        
        logger.info(f"✔ Copied {src_path} ({mb:.2f} MiB) → {dst_path} \nElapsed : {elapsed:.2f} s \nSpeed   : {speed:.2f} MiB/s")
        

    def close(self):
        self.client.close()
        logger.info("The connection has been released")

    def __del__(self):
        self.close()
