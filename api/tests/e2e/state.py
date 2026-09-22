"""試験用外部adapterの状態をAPIとworkerで共有する。"""

import fcntl
import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from sqlalchemy.engine import make_url


def require_e2e_environment() -> None:
    """実DBを消去する設定やproductionでのtest route起動を拒否する。"""

    if os.getenv("VIRTY_TESTING") != "1" or os.getenv("VIRTY_BACKEND_MODE") != "e2e":
        raise RuntimeError("E2EにはVIRTY_TESTING=1とVIRTY_BACKEND_MODE=e2eが必要です")
    try:
        url = make_url(os.getenv("SQLALCHEMY_DATABASE_URL", ""))
    except Exception:
        raise RuntimeError("E2E専用PostgreSQLの設定が必要です") from None
    if url.get_backend_name() != "postgresql" or url.database != "virty_test_e2e":
        raise RuntimeError("E2Eはvirty_test_e2e専用PostgreSQLだけで実行できます")


def empty_state() -> dict[str, Any]:
    return {"domains": {}, "storages": {}, "networks": {}, "failures": []}


@contextmanager
def locked_state() -> Iterator[dict[str, Any]]:
    """別processからの更新も直列化し、置換で不完全なJSONを残さない。"""

    require_e2e_environment()
    from settings import DATA_ROOT

    root = Path(DATA_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    path = root / "e2e-state.json"
    with (root / "e2e-state.lock").open("a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else empty_state()
        try:
            yield state
        finally:
            # 故障を消費した例外経路でも次回への持越しを防ぐ。
            temporary = root / "e2e-state.tmp"
            temporary.write_text(json.dumps(state), encoding="utf-8")
            temporary.replace(path)
            fcntl.flock(lock, fcntl.LOCK_UN)


def fail_once(state: dict[str, Any], operation: str) -> None:
    if operation in state["failures"]:
        state["failures"].remove(operation)
        raise RuntimeError(f"E2Eで指定した{operation}の失敗")
