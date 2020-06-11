import paramiko

import time

R_HOST='192.168.

client = paramiko.SSHClient()
client.load_system_host_keys()

client.connect(R_HOST)

try:
    ssh_shell = client.invoke_shell()
except:
    exit

stdin, stdout, stderr = client.exec_command('ip a')

print(stdout.read().decode('utf-8'))