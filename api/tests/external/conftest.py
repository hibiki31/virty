"""専用labだけで実行できる破壊的testの安全境界。"""

import os
import shlex
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from tests.external.support.config import (
    EnvConfig,
    InfraConfigError,
    apply_run_prefix,
    derive_resource_name,
    load_infra_config_file,
    validate_infra_config,
    validate_run_id,
)
from tests.external.support.manifest import (
    CleanupPlanner,
    ManifestEntry,
    build_expected_manifest_entries,
    infra_project_id,
    initialize_manifest,
    load_manifest,
    mark_current_entry_removed,
    manifest_path,
)
from tests.external.support.remote_inventory import (
    RemoteInventoryError,
    assert_remote_path_absent,
    delete_manifest_libvirt_target,
    logical_libvirt_name,
    remote_inventory_manager,
)
from tests.external.support.task_poller import wait_for_tasks


def _load_infra_config() -> EnvConfig:
    config_path = os.getenv("VIRTY_INFRA_CONFIG")
    run_id = os.getenv("VIRTY_TEST_RUN_ID", "")
    if not config_path:
        raise pytest.UsageError("VIRTY_INFRA_CONFIGを指定してください")
    try:
        validate_run_id(run_id)
        config = load_infra_config_file(config_path)
        validate_infra_config(config)
        return apply_run_prefix(config, run_id)
    except InfraConfigError as exc:
        raise pytest.UsageError(str(exc)) from None


def _cleanup_marker() -> Path:
    return Path(
        os.getenv(
            "VIRTY_INFRA_CLEANUP_MARKER",
            "/workspace/api/data/infra-cleanup-armed",
        )
    )


