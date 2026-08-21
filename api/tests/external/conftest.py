"""専用labだけで実行できる破壊的testの安全境界。"""

import json
import os
import re
import shlex
import time
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str
    publickey: str


class Project(BaseModel):
    name: str


class Server(BaseModel):
    name: str
    domain: str
    username: str


class Storage(BaseModel):
    name: str
    path: str


class Networks(BaseModel):
    name: str
    type: str
    octet: int


class VM(BaseModel):
    name: str
    image: str
    network: str


class EnvConfig(BaseModel):
    allow_destructive: bool
    lab_id: str
    username: str
    password: str
    users: list[User]
    projects: list[Project]
    key: str
    pub: str
    servers: list[Server]
    storages: list[Storage]
    networks: list[Networks]
    vms: list[VM]
    image_url: str
    iso_url: str


def _load_infra_config() -> EnvConfig:
    config_path = os.getenv("VIRTY_INFRA_CONFIG")
    run_id = os.getenv("VIRTY_TEST_RUN_ID", "")
    if not config_path:
        raise pytest.UsageError("VIRTY_INFRA_CONFIGを指定してください")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{5,31}", run_id):
        raise pytest.UsageError("VIRTY_TEST_RUN_IDは6〜32文字の小文字英数字と'-'で指定してください")

    path = Path(config_path)
    if not path.is_file():
        raise pytest.UsageError(f"専用lab設定が存在しません: {path}")
    try:
        config = EnvConfig.model_validate_json(path.read_text(encoding="utf-8"))
        validate_infra_config(config)
    except (OSError, ValueError) as exc:
        raise pytest.UsageError(f"専用lab設定が不正です: {exc}") from exc
    return _apply_run_prefix(config, run_id)


def validate_infra_config(config: EnvConfig) -> None:
    """資源作成前に、external suiteが暗黙に要求する設定を検証する。"""

    if config.allow_destructive is not True or not config.lab_id.strip():
        raise ValueError("allow_destructive=trueかつlab_id付きの専用lab設定が必要です")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", config.lab_id):
        raise ValueError("lab_idの形式が不正です")

    collections = {
        "servers": config.servers,
        "storages": config.storages,
        "networks": config.networks,
        "vms": config.vms,
        "users": config.users,
        "projects": config.projects,
    }
    for label, resources in collections.items():
        if not resources:
            raise ValueError(f"{label}を1件以上指定してください")
        names = [resource.name if hasattr(resource, "name") else resource.username for resource in resources]
        if len(names) != len(set(names)):
            raise ValueError(f"{label}の名前は重複できません")

    for suffix in ("test-cloud", "test-iso", "test-img"):
        if not any(storage.name.endswith(suffix) for storage in config.storages):
            raise ValueError(f"storagesに末尾{suffix!r}の定義が必要です")
    if not any(network.name.endswith("test-nat") for network in config.networks):
        raise ValueError("networksに末尾'test-nat'の定義が必要です")
    if any(not PurePosixPath(storage.path).is_absolute() for storage in config.storages):
        raise ValueError("storage pathは管理node上の絶対pathで指定してください")

    for label, url in {
        "image_url": config.image_url,
        "iso_url": config.iso_url,
    }.items():
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"{label}はhttp(s)の絶対URLで指定してください")
    if not config.key.strip() or not config.pub.strip():
        raise ValueError("keyとpubを空にできません")


def _apply_run_prefix(config: EnvConfig, run_id: str) -> EnvConfig:
    """同じ専用lab内でtest資源名とpathをrunごとに分離する。"""

    config.username = f"{run_id}-{config.username}"
    for resource in [*config.projects, *config.servers, *config.storages, *config.networks, *config.vms]:
        resource.name = f"{run_id}-{resource.name}"
    for user in config.users:
        user.username = f"{run_id}-{user.username}"
    for storage in config.storages:
        path = PurePosixPath(storage.path)
        storage.path = str(path.with_name(f"{run_id}-{path.name}"))
    return config


