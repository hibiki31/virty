import subprocess

from mixin.log import setup_logger

logger = setup_logger(__name__)


class SSHManager():
    def __init__(self, user, domain):
        self.base_cmd = ["ssh" , user+"@"+domain ]
    
    def run_cmd(self, cmd):
        cmd = self.base_cmd + cmd
        return subprocess.run(cmd, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE, )


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