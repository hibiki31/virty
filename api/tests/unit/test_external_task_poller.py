from collections import defaultdict
from uuid import UUID, uuid4

import pytest

from tests.external.support.task_poller import TaskPollingError, wait_for_tasks


pytestmark = [pytest.mark.unit, pytest.mark.timeout(10)]


class FakeResponse:
    def __init__(self, payload, error: Exception | None = None):
        self.payload = payload
        self.error = error

    def raise_for_status(self) -> None:
        if self.error is not None:
            raise self.error

    def json(self):
        return self.payload


class SequenceClient:
    def __init__(self, payloads: dict[str, list[dict[str, object]]]):
        self.payloads = {key: list(values) for key, values in payloads.items()}
        self.calls: defaultdict[str, int] = defaultdict(int)

    def get(self, path: str) -> FakeResponse:
        task_uuid = path.rsplit("/", 1)[-1]
        self.calls[task_uuid] += 1
        values = self.payloads[task_uuid]
        value = values.pop(0) if len(values) > 1 else values[0]
        return FakeResponse(value)


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += seconds


def _enqueue(*task_uuids: str) -> FakeResponse:
    return FakeResponse([{"uuid": task_uuid} for task_uuid in task_uuids])


def _snapshot(task_uuid: str, status: str, **extra: str) -> dict[str, object]:
    return {"uuid": task_uuid, "status": status, **extra}


def test_waits_for_multiple_tasks_with_one_shared_deadline() -> None:
    first = str(uuid4())
    second = str(uuid4())
    client = SequenceClient(
        {
            first: [_snapshot(first, "start"), _snapshot(first, "finish")],
            second: [_snapshot(second, "wait"), _snapshot(second, "finish")],
        }
    )
    clock = FakeClock()

    snapshots = wait_for_tasks(
        _enqueue(first, second),
        client,
        timeout_seconds=5,
        poll_interval=1,
        clock=clock,
        sleep=clock.sleep,
    )

    assert [snapshot.uuid for snapshot in snapshots] == [first, second]
    assert [snapshot.status for snapshot in snapshots] == ["finish", "finish"]


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {},
        [{"uuid": ""}],
        [{"uuid": "not-a-uuid"}],
    ],
)
def test_rejects_empty_or_malformed_enqueue_payload(payload) -> None:
    with pytest.raises(TaskPollingError):
        wait_for_tasks(FakeResponse(payload), SequenceClient({}))


def test_rejects_duplicate_uuid_after_normalization() -> None:
    task_uuid = uuid4()
    uppercase = str(task_uuid).upper()
    assert UUID(uppercase) == task_uuid

    with pytest.raises(TaskPollingError, match="duplicated"):
        wait_for_tasks(_enqueue(str(task_uuid), uppercase), SequenceClient({}))


def test_http_error_is_wrapped_without_original_body_or_cause() -> None:
    secret_seed = "credential-bearing-response-body"
    with pytest.raises(TaskPollingError) as caught:
        wait_for_tasks(
            FakeResponse({}, RuntimeError(secret_seed)),
            SequenceClient({}),
        )

    assert secret_seed not in str(caught.value)
    assert caught.value.__cause__ is None


@pytest.mark.parametrize("status", ["error", "lost", "cancelled", "unknown"])
def test_failure_state_keeps_details_off_display(status: str) -> None:
    task_uuid = str(uuid4())
    secret_seed = "sensitive-worker-log"
    client = SequenceClient(
        {
            task_uuid: [
                _snapshot(task_uuid, status, message=secret_seed, log=secret_seed)
            ]
        }
    )

    with pytest.raises(TaskPollingError) as caught:
        wait_for_tasks(_enqueue(task_uuid), client)

    assert secret_seed not in str(caught.value)
    assert task_uuid not in str(caught.value)
    assert caught.value.snapshots[task_uuid].log == secret_seed


@pytest.mark.parametrize("status", ["reconciling", "cancel_requested"])
def test_known_inflight_status_continues_polling(status: str) -> None:
    task_uuid = str(uuid4())
    client = SequenceClient(
        {task_uuid: [_snapshot(task_uuid, status), _snapshot(task_uuid, "finish")]}
    )

    snapshots = wait_for_tasks(_enqueue(task_uuid), client, poll_interval=0.01)

    assert snapshots[0].status == "finish"


def test_timeout_reports_safe_state_and_is_finite() -> None:
    task_uuid = str(uuid4())
    client = SequenceClient({task_uuid: [_snapshot(task_uuid, "start")]})
    clock = FakeClock()

    with pytest.raises(TaskPollingError, match="timed out"):
        wait_for_tasks(
            _enqueue(task_uuid),
            client,
            timeout_seconds=2,
            poll_interval=0.5,
            clock=clock,
            sleep=clock.sleep,
        )

    assert clock.value == 2


def test_task_response_identity_must_match_requested_uuid() -> None:
    task_uuid = str(uuid4())
    other_uuid = str(uuid4())
    client = SequenceClient({task_uuid: [_snapshot(other_uuid, "finish")]})

    with pytest.raises(TaskPollingError, match="identity"):
        wait_for_tasks(_enqueue(task_uuid), client)
