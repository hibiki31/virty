import base64
import paramiko
import pprint

def main():
    get_data = ssh_pass_code(
        host = "192.168",
        user = "",
        password = "",
        command = "ip a"
    )
    pprint.pprint(get_data)

def ssh_pass_code(host, user, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user,password=password )

    channel = client.get_transport().open_session()
    channel.exec_command(command)

    # 標準出力
    # バッファーは1kb
    get_std = b''
    for i in range(1,10):
        buff = channel.recv(1024)
        if buff == b'':
            break
        get_std += buff
    get_std = get_std.decode().splitlines()

    get_err =b''
    for i in range(1,10):
        buff = channel.recv_stderr(1024)
        if buff == b'':
            break
        get_err += buff
    
    get_err = get_err.decode().splitlines()

    code = int(channel.recv_exit_status())
    client.close()
    return [code, get_std, get_err]

if __name__ == "__main__":
    main()