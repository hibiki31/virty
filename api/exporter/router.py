
from io import StringIO
from typing import Iterable

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from domain.models import DomainModel
from mixin.database import get_db
from task.models import TaskModel

app = APIRouter(prefix="/api/metrics", tags=["metrics"])


class Metric(BaseModel):
    label: dict | None = None
    value: str | int | float
    
    def __init__(self, **data):
        # Noneのvalueを0に変換して共通化
        if "value" in data and data["value"] is None:
            data["value"] = 0
        super().__init__(**data)


class ExpoterEditor():
    def __init__(self) -> None:
        self._buffer: StringIO = StringIO()

    def metric(self,name: str, type: str, help_: str = "Virty Metrics", values: Iterable[Metric] | None = None) -> None:
        """Append a counter metric block to the internal buffer."""
        values = tuple(values or ())
        self._write_header(name, help_, type)
        for metric in values:
            self._buffer.write(f"{name}{self._format_labels(metric.label)} {metric.value}\n")

    def render(self) -> str:
        """Return the accumulated metrics text and reset the buffer."""
        text = self._buffer.getvalue()
        self._buffer.seek(0)
        self._buffer.truncate(0)
        return text

    def _write_header(self, name: str, help_: str, mtype: str) -> None:
        self._buffer.write(f"# HELP {name} {help_}\n")
        self._buffer.write(f"# TYPE {name} {mtype}\n")

    @staticmethod
    def _format_labels(labels: dict[str, str] | None) -> str:
        """Return `{k="v", ...}` or empty string when labels is falsy."""
        if not labels:
            return ""
        joined = ",".join(f'{k}="{v}"' for k, v in labels.items())
        return f"{{{joined}}}"
                
                
        


@app.get(
    "",
    response_class=PlainTextResponse,
    responses={
        200: {
            "content": {"text/plain": {"example": "# HELP virty_vm_len Virty Metrics\n# TYPE virty_vm_len gauge\nvirty_vm_len 10\n# HELP virty_vm_cpus Virty Metrics\n# TYPE virty_vm_cpus gauge\nvirty_vm_cpus 4\n# HELP virty_vm_memorys Virty Metrics\n# TYPE virty_vm_memorys gauge\nvirty_vm_memorys 8192\n# HELP virty_task_counter Virty Metrics\n# TYPE virty_task_counter counter\nvirty_task_counter 5\n# HELP virty_task_runtime Virty Metrics\n# TYPE virty_task_runtime counter\nvirty_task_runtime 12345\n# HELP virty_task_summry Virty Metrics\n# TYPE virty_task_summry counter\nvirty_task_summry{status=\"finish\"} 42\nvirty_task_summry{status=\"init\"} 13\nvirty_task_summry{status=\"start\"} 7\n"}}
        }
    }
)
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
    
    stmt = (
    select(
        TaskModel.status,
        func.count(TaskModel.uuid).label("count")  # カラム名を明示したい場合は label()
    )
    .group_by(TaskModel.status)
    )

    results = db.execute(stmt).all()
    # 返り値の例: [('finish', 42), ('init', 13), ('start', 7)]
    
    

    ex = ExpoterEditor()
    ex.metric("virty_vm_len", "gauge",values=[Metric(value=vm_metric[0])])
    ex.metric("virty_vm_cpus", "gauge",values=[Metric(value=vm_metric[1])])
    ex.metric("virty_vm_memorys", "gauge",values=[Metric(value=vm_metric[2])])
    
    ex.metric("virty_task_counter", "counter",values=[Metric(value=task_metric[0])])
    ex.metric("virty_task_runtime", "counter",values=[Metric(value=task_metric[1])])

    ex.metric("virty_task_summry", "counter",values=[
        Metric(value=result[1], label={"status": result[0]}) for result in results
    ])

    return ex.render()