def _cleanup_marker() -> Path:
    return Path(
        os.getenv(
            "VIRTY_INFRA_CLEANUP_MARKER",
            "/workspace/api/data/infra-cleanup-armed",
        )
    )


def _remote_paths(env: EnvConfig, run_prefix: str) -> list[str]:
    return [
        f"/tmp/{run_prefix}-virty-pytest",
        f"/tmp/{run_prefix}-virty-pytest.img",
        f"/tmp/{run_prefix}-virty-copy-source",
        f"/tmp/{run_prefix}-virty-copy-destination",
        f"/var/lib/libvirt/test/{run_prefix}-unit",
        *(storage.path for storage in env.storages),
    ]


def assert_no_remote_collisions(env: EnvConfig, run_prefix: str) -> None:
    """作成・cleanupを許可する前に、run専用名/pathが未使用だと確認する。"""

    from module.paramikolib import ParamikoManager

    expected_pools = {storage.name for storage in env.storages}
    expected_networks = {network.name for network in env.networks}

    for server in env.servers:
        expected_vms = {f"{vm.name}-{server.name}" for vm in env.vms}
        manager = ParamikoManager(
            user=server.username,
            domain=server.domain,
            port=22,
        )
        try:
            inventories = {
                "storage": (
                    expected_pools,
                    manager.run_cmd("virsh pool-list --all --name").stdout,
                ),
                "network": (
                    expected_networks,
                    manager.run_cmd("virsh net-list --all --name").stdout,
                ),
                "VM": (
                    expected_vms,
                    manager.run_cmd("virsh list --all --name").stdout,
                ),
            }
            for label, (expected, raw_names) in inventories.items():
                collision = expected.intersection(raw_names.splitlines())
                if collision:
                    raise RuntimeError(
                        f"既存{label}とrun IDが衝突しています: "
                        f"{server.name}/{sorted(collision)}"
                    )

            for remote_path in _remote_paths(env, run_prefix):
                result = manager.run_cmd(
                    "if test -e "
                    f"{shlex.quote(remote_path)}; then printf present; fi"
                )
                if result.stdout == "present":
                    raise RuntimeError(
                        "既存remote pathとrun IDが衝突しています: "
                        f"{server.name}:{remote_path}"
                    )
        finally:
            manager.close()


def pytest_sessionstart(session: pytest.Session) -> None:
    session.config._virty_infra_config = _load_infra_config()


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        item.add_marker(pytest.mark.external)
        # signal方式ならtimeout時にもfixture finalizerでrun資源を回収できる。
        item.add_marker(pytest.mark.timeout(1200, method="signal"))


@pytest.fixture(scope="session")
def env(request: pytest.FixtureRequest) -> EnvConfig:
    return request.config._virty_infra_config


@pytest.fixture(scope="session")
def run_prefix() -> str:
    return os.environ["VIRTY_TEST_RUN_ID"]


@pytest.fixture(scope="session", autouse=True)
def cleanup_run_resources(
    env: EnvConfig,
    client: TestClient,
    run_prefix: str,
    installed_sshkeys,
):
    """失敗・中断後も、このrunが作成した専用lab資源だけを後始末する。"""

    marker = _cleanup_marker()
    marker.unlink(missing_ok=True)
    assert_no_remote_collisions(env, run_prefix)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(run_prefix, encoding="utf-8")
    yield

    cleanup_resources(env, client, run_prefix)


