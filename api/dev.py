from time import sleep

from module.ansiblelib import AnsibleManager


def main():
    while True:
        am = AnsibleManager("akane", "192.168.144.33")
        am.run("ls", extravars={"ls_dir": "/"})
        sleep(5)

if __name__ == "__main__":
    main()