from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from domain.models import DomainModel
from mixin.database import get_db
from task.models import TaskModel

app = APIRouter(prefix="/api/metrics", tags=["metrics"])


@app.get("", response_class=PlainTextResponse)
def get_metrics(
        db: Session = Depends(get_db)
    ):
    vm_metric = db.query(
        func.count(DomainModel.uuid), 
        func.sum(DomainModel.core),
        func.sum(DomainModel.memory),
    ).one()

    task_metric = db.query(
        func.count(TaskModel.uuid),
        func.sum(TaskModel.run_time)
    ).one()

    res = f"""
# TYPE vm_counter counter
vm_counter {vm_metric[0]}
# TYPE vm_cpus gauge
vm_cpus {vm_metric[1]}
# TYPE vm_memorys gauge
vm_memorys {vm_metric[2]}
# TYPE task_counter counter
task_counter {task_metric[0]}
# TYPE task_runtime gauge
task_runtime {task_metric[1]}
"""
    return res