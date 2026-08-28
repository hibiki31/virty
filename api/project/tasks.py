from sqlalchemy.orm import Session

from mixin.log import setup_logger
from task.functions import TaskBase, TaskRequest
from task.models import TaskModel

from .schemas import ProjectForCreate
from .service import create_project_with_members, ensure_project_deletable

worker_task = TaskBase()
logger = setup_logger(__name__)


@worker_task(key="post.project.root")
def post_project_root(db: Session, model: TaskModel, req: TaskRequest) -> None:
    body = ProjectForCreate.model_validate(req.body)
    project = create_project_with_members(
        db,
        name=body.name,
        member_ids=body.member_ids,
    )
    db.commit()
    model.message = f"Project {project.id}を作成しました"


@worker_task(key="delete.project.root")
def delete_project_root(db: Session, model: TaskModel, req: TaskRequest) -> None:
    project_id = str(req.path_param["project_id"])
    project = ensure_project_deletable(db, project_id, lock=True)
    db.delete(project)
    db.commit()
    model.message = "Projectを削除しました"