def cleanup_resources(
    env: EnvConfig,
    client: TestClient,
    run_prefix: str,
) -> None:
    """run IDに一致するlocal/remote資源を依存関係の逆順で削除する。"""

    from mixin.database import SessionLocal
    from module.ansiblelib import AnsibleManager
    from project.models import ProjectModel
    from tests.external.fixtures.network import delete_network
    from tests.external.fixtures.node import delete_node
    from tests.external.fixtures.storage import delete_storage
    from tests.external.fixtures.vm import delete_vm
    from user.models import UserModel

    failures: list[str] = []

    def cleanup(label: str, action) -> None:
        try:
            action()
        except Exception as exc:
            failures.append(f"{label}: {exc}")

    # 依存関係の逆順で削除する。nodeは最後まで接続先として保持する。
    cleanup("VM", lambda: delete_vm(env, client, skipp=True))
    cleanup("network", lambda: delete_network(env, client, skipp=True))
    cleanup("storage", lambda: delete_storage(env, client, skipp=True))

    remote_paths = _remote_paths(env, run_prefix)
    for server in env.servers:
        for remote_path in remote_paths:
            cleanup(
                f"remote path {server.name}:{remote_path}",
                lambda server=server, remote_path=remote_path: AnsibleManager(
                    user=server.username,
                    domain=server.domain,
                ).run(
                    playbook_name="pb_deleteinnode",
                    extravars={
                        "host": f"{server.username}@{server.domain}",
                        "file": remote_path,
                    },
                    timeout=120,
                ),
            )

    def cleanup_projects() -> None:
        with SessionLocal.begin() as db:
            db.query(ProjectModel).filter(
                ProjectModel.name.startswith(f"{run_prefix}-")
            ).delete(synchronize_session=False)

    def cleanup_users() -> None:
        with SessionLocal.begin() as db:
            db.query(UserModel).filter(
                UserModel.username.startswith(f"{run_prefix}-")
            ).delete(synchronize_session=False)

    cleanup("project", cleanup_projects)
    cleanup("node", lambda: delete_node(env, client))
    cleanup("user", cleanup_users)

    if failures:
        pytest.fail("external test資源のcleanupに失敗しました: " + "; ".join(failures))
    _cleanup_marker().unlink(missing_ok=True)


@pytest.fixture(scope="session")
def gust_client() -> TestClient:
    from main import app

    return TestClient(app)


@pytest.fixture(scope="session")
def client(env: EnvConfig, gust_client: TestClient) -> TestClient:
    return create_authenticated_client(env, gust_client)


def create_authenticated_client(
    env: EnvConfig,
    guest_client: TestClient | None = None,
) -> TestClient:
    if guest_client is None:
        from main import app

        guest_client = TestClient(app)

    req_data = {"username": env.username, "password": env.password}
    if not guest_client.get("/api/version").json()["initialized"]:
        guest_client.post("/api/auth/setup", json=req_data)
    resp = guest_client.post("/api/auth", data=req_data)
    resp.raise_for_status()
    return TestClient(
        guest_client.app,
        headers={
            "Authorization": f"Bearer {resp.json()['access_token']}",
            "Content-Type": "application/json",
        },
    )


def wait_tasks(resp: Any, client: TestClient) -> str:
    timeout = float(os.getenv("VIRTY_EXTERNAL_TASK_TIMEOUT_SECONDS", "900"))
    deadline = time.monotonic() + timeout
    for task in resp.json():
        uuid = task["uuid"]
        last_task: dict[str, Any] = {}
        while time.monotonic() < deadline:
            task_response = client.get(f"/api/tasks/{uuid}")
            task_response.raise_for_status()
            last_task = task_response.json()
            status = last_task["status"]
            if status in {"error", "lost"}:
                raise RuntimeError(
                    f"task uuid={uuid}, status={status}, "
                    f"message={last_task.get('message')}, log={last_task.get('log')}"
                )
            if status == "finish":
                break
            time.sleep(0.5)
        else:
            raise TimeoutError(
                f"taskが{timeout:.0f}秒以内に完了しませんでした: "
                f"uuid={uuid}, status={last_task.get('status')}, "
                f"message={last_task.get('message')}, log={last_task.get('log')}"
            )
    return "finish"


pytest_plugins = [
    "tests.external.fixtures.node",
    "tests.external.fixtures.storage",
    "tests.external.fixtures.network",
    "tests.external.fixtures.vm",
]
