import os

import paramiko


class ParamikoManager():
    def __init__(self, user, domain, port):
        self.user = user
        self.domain = domain
        self.port = port
        self.client = paramiko.SSHClient()
        
        key_path = os.path.expanduser("~/.ssh/id_rsa")
        private_key = paramiko.RSAKey.from_private_key_file(key_path)
        print(user,domain)
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=domain, username=user, port=port, pkey=private_key)
        
    
    def sample_ls(self):
        stdin, stdout, stderr = self.client.exec_command("ls -l")
        print("コマンド出力:")
        for line in stdout:
            print(line.strip())

        print("エラー出力:")
        for line in stderr:
            print(line.strip())

    def close(self):
        self.client.close()
        print("リソースを解放しました")

    def __del__(self):
        self.close()