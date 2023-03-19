from pprint import pprint
from module.sshlib import SSHManager
from mixin.database import SessionLocal
from sqlalchemy.orm import Session


from node.models import NodeModel

from domain.tasks import put_vm_list

from module.ansiblelib import AnsibleManager


def main():
    pass

if __name__ == "__main__":
    main()