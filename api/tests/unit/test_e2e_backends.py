"""全層試験支援が外部接続や架空の成功を生まないことを確認する。"""

import importlib
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError

from module.backends import create_ansible_backend, create_libvirt_backend
from module.xmllib import XmlEditor
from node.models import NodeModel
from tests.e2e.backends import E2EAnsibleBackend, E2ELibvirtBackend, inventory_domain_xml
from tests.e2e.diagnostics import task_diagnostic
from tests.e2e.state import empty_state, locked_state, require_e2e_environment


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]


@pytest.fixture
def e2e_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.setenv("VIRTY_TESTING", "1")
    monkeypatch.setenv("VIRTY_BACKEND_MODE", "e2e")
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URL", "postgresql://test:test@db/virty_test_e2e")
    monkeypatch.setattr("settings.DATA_ROOT", str(tmp_path))
    with locked_state() as state:
        state.update(empty_state())
        state["storages"]["pool"] = {
            "uuid": "pool", "name": "E2E pool", "node_name": "node", "domain": "node.invalid",
            "path": "/e2e/images", "capacity": 100, "available": 90, "allocation": 10,
            "active": True, "auto_start": True, "status": 2,
            "images": [{"name": "template.qcow2", "path": "/e2e/images/template.qcow2", "capacity": 4, "allocation": 1}],
        }
    return tmp_path


@pytest.mark.parametrize(("variable", "value"), [
    ("VIRTY_TESTING", "0"), ("VIRTY_BACKEND_MODE", "production"),
    ("SQLALCHEMY_DATABASE_URL", "postgresql://test:test@db/virty_test_shared"),
    ("SQLALCHEMY_DATABASE_URL", "sqlite:///virty_test_e2e"),
    ("SQLALCHEMY_DATABASE_URL", "invalid-url"),
])
def test_e2e_guard_rejects_non_dedicated_environment(
    e2e_state: Path, monkeypatch: pytest.MonkeyPatch, variable: str, value: str,
) -> None:
    monkeypatch.setenv(variable, value)
    with pytest.raises(RuntimeError):
        require_e2e_environment()


def test_e2e_entrypoint_cannot_load_in_standard_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VIRTY_BACKEND_MODE", "production")
    sys.modules.pop("tests.e2e.app", None)
    with pytest.raises(RuntimeError, match="VIRTY_BACKEND_MODE=e2e"):
        importlib.import_module("tests.e2e.app")


def test_production_routes_have_no_e2e_control() -> None:
    from main import app

    assert all("__e2e" not in getattr(route, "path", "") for route in app.routes)
    assert all("__e2e" not in path for path in app.openapi()["paths"])


def test_reset_checks_actual_connection_before_destructive_sql(
    e2e_state: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    control = importlib.import_module("tests.e2e.app")
    ready_file = e2e_state / "worker.ready"
    ready_file.touch()
    monkeypatch.setenv("VIRTY_WORKER_READY_FILE", str(ready_file))
    session = MagicMock()
    session.get_bind.return_value.engine.url.database = "production"
    session_factory = MagicMock()
    session_factory.begin.return_value.__enter__.return_value = session
    monkeypatch.setattr(control, "SessionLocal", session_factory)
    with pytest.raises(RuntimeError, match="接続先DB"):
        control.reset(control.ResetRequest(seed=False))
    session.execute.assert_not_called()
    with locked_state() as state:
        assert "pool" in state["storages"]


@pytest.mark.parametrize(("code_attribute", "sqlstate"), [("sqlstate", "40P01"), ("pgcode", "55P03"), ("sqlstate", "23505")])
def test_reset_retries_only_lock_conflicts_after_transaction_rollback(
    e2e_state: Path, monkeypatch: pytest.MonkeyPatch, code_attribute: str, sqlstate: str,
) -> None:
    control = importlib.import_module("tests.e2e.app")
    ready_file = e2e_state / "worker.ready"
    ready_file.touch()
    monkeypatch.setenv("VIRTY_WORKER_READY_FILE", str(ready_file))
    failure = MagicMock(spec=Exception)
    setattr(failure, code_attribute, sqlstate)
    database_error = OperationalError("test lock statement", {}, failure)
    session = MagicMock()
    session.get_bind.return_value.engine.url.database = "virty_test_e2e"
    session.execute.side_effect = [None, database_error]
    events: list[str] = []

    @contextmanager
    def transaction() -> Iterator[MagicMock]:
        try:
            yield session
        except Exception:
            events.append("rollback")
            raise
        else:
            events.append("commit")

    factory = MagicMock()
    factory.begin = transaction
    monkeypatch.setattr(control, "SessionLocal", factory)
    if sqlstate in {"40P01", "55P03"}:
        with pytest.raises(HTTPException) as raised:
            control.reset(control.ResetRequest(seed=False))
        assert raised.value.status_code == 409
    else:
        with pytest.raises(OperationalError) as unexpected:
            control.reset(control.ResetRequest(seed=False))
        assert unexpected.value is database_error
    assert events == ["rollback"]
    assert str(session.execute.call_args_list[0].args[0]) == "SET LOCAL lock_timeout = '1s'"
    with locked_state() as state:
        assert "pool" in state["storages"]


def test_vm_copy_definition_and_inventory_survive_adapter_recreation(e2e_state: Path) -> None:
    ansible = create_ansible_backend("unused", "node.invalid")
    assert isinstance(ansible, E2EAnsibleBackend)
    ansible.run("commom/copy_node_internal", {"src": "/e2e/images/template.qcow2", "dst": "/e2e/images/vm.img"})
    ansible.run("vms/qemu_image_resize", {"path": "/e2e/images/vm.img", "size": "12G"})
    libvirt = create_libvirt_backend(NodeModel(name="node"))
    assert isinstance(libvirt, E2ELibvirtBackend)
    xml = '<domain><uuid>vm</uuid><name>vm</name><devices><disk device="disk"><source file="/e2e/images/vm.img"/></disk></devices></domain>'
    libvirt.domain_define(xml)
    libvirt.domain_poweron("vm")

    fresh = E2ELibvirtBackend("node")
    assert fresh.domain_data() == [{"node_name": "node", "xml": inventory_domain_xml(xml), "status": 1, "auto": False}]
    pool = fresh.storages_data("fresh-token")[0]
    assert pool.update_token == "fresh-token"
    assert [(image.name, image.capacity) for image in pool.images] == [("template.qcow2", 4), ("vm.img", 12)]
    assert E2ELibvirtBackend("other-node").domain_data() == []
    assert E2ELibvirtBackend("other-node").storages_data("fresh-token") == []


def test_defined_vm_inventory_uses_libvirt_memory_units_for_real_parser(e2e_state: Path) -> None:
    editor = XmlEditor("static", "domain_base")
    editor.domain_uuid_generate(domain_uuid="vm")
    editor.domain_base_edit(domain_name="e2e-parser-vm", memory_mega_byte=8192, core=2, vnc_port=0)
    backend = E2ELibvirtBackend("node")
    backend.domain_define(editor.dump_str())
    parsed = XmlEditor("str", backend.domain_data()[0]["xml"]).domain_parse()
    assert parsed.memory == 8192
    assert parsed.vcpu == 2
    assert parsed.name == "e2e-parser-vm"


def test_one_shot_failure_persists_consumption_and_has_no_definition(e2e_state: Path) -> None:
    with locked_state() as state:
        state["failures"] = ["domain_define"]
    backend = E2ELibvirtBackend("node")
    xml = "<domain><uuid>vm</uuid><name>vm</name></domain>"
    with pytest.raises(RuntimeError, match="domain_defineの失敗"):
        backend.domain_define(xml)
    assert backend.domain_data() == []
    E2ELibvirtBackend("node").domain_define(xml)
    assert len(backend.domain_data()) == 1


def test_unsupported_and_missing_resource_operations_fail_closed(e2e_state: Path) -> None:
    ansible = E2EAnsibleBackend("node.invalid")
    with pytest.raises(NotImplementedError):
        ansible.run("commom/download_file_in_node")
    with pytest.raises(ValueError, match="copy元"):
        ansible.run("commom/copy_node_internal", {"src": "/missing", "dst": "/e2e/images/vm.img"})
    backend = E2ELibvirtBackend("node")
    with pytest.raises(NotImplementedError):
        backend.storage_define("<pool/>")
    with pytest.raises(ValueError, match="disk"):
        backend.domain_define('<domain><uuid>vm</uuid><name>vm</name><devices><disk device="disk"><source file="/missing"/></disk></devices></domain>')
    assert backend.domain_data() == []


def test_task_diagnostic_omits_messages_sources_and_non_repository_paths(tmp_path: Path) -> None:
    source = tmp_path / "worker.py"
    source.write_text("raise RuntimeError('sensitive-value')\n", encoding="utf-8")
    log = f'''Traceback (most recent call last):
  File "{source}", line 1, in run
    raise RuntimeError('sensitive-value')
  File "/outside/sensitive-host.py", line 2, in run
RuntimeError: password=sensitive-value
sensitive-token-note
'''
    assert task_diagnostic(log, tmp_path) == {
        "exceptionType": "RuntimeError", "frames": [{"file": "worker.py", "line": 1}],
    }
    assert task_diagnostic("secret-token: arbitrary body", tmp_path) == {"exceptionType": None, "frames": []}