def _write_cleanup_marker(path: Path, run_prefix: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(run_prefix)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        os.chmod(path, 0o600)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        temporary.unlink(missing_ok=True)


def _remote_paths(env: EnvConfig, run_prefix: str) -> list[str]:
    return [
        f"/tmp/{run_prefix}-virty-pytest",
        f"/tmp/{run_prefix}-virty-pytest.img",
        f"/tmp/{run_prefix}-virty-copy-source",
        f"/tmp/{run_prefix}-virty-copy-destination",
        f"/var/lib/libvirt/test/{run_prefix}-unit",
        *(storage.path for storage in env.storages),
    ]


def _run_cleanup_tiers(
    planner: CleanupPlanner,
    cleanup_entry: Callable[[ManifestEntry], bool],
) -> bool:
    """同一tierを完遂し、失敗したtierより下位のcleanupを遮断する。"""

    for tier in planner.pending_tiers():
        tier_succeeded = True
        for entry in tier:
            if not cleanup_entry(entry):
                tier_succeeded = False
        if not tier_succeeded:
            return False
    return True


def assert_no_remote_collisions(env: EnvConfig, run_prefix: str) -> None:
    """作成・cleanupを許可する前に、run専用名/pathが未使用だと確認する。"""

    expected_pools = {storage.name for storage in env.storages}
    expected_networks = {network.name for network in env.networks}

    for server_index, server in enumerate(env.servers):
        expected_vms = {
            derive_resource_name(run_prefix, vm.name, server.name)
            for vm in env.vms
        }
        with remote_inventory_manager(
            user=server.username,
            domain=server.domain,
            server_index=server_index,
        ) as manager:
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
                kind = "vm" if label == "VM" else label
                actual = {
                    logical_libvirt_name(kind, raw_name)
                    for raw_name in raw_names.splitlines()
                }
                collision = expected.intersection(actual)
                if collision:
                    raise RemoteInventoryError(
                        "remote collision detected: "
                        f"kind={kind} server_index={server_index} "
                        f"count={len(collision)}"
                    )

            for remote_path in _remote_paths(env, run_prefix):
                result = manager.run_cmd(
                    "if test -e "
                    f"{shlex.quote(remote_path)}; then printf present; fi"
                )
                if result.stdout == "present":
                    raise RemoteInventoryError(
                        "remote collision detected: "
                        f"kind=remote-path server_index={server_index} count=1"
                    )


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
def resource_manifest_guard(env: EnvConfig, run_prefix: str):
    """API/local/remote mutationより前にcollisionとallowlistを固定する。"""

    marker = _cleanup_marker()
    marker.unlink(missing_ok=True)
    assert_no_remote_collisions(env, run_prefix)
    initialize_manifest(
        manifest_path(),
        run_id=run_prefix,
        lab_id=env.lab_id,
        project_id=infra_project_id(),
        entries=build_expected_manifest_entries(
            env,
            run_prefix,
            _remote_paths(env, run_prefix),
        ),
    )
    _write_cleanup_marker(marker, run_prefix)
    yield


@pytest.fixture(scope="session", autouse=True)
def cleanup_run_resources(
    resource_manifest_guard,
    env: EnvConfig,
    client: TestClient,
    run_prefix: str,
    installed_sshkeys,
):
    """全teardownをmanifest plannerの依存順序へ一本化する。"""

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
    from tests.external.fixtures.network import (
        delete_network_target,
        reload_networks,
    )
    from tests.external.fixtures.node import delete_node_target
    from tests.external.fixtures.storage import delete_storage_target
    from tests.external.fixtures.vm import delete_vm_target, reload_vms
    from user.models import UserModel

    failures: list[str] = []
    project_id = infra_project_id()
    manifest = load_manifest(
        manifest_path(),
        expected_run_id=run_prefix,
        expected_lab_id=env.lab_id,
        expected_project_id=project_id,
    )
    planner = CleanupPlanner(manifest)
    server_indexes = {server.name: index for index, server in enumerate(env.servers)}
    servers = {server.name: server for server in env.servers}

    def cleanup(
        label: str,
        entry: ManifestEntry,
        action: Callable[[], None],
    ) -> bool:
        if not planner.allows(entry):
            failures.append(f"{label}: manifest allowlist error")
            return False
        try:
            action()
            mark_current_entry_removed(env, entry)
        except Exception:
            failures.append(f"{label}: cleanup failed")
            return False
        return True

    @contextmanager
    def muted_ansible_logging():
        import module.ansiblelib as ansiblelib

        previous = ansiblelib.logger.disabled
        ansiblelib.logger.disabled = True
        try:
            yield
        finally:
            ansiblelib.logger.disabled = previous

    def cleanup_entry(entry: ManifestEntry) -> bool:
        server_index = server_indexes.get(entry.node) if entry.node is not None else None
        label = (
            f"{entry.kind}[server_index={server_index}]"
            if server_index is not None
            else entry.kind
        )
        if entry.kind == "vm":
            assert entry.node is not None and entry.name is not None

            def delete_vm(entry=entry) -> None:
                mapped_server_index = server_indexes[entry.node or ""]
                server = servers[entry.node or ""]
                try:
                    reload_vms(env, client)
                except Exception:
                    # reload不能でもmanifest exact remote fallbackへ進む。
                    pass
                deleted_uuid = delete_vm_target(
                    client,
                    node_name=entry.node or "",
                    vm_name=entry.name or "",
                    resource_uuid=entry.resource_uuid,
                )
                with remote_inventory_manager(
                    user=server.username,
                    domain=server.domain,
                    server_index=mapped_server_index,
                ) as remote:
                    delete_manifest_libvirt_target(
                        remote,
                        kind="vm",
                        name=entry.name or "",
                        resource_uuid=entry.resource_uuid or deleted_uuid,
                        server_index=mapped_server_index,
                    )

            return cleanup(
                label,
                entry,
                delete_vm,
            )
        elif entry.kind == "network":
            assert entry.node is not None and entry.name is not None

            def delete_network(entry=entry) -> None:
                mapped_server_index = server_indexes[entry.node or ""]
                server = servers[entry.node or ""]
                try:
                    reload_networks(env, client)
                except Exception:
                    # reload不能でもmanifest exact remote fallbackへ進む。
                    pass
                deleted_uuid = delete_network_target(
                    client,
                    node_name=entry.node or "",
                    network_name=entry.name or "",
                    resource_uuid=entry.resource_uuid,
                )
                with remote_inventory_manager(
                    user=server.username,
                    domain=server.domain,
                    server_index=mapped_server_index,
                ) as remote:
                    delete_manifest_libvirt_target(
                        remote,
                        kind="network",
                        name=entry.name or "",
                        resource_uuid=entry.resource_uuid or deleted_uuid,
                        server_index=mapped_server_index,
                    )

            return cleanup(
                label,
                entry,
                delete_network,
            )
        elif entry.kind == "storage":
            assert entry.node is not None and entry.name is not None

            def delete_storage(entry=entry) -> None:
                mapped_server_index = server_indexes[entry.node or ""]
                server = servers[entry.node or ""]
                deleted_uuid = delete_storage_target(
                    client,
                    node_name=entry.node or "",
                    storage_name=entry.name or "",
                    resource_uuid=entry.resource_uuid,
                )
                with remote_inventory_manager(
                    user=server.username,
                    domain=server.domain,
                    server_index=mapped_server_index,
                ) as remote:
                    delete_manifest_libvirt_target(
                        remote,
                        kind="storage",
                        name=entry.name or "",
                        resource_uuid=entry.resource_uuid or deleted_uuid,
                        server_index=mapped_server_index,
                    )

            return cleanup(
                label,
                entry,
                delete_storage,
            )
        elif entry.kind == "remote_path":
            assert entry.node is not None and entry.path is not None
            server = next(
                (server for server in env.servers if server.name == entry.node),
                None,
            )
            if server is None:
                failures.append(f"{label}: server mapping failed")
                return False

            def delete_remote_path(server=server, remote_path=entry.path) -> None:
                with muted_ansible_logging():
                    AnsibleManager(
                        user=server.username,
                        domain=server.domain,
                    ).run(
                        playbook_name="pb_deleteinnode",
                        extravars={
                            "host": f"{server.username}@{server.domain}",
                            "file": remote_path,
                        },
                        timeout=120,
                    )
                with remote_inventory_manager(
                    user=server.username,
                    domain=server.domain,
                    server_index=server_indexes[server.name],
                ) as remote:
                    assert_remote_path_absent(
                        remote,
                        path=remote_path or "",
                        server_index=server_indexes[server.name],
                    )

            return cleanup(label, entry, delete_remote_path)
        elif entry.kind == "project":
            assert entry.name is not None

            def delete_project(name=entry.name) -> None:
                with SessionLocal.begin() as db:
                    db.query(ProjectModel).filter(ProjectModel.name == name).delete(
                        synchronize_session=False
                    )

            return cleanup(label, entry, delete_project)
        elif entry.kind == "node":
            assert entry.name is not None
            return cleanup(
                label,
                entry,
                lambda entry=entry: delete_node_target(
                    client,
                    entry.name or "",
                ),
            )
        elif entry.kind == "user":
            assert entry.name is not None

            def delete_user(name=entry.name) -> None:
                with SessionLocal.begin() as db:
                    db.query(UserModel).filter(UserModel.username == name).delete(
                        synchronize_session=False
                    )

            return cleanup(label, entry, delete_user)

        raise AssertionError("未対応のmanifest resource kindです")

    _run_cleanup_tiers(planner, cleanup_entry)

    if failures:
        pytest.fail("external test資源のcleanupに失敗しました: " + "; ".join(failures))


@pytest.fixture(scope="session")
def gust_client() -> TestClient:
    from main import app

    return TestClient(app)


@pytest.fixture(scope="session")
def client(
    resource_manifest_guard,
    env: EnvConfig,
    gust_client: TestClient,
) -> TestClient:
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
    wait_for_tasks(resp, client, timeout_seconds=timeout)
    return "finish"


pytest_plugins = [
    "tests.external.fixtures.node",
    "tests.external.fixtures.storage",
    "tests.external.fixtures.network",
    "tests.external.fixtures.vm",
]
