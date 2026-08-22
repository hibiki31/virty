from types import SimpleNamespace
from typing import Any

import httpx
import pytest

# SQLAlchemy relationship名を解決するため、全modelを先に登録する。
import models as _all_models  # noqa: F401
from network import tasks
from task.schemas import TaskRequest


class _Query:
    def __init__(self, *, network_node: Any, overlay_nodes: list[Any]) -> None:
        self.network_node = network_node
        self.overlay_nodes = overlay_nodes

    def filter(self, *_: object) -> "_Query":
        return self

    def order_by(self, *_: object) -> "_Query":
        return self

    def one(self) -> Any:
        return self.network_node

    def all(self) -> list[Any]:
        return self.overlay_nodes


class _Database:
    def __init__(self, *, network_node: Any, overlay_nodes: list[Any]) -> None:
        self.network_node = network_node
        self.overlay_nodes = overlay_nodes

    def query(self, *_: object) -> _Query:
        return _Query(
            network_node=self.network_node,
            overlay_nodes=self.overlay_nodes,
        )


def _node(name: str, domain: str, *, extra: dict[str, str]) -> Any:
    return SimpleNamespace(
        name=name,
        domain=domain,
        roles=[SimpleNamespace(role_name="vxlan_overlay", extra_json=extra)],
    )


def test_provider_network_uses_request_body_and_each_worker_role_extra(
    monkeypatch: Any,
) -> None:
    network_node = _node(
        "network-node",
        "network-node.internal",
        extra={"local_ip": "192.0.2.1", "network_node_ip": "198.51.100.1"},
    )
    worker_a = _node(
        "worker-a",
        "worker-a.internal",
        extra={"local_ip": "192.0.2.10", "network_node_ip": "198.51.100.10"},
    )
    worker_b = _node(
        "worker-b",
        "worker-b.internal",
        extra={"local_ip": "192.0.2.20", "network_node_ip": "198.51.100.20"},
    )
    db = _Database(
        network_node=network_node,
        overlay_nodes=[network_node, worker_a, worker_b],
    )
    defined_on: list[str] = []
    posts: list[tuple[str, dict[str, Any], float]] = []

    class _VirtManager:
        def __init__(self, *, node_model: Any) -> None:
            self.node_model = node_model

        def network_define(self, *, xml_str: str) -> None:
            assert xml_str == "<network/>"
            defined_on.append(self.node_model.name)

    class _XmlEditor:
        def __init__(self, *_: object) -> None:
            pass

        def network_provider(self, **_: object) -> None:
            pass

        def network_internal(self, **_: object) -> None:
            pass

        @staticmethod
        def dump_str() -> str:
            return "<network/>"

    monkeypatch.setattr(tasks, "randint", lambda *_: 0x123456)
    monkeypatch.setattr(
        tasks,
        "create_libvirt_backend",
        lambda *, node_model: _VirtManager(node_model=node_model),
    )
    monkeypatch.setattr(tasks.xmllib, "XmlEditor", _XmlEditor)
    def post(*, url: str, json: dict[str, Any], timeout: float) -> httpx.Response:
        posts.append((url, json, timeout))
        return httpx.Response(204, request=httpx.Request("POST", url))

    monkeypatch.setattr(tasks.httpx, "post", post)

    tasks.post_network_provider(
        db,
        SimpleNamespace(),
        TaskRequest(
            path_param={},
            body={
                "name": "provider-a",
                "dnsDomain": "example.internal",
                "networkAddress": "198.51.100.0",
                "networkPrefix": "24",
                "gatewayAddress": "198.51.100.1",
                "dhcpStart": "198.51.100.100",
                "dhcpEnd": "198.51.100.200",
                "networkNode": "network-node",
            },
        ),
    )

    assert defined_on == ["network-node", "worker-a", "worker-b"]
    assert posts == [
        (
            "http://network-node.internal:8766/vxlan",
            {"vni": 0x123456, "node_id": 0, "remote_ip": "192.0.2.10"},
            tasks.NETWORK_PROVIDER_HTTP_TIMEOUT_SECONDS,
        ),
        (
            "http://network-node.internal:8766/vxlan",
            {"vni": 0x123456, "node_id": 1, "remote_ip": "192.0.2.20"},
            tasks.NETWORK_PROVIDER_HTTP_TIMEOUT_SECONDS,
        ),
        (
            "http://worker-a.internal:8766/vxlan",
            {"vni": 0x123456, "node_id": 0, "remote_ip": "198.51.100.10"},
            tasks.NETWORK_PROVIDER_HTTP_TIMEOUT_SECONDS,
        ),
        (
            "http://worker-b.internal:8766/vxlan",
            {"vni": 0x123456, "node_id": 0, "remote_ip": "198.51.100.20"},
            tasks.NETWORK_PROVIDER_HTTP_TIMEOUT_SECONDS,
        ),
    ]


def test_provider_network_rejects_failed_internal_http_response(
    monkeypatch: Any,
) -> None:
    network_node = _node(
        "network-node",
        "network-node.internal",
        extra={"local_ip": "192.0.2.1", "network_node_ip": "198.51.100.1"},
    )
    worker = _node(
        "worker-a",
        "worker-a.internal",
        extra={"local_ip": "192.0.2.10", "network_node_ip": "198.51.100.10"},
    )
    db = _Database(
        network_node=network_node,
        overlay_nodes=[network_node, worker],
    )
    defined_on: list[str] = []

    class _VirtManager:
        def __init__(self, *, node_model: Any) -> None:
            self.node_model = node_model

        def network_define(self, *, xml_str: str) -> None:
            assert xml_str == "<network/>"
            defined_on.append(self.node_model.name)

    class _XmlEditor:
        def __init__(self, *_: object) -> None:
            pass

        def network_provider(self, **_: object) -> None:
            pass

        def network_internal(self, **_: object) -> None:
            pass

        @staticmethod
        def dump_str() -> str:
            return "<network/>"

    def post(*, url: str, json: dict[str, Any], timeout: float) -> httpx.Response:
        assert json == {
            "vni": 0x123456,
            "node_id": 0,
            "remote_ip": "192.0.2.10",
        }
        assert timeout == tasks.NETWORK_PROVIDER_HTTP_TIMEOUT_SECONDS
        return httpx.Response(500, request=httpx.Request("POST", url))

    monkeypatch.setattr(tasks, "randint", lambda *_: 0x123456)
    monkeypatch.setattr(
        tasks,
        "create_libvirt_backend",
        lambda *, node_model: _VirtManager(node_model=node_model),
    )
    monkeypatch.setattr(tasks.xmllib, "XmlEditor", _XmlEditor)
    monkeypatch.setattr(tasks.httpx, "post", post)

    with pytest.raises(httpx.HTTPStatusError):
        tasks.post_network_provider(
            db,
            SimpleNamespace(),
            TaskRequest(
                path_param={},
                body={
                    "name": "provider-a",
                    "dnsDomain": "example.internal",
                    "networkAddress": "198.51.100.0",
                    "networkPrefix": "24",
                    "gatewayAddress": "198.51.100.1",
                    "dhcpStart": "198.51.100.100",
                    "dhcpEnd": "198.51.100.200",
                    "networkNode": "network-node",
                },
            ),
        )

    # network nodeへの定義後に失敗しているため、workerは結果不明として扱う。
    assert defined_on == ["network-node"]
