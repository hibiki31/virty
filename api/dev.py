from pprint import pprint
from module.sshlib import SSHManager

def main():
    mg = SSHManager("", "", 22)
    print(mg.get_node_cpu_core())



if __name__ == "__main__":
    main()