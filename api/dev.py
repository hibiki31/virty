from pprint import pprint
from module.sshlib import SSHManager
from mixin.database import SessionLocal
from sqlalchemy.orm import Session


from node.models import NodeModel

from exporter.tasks import value_add
from domain.tasks import put_vm_list
from celery import chain, group


def main():
    db:Session = SessionLocal()
    # task = chain(
    #     group(value_add.si(x=10,y=19), value_add.si(x=10,y=100)), 
    #     group(value_add.s(x=10,y=199), value_add.s(x=10,y=11100))
    # )
    task = put_vm_list.si(node_name="shiori").apply_async()
    print(task.id)

if __name__ == "__main__":
    main()