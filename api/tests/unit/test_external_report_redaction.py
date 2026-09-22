import hashlib
from types import SimpleNamespace
from typing import Literal, cast
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.external.conftest import (
    create_authenticated_client,
    pytest_runtest_makereport as external_makereport,
)
from tests.external.support.config import EnvConfig
from tests.external.support.task_poller import TaskPollingError, TaskSnapshot


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]
SENSITIVE_VALUE = "report-private-key-and-node.lab.example.test"


def _raise_with_credentials(private_key: str) -> None:
    error = RuntimeError(private_key)
    error.add_note(f"remote stdout: {private_key}")
    raise error


def _redact_report(item: pytest.Item, call: pytest.CallInfo[None]) -> pytest.TestReport:
    report = pytest.TestReport.from_item_and_call(item, call)
    report.sections.append(("Captured stdout call", SENSITIVE_VALUE))
    report.sections.append(("Captured log call", SENSITIVE_VALUE))
    report.user_properties.append(("remote", SENSITIVE_VALUE))
    hook = external_makereport(item, call)
    next(hook)
    with pytest.raises(StopIteration) as result:
        hook.send(report)
    return cast(pytest.TestReport, result.value.value)


@pytest.mark.parametrize("phase", ["setup", "call", "teardown"])
def test_failure_report_keeps_location_and_type_without_credentials(
    request: pytest.FixtureRequest, phase: Literal["setup", "call", "teardown"],
) -> None:
    call = pytest.CallInfo.from_call(
        lambda: _raise_with_credentials(SENSITIVE_VALUE), when=phase,
    )
    original = pytest.TestReport.from_item_and_call(request.node, call)
    assert SENSITIVE_VALUE in original.longreprtext

    report = _redact_report(request.node, call)

    assert report.failed
    assert SENSITIVE_VALUE not in report.longreprtext
    assert "type=RuntimeError" in report.longreprtext
    assert f"phase={phase}" in report.longreprtext
    assert "test_external_report_redaction.py:" in report.longreprtext
    assert "(_raise_with_credentials)" in report.longreprtext
    assert "test_failure_report_keeps_location_and_type_without_credentials" in report.longreprtext
    assert report.sections == []
    assert report.user_properties == []


def test_task_failure_report_keeps_only_safe_ids_and_known_states(request: pytest.FixtureRequest) -> None:
    task_uuid = str(uuid4())

    def fail_task() -> None:
        raise TaskPollingError("reached failure state", {
            task_uuid: TaskSnapshot(uuid=task_uuid, status="error", message=SENSITIVE_VALUE, log=SENSITIVE_VALUE),
            SENSITIVE_VALUE: TaskSnapshot(uuid=SENSITIVE_VALUE, status=SENSITIVE_VALUE),
        })

    report = _redact_report(request.node, pytest.CallInfo.from_call(fail_task, when="call"))

    assert SENSITIVE_VALUE not in report.longreprtext
    assert "type=TaskPollingError" in report.longreprtext
    assert "reached failure state" in report.longreprtext
    safe_id = hashlib.sha256(task_uuid.encode()).hexdigest()[:12]
    assert f"task id={safe_id} status=error" in report.longreprtext


def test_skip_report_removes_dynamic_reason(request: pytest.FixtureRequest) -> None:
    def skip() -> None:
        pytest.skip(SENSITIVE_VALUE)

    report = _redact_report(request.node, pytest.CallInfo.from_call(skip, when="call"))

    assert report.skipped
    assert SENSITIVE_VALUE not in report.longreprtext


def test_external_api_failure_is_an_http_result_without_server_traceback() -> None:
    app = FastAPI()

    @app.get("/api/version")
    def version() -> dict[str, bool]:
        return {"initialized": True}

    @app.post("/api/auth")
    def auth() -> dict[str, str]:
        return {"access_token": "synthetic-test-token"}

    @app.get("/broken")
    def broken() -> None:
        _raise_with_credentials(SENSITIVE_VALUE)

    env = cast(EnvConfig, SimpleNamespace(username="test-admin", password="synthetic-test-password"))
    with TestClient(app, raise_server_exceptions=False) as guest:
        with create_authenticated_client(env, guest) as client:
            response = client.get("/broken")

    assert response.status_code == 500
    assert SENSITIVE_VALUE not in response.text
