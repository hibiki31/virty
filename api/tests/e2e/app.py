"""試験専用controlを持ち、production appをそのままmountするentrypoint。"""

import os
from datetime import timedelta
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from tests.e2e.state import empty_state, locked_state, require_e2e_environment

# mainのimportより前に検査し、production設定では起動させない。
require_e2e_environment()

from auth.router import create_access_token  # noqa: E402
from main import app as production_app  # noqa: E402
from main import lifespan  # noqa: E402
from mixin.database import Base, SessionLocal  # noqa: E402
from settings import APP_ROOT  # noqa: E402
from task.models import TaskModel  # noqa: E402
from tests.e2e.diagnostics import TaskDiagnostic, task_diagnostic  # noqa: E402
from tests.e2e.fixtures import MANIFEST, seed_database  # noqa: E402
from user.models import UserModel  # noqa: E402


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)


class ResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seed: bool = True


class FailureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: Literal["domain_define", "domain_data", "domain_power", "storages_data", "ansible.run"]


class ExpiredTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str


def require_worker_ready() -> None:
    ready_file = os.getenv("VIRTY_WORKER_READY_FILE")
    if not ready_file or not Path(ready_file).is_file():
        raise HTTPException(status_code=409, detail="E2E workerの起動準備が完了していません")


@app.get("/api/__e2e/ready")
def ready() -> dict[str, bool]:
    require_e2e_environment()
    require_worker_ready()
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"ready": True}


@app.post("/api/__e2e/reset")
def reset(request: ResetRequest) -> dict[str, Any]:
    require_e2e_environment()
    require_worker_ready()
    try:
        with SessionLocal.begin() as db:
            if db.get_bind().engine.url.database != "virty_test_e2e":
                raise RuntimeError("E2E resetの接続先DBが専用DBと一致しません")
            # 終了直前の認証済みpollはusers→tasksの順でlockを取るため有限時間で譲る。
            db.execute(text("SET LOCAL lock_timeout = '1s'"))
            # schedulerがstatusを読むtransactionと排他し、実行中taskを消さない。
            db.execute(text('LOCK TABLE tasks IN ACCESS EXCLUSIVE MODE'))
            active = db.query(TaskModel).filter(TaskModel.status.notin_(("finish", "error", "lost", "cancelled"))).first()
            if active is not None:
                raise HTTPException(status_code=409, detail="E2E workerに未完了taskがあります")
            tables = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
            db.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))
            fixture = seed_database(db) if request.seed else empty_state()
            db.flush()
            with locked_state() as state:
                state.clear()
                state.update(fixture)
    except DBAPIError as exc:
        # begin contextを抜けてrollbackした後でのみ、競合を再試行可能にする。
        sqlstate = getattr(exc.orig, "sqlstate", None) or getattr(exc.orig, "pgcode", None)
        if sqlstate in {"40P01", "55P03"}:
            raise HTTPException(status_code=409, detail="E2E APIの処理完了を待って初期化を再試行してください") from None
        raise
    return MANIFEST


@app.post("/api/__e2e/failure")
def failure(request: FailureRequest) -> dict[str, str]:
    with locked_state() as state:
        state["failures"].append(request.operation)
    return {"operation": request.operation}


@app.post("/api/__e2e/expired-token")
def expired_token(request: ExpiredTokenRequest, response: Response) -> dict[str, str]:
    require_e2e_environment()
    with SessionLocal() as db:
        user = db.get(UserModel, request.username)
        if user is None:
            raise HTTPException(status_code=404, detail="E2E利用者がありません")
        token = create_access_token({"sub": user.username, "scopes": [scope.name for scope in user.scopes], "projects": [project.id for project in user.projects], "session_generation": user.session_generation}, timedelta(seconds=-1))
    response.headers["Cache-Control"] = "no-store"
    return {"access_token": token}


@app.get("/api/__e2e/tasks/{uuid}/diagnostic")
def task_failure_diagnostic(uuid: str, response: Response) -> TaskDiagnostic:
    require_e2e_environment()
    with SessionLocal() as db:
        task = db.get(TaskModel, uuid)
        if task is None:
            raise HTTPException(status_code=404, detail="E2E taskがありません")
        result = task_diagnostic(task.log, Path(APP_ROOT))
    response.headers["Cache-Control"] = "no-store"
    return result


app.mount("/", production_app)
