from storage.tasks import update_storage_list
from network.tasks import update_network_list
from mixin.database import SessionLocal
from task.models import TaskModel


def dev_update_storage_list():
    db = SessionLocal()
    update_storage_list(db=db, model=TaskModel())

def dev_update_network_list():
    db = SessionLocal()
    update_network_list(db=db, model=TaskModel())


if __name__ == "__main__":
    dev_update_network_list()