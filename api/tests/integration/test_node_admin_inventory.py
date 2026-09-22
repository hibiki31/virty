from datetime import timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from mixin.database import SessionLocal
from node.models import NodeModel
from project.models import ProjectModel
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _headers(
    username: str, scopes: list[str], *, projects: list[str] | None = None,
) -> dict[str, str]:
    token = create_access_token(
        data={"sub": username, "scopes": scopes, "projects": projects or []},
        expires_delta=timedelta(minutes=5),
    )
    return {"Authorization": f"Bearer {token}"}


def test_unassigned_nodes_require_explicit_admin_inventory(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    suffix = uuid4().hex
    admin_name = f"node-admin-{suffix}"
    member_name = f"node-member-{suffix}"
    node_name = f"unassigned-{suffix}"
    project_id = suffix[:6]
    ssh_calls: list[str] = []

    class FakeSSH:
        def run_cmd(self, command: str) -> SimpleNamespace:
            ssh_calls.append(command)
            return SimpleNamespace(stdout="診断結果")

    monkeypatch.setattr("node.router.create_ssh_backend", lambda **kwargs: FakeSSH())
    try:
        with SessionLocal.begin() as db:
            admin = UserModel(username=admin_name, hashed_password="unused")
            member = UserModel(username=member_name, hashed_password="unused")
            db.add_all([
                admin,
                member,
                UserScopeModel(user_id=admin_name, name="admin"),
                UserScopeModel(user_id=member_name, name="user"),
                ProjectModel(id=project_id, name="未割当の確認", users=[admin]),
                NodeModel(
                    name=node_name, description="追加直後のnode", domain="node.invalid",
                    user_name="unused", port=22, core=1, memory=1024, cpu_gen="test",
                    os_like="linux", os_name="test", os_version="1", status=10,
                    ansible_facts={"test": "facts"},
                ),
            ])

        headers = _headers(admin_name, ["admin"], projects=[project_id])
        query: dict[str, str | int] = {"nameLike": node_name, "limit": 0}
        normal = api_client.get("/api/nodes", headers=headers, params=query)
        assert normal.status_code == 200
        assert normal.json() == {"count": 0, "data": []}

        inventory = api_client.get(
            "/api/nodes", headers=headers, params={**query, "admin": True},
        )
        assert inventory.status_code == 200, inventory.text
        assert inventory.json()["count"] == 1
        assert inventory.json()["data"][0]["name"] == node_name
        page = api_client.get(
            "/api/nodes", headers=headers,
            params={**query, "admin": True, "limit": 1, "page": 1},
        )
        assert page.json() == {"count": 1, "data": []}
        filtered = api_client.get(
            "/api/nodes", headers=headers,
            params={**query, "admin": True, "projectId": project_id},
        )
        assert filtered.status_code == 200
        assert filtered.json() == {"count": 0, "data": []}
        assert api_client.get(
            "/api/nodes", headers=_headers(admin_name, ["admin"]),
            params={"admin": True, "projectId": project_id},
        ).status_code == 404
        assert api_client.get(
            "/api/nodes", headers=headers,
            params={"admin": True, "projectId": "missing"},
        ).status_code == 404

        endpoints = ["/api/nodes"] + [
            f"/api/nodes/{node_name}{path}" for path in ("", "/facts", "/info")
        ]
        # queryの偽装と、DB/tokenの片方だけがadminである場合を拒否する。
        for denied_headers in (
            _headers(member_name, ["user"]),
            _headers(member_name, ["admin"]),
            _headers(admin_name, ["node.read"]),
        ):
            for endpoint in endpoints:
                assert api_client.get(
                    endpoint, headers=denied_headers, params={"admin": True},
                ).status_code == 403

        for endpoint in endpoints[1:]:
            assert api_client.get(endpoint, headers=headers).status_code == 404
        assert ssh_calls == []

        detail = api_client.get(endpoints[1], headers=headers, params={"admin": True})
        assert detail.status_code == 200
        assert detail.json()["name"] == node_name
        facts = api_client.get(endpoints[2], headers=headers, params={"admin": True})
        assert facts.status_code == 200
        assert facts.json() == {"test": "facts"}
        info = api_client.get(endpoints[3], headers=headers, params={"admin": True})
        assert info.status_code == 200
        assert info.json()["uptime"] == "診断結果"
        assert ssh_calls
        assert api_client.get(
            f"/api/nodes/missing-{suffix}", headers=headers, params={"admin": True},
        ).status_code == 404
    finally:
        with SessionLocal.begin() as db:
            db.query(ProjectModel).filter(ProjectModel.id == project_id).delete()
            db.query(NodeModel).filter(NodeModel.name == node_name).delete()
            db.query(UserModel).filter(
                UserModel.username.in_([admin_name, member_name]),
            ).delete(synchronize_session=False)
