from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from domain.models import DomainModel
from flavor.models import FlavorModel
from mixin.database import SessionLocal
from network.models import NetworkModel, NetworkPoolModel, NetworkPortgroupModel
from node.models import NodeModel
from project.models import ProjectModel
from storage.models import AssociationStoragePoolModel, ImageModel, StorageModel, StoragePoolModel
from task.functions import TaskManager
from task.models import TaskModel
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _headers(username: str, scopes: list[str], projects: list[str] | None = None) -> dict[str, str]:
    token = create_access_token(
        {"sub": username, "scopes": scopes, "projects": projects or []},
        timedelta(minutes=5),
    )
    return {"Authorization": f"Bearer {token}"}


def test_admin_inventory_covers_all_resources_and_preserves_project_boundaries(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    suffix = uuid4().hex
    prefix = f"inventory-{suffix}"
    admin_name, member_name = f"admin-{suffix}", f"member-{suffix}"
    project_id = suffix[:6]
    nodes = [f"{prefix}-{index}" for index in range(2)]
    storage_ids = [str(uuid4()) for _ in range(2)]
    network_ids = [str(uuid4()) for _ in range(2)]
    vm_ids = [str(uuid4()) for _ in range(2)]
    task_id = str(uuid4())
    monkeypatch.setattr("domain.router.DATA_ROOT", str(tmp_path))
    monkeypatch.setattr("network.router.DATA_ROOT", str(tmp_path))
    original_commit = TaskManager.commit

    def hold_task(manager: TaskManager, *args: Any, **kwargs: Any) -> TaskModel:
        # downloadの受付だけを検査し、verify workerによる外部処理を防ぐ。
        kwargs["commit_transaction"] = False
        task = original_commit(manager, *args, **kwargs)
        task.status = "test-held"
        manager.db.commit()
        return task

    monkeypatch.setattr(TaskManager, "commit", hold_task)
    for kind, ids in (("domain", vm_ids), ("network", network_ids)):
        directory = tmp_path / "xml" / kind
        directory.mkdir(parents=True)
        for resource_id in ids:
            (directory / f"{resource_id}.xml").write_text(f"<{kind}/>")

    try:
        with SessionLocal.begin() as db:
            admin = UserModel(username=admin_name, hashed_password="unused")
            member = UserModel(username=member_name, hashed_password="unused")
            db.add_all([
                admin, member,
                UserScopeModel(user_id=admin_name, name="admin"),
                UserScopeModel(user_id=member_name, name="user"),
                UserScopeModel(user_id=member_name, name="image.manage"),
            ])
            project = ProjectModel(id=project_id, name=prefix, users=[admin, member])
            db.add(project)
            for index, node_name in enumerate(nodes):
                db.add(NodeModel(
                    name=node_name, description="管理用inventory試験", domain="unused.invalid",
                    user_name="unused", port=22, core=2, memory=2048, cpu_gen="test",
                    os_like="linux", os_name="test", os_version="1", status=10, ansible_facts={},
                ))
                db.flush()
                storage = StorageModel(
                    uuid=storage_ids[index], name=node_name, node_name=node_name,
                    capacity=100, available=80, path=f"/images/{node_name}",
                    active=True, auto_start=True, status=2, update_token=suffix,
                )
                network = NetworkModel(
                    uuid=network_ids[index], name=node_name, node_name=node_name,
                    type="openvswitch", bridge=f"br-{index}", active=True,
                    auto_start=True, update_token=suffix,
                )
                port = NetworkPortgroupModel(
                    network=network, name="granted", is_default=True, update_token=suffix,
                )
                db.add(NetworkPortgroupModel(
                    network=network, name="private", is_default=False, update_token=suffix,
                ))
                storage_pool = StoragePoolModel(
                    name=node_name, storages=[AssociationStoragePoolModel(storage=storage)],
                )
                network_pool = NetworkPoolModel(name=node_name, ports=[port])
                flavor = FlavorModel(
                    name=node_name, os="linux", description="test", icon="linux",
                    manual_url="https://example.invalid", cloud_init_ready=False,
                    cloud_init_user="unused",
                )
                db.add_all([storage_pool, network_pool, flavor])
                db.flush()
                db.add(ImageModel(
                    name=node_name, storage_uuid=storage.uuid,
                    path=f"/images/{node_name}/disk", capacity=10, allocation=2,
                    flavor=flavor, update_token=suffix,
                ))
                vm = DomainModel(
                    uuid=vm_ids[index], name=node_name, node_name=node_name,
                    core=1, memory=1024, storage_used=10, status=5, update_token=suffix,
                )
                if index == 0:
                    project.storage_pools.append(storage_pool)
                    project.network_pools.append(network_pool)
                    project.flavors.append(flavor)
                    vm.owner_project_id = project_id
                else:
                    vm.owner_user_id = member_name
                db.add(vm)
            db.add(TaskModel(
                uuid=task_id, user_id=member_name, status="finish", resource="vm",
                object="root", method="post", request="{}", post_time=datetime.now(UTC),
            ))

        admin_headers = _headers(admin_name, ["admin"])
        project_headers = _headers(admin_name, ["admin"], [project_id])
        member_headers = _headers(member_name, ["user"], [project_id])
        list_paths = [f"/api/{name}" for name in (
            "vms", "nodes", "storages", "images", "networks", "flavors",
        )]
        query: dict[str, str | int | bool] = {"nameLike": prefix, "limit": 0}
        for path in list_paths:
            ordinary = api_client.get(path, headers=admin_headers, params=query)
            assert ordinary.status_code == 200, ordinary.text
            assert ordinary.json()["count"] == 0, path
            inventory = api_client.get(path, headers=admin_headers, params={**query, "admin": True})
            assert inventory.status_code == 200, inventory.text
            assert inventory.json()["count"] == 2, path
            filtered = api_client.get(path, headers=project_headers, params={
                **query, "admin": True, "projectId": project_id,
            })
            assert filtered.status_code == 200, filtered.text
            assert filtered.json()["count"] == 1, path
            assert filtered.json()["data"][0]["name"] == nodes[0]
            if path == "/api/networks":
                assert {port["name"] for port in inventory.json()["data"][0]["portgroups"]} == {"granted", "private"}
                assert [port["name"] for port in filtered.json()["data"][0]["portgroups"]] == ["granted"]
            assert api_client.get(path, headers=admin_headers, params={
                **query, "admin": True, "projectId": project_id,
            }).status_code == 404
            page = api_client.get(path, headers=admin_headers, params={
                **query, "admin": True, "limit": 1, "page": 1,
            })
            assert page.json()["count"] == 2 and len(page.json()["data"]) == 1

        pool_paths = ["/api/storages/pools", "/api/networks/pools"]
        for path in pool_paths:
            assert api_client.get(path, headers=admin_headers).json() == []
            inventory = api_client.get(path, headers=admin_headers, params={"admin": True})
            assert inventory.status_code == 200, inventory.text
            assert set(nodes).issubset({row["name"] for row in inventory.json()})
            filtered = api_client.get(path, headers=project_headers, params={"admin": True, "projectId": project_id})
            assert filtered.status_code == 200
            assert [row["name"] for row in filtered.json()] == [nodes[0]]

        detail_paths = [
            f"/api/vms/{vm_ids[1]}", f"/api/vms/{vm_ids[1]}/xml",
            f"/api/storages/{storage_ids[1]}", f"/api/networks/{network_ids[0]}",
            f"/api/networks/{network_ids[0]}/xml", f"/api/projects/{project_id}",
        ]
        for path in detail_paths:
            assert api_client.get(path, headers=admin_headers).status_code == 404
            detail = api_client.get(path, headers=admin_headers, params={"admin": True})
            assert detail.status_code == 200, detail.text
        assert api_client.get(
            f"/api/networks/{network_ids[0]}/xml", headers=project_headers,
            params={"admin": True, "projectId": project_id},
        ).status_code == 404

        projects = api_client.get("/api/projects", headers=admin_headers, params={**query, "admin": True})
        assert projects.status_code == 200
        assert projects.json()["count"] == 1
        dashboard = api_client.get("/api/dashboard", headers=admin_headers, params={"admin": True})
        assert dashboard.status_code == 200, dashboard.text
        assert dashboard.json()["visibility"] == "all"
        with SessionLocal() as db:
            for field, model in (("vms", DomainModel), ("nodes", NodeModel), ("storages", StorageModel), ("images", ImageModel), ("networks", NetworkModel)):
                assert dashboard.json()[field]["count"] == db.query(model).count()
        assert task_id in {task["uuid"] for task in dashboard.json()["tasks"]["recent"]}
        ordinary_dashboard = api_client.get("/api/dashboard", headers=admin_headers).json()
        assert ordinary_dashboard["visibility"] == "assigned"
        assert ordinary_dashboard["vms"]["count"] == 0

        # 明示queryだけ、DBだけ、tokenだけでは全体参照を許可しない。
        for headers in (member_headers, _headers(member_name, ["admin"]), _headers(admin_name, ["user"])):
            for path in list_paths + pool_paths + detail_paths + ["/api/projects", "/api/dashboard"]:
                assert api_client.get(path, headers=headers, params={"admin": True}).status_code == 403, path
        assert api_client.get(f"/api/vms/{vm_ids[0]}", headers=member_headers).status_code == 200
        # 管理者のconsole接続には明示指定とDB・token双方のadmin scopeが必要。
        assert api_client.post(f"/api/vms/{vm_ids[1]}/console-ticket", headers=admin_headers).status_code == 404
        admin_ticket = api_client.post(
            f"/api/vms/{vm_ids[1]}/console-ticket",
            headers=admin_headers,
            params={"admin": True},
        )
        assert admin_ticket.status_code == 200, admin_ticket.text
        assert admin_ticket.json()["token"]
        for headers in (member_headers, _headers(member_name, ["admin"]), _headers(admin_name, ["user"])):
            assert api_client.post(
                f"/api/vms/{vm_ids[1]}/console-ticket",
                headers=headers,
                params={"admin": True},
            ).status_code == 403
        assert api_client.get("/api/projects/missing", headers=admin_headers, params={"admin": True}).status_code == 404

        download_path = "/api/tasks/images/download"
        download_body = {"storageUuid": storage_ids[1], "imageUrl": "https://unused.invalid/installer.iso"}
        # 一覧で選択できるProject未割当storageへ、明示的な管理操作で受付できる。
        ordinary = api_client.post(download_path, headers=admin_headers, json=download_body)
        assert ordinary.status_code == 404
        assert ordinary.json()["detail"]["code"] == "storage_not_found"
        download = api_client.post(
            download_path, headers=admin_headers, params={"admin": True}, json=download_body,
        )
        assert download.status_code == 200, download.text
        task = download.json()[0]
        assert (task["method"], task["resource"], task["object"]) == ("post", "image", "download")
        assert task["request"]["body"]["storage_uuid"] == storage_ids[1]

        scoped_headers = _headers(member_name, ["image.manage"], [project_id])
        for headers in (scoped_headers, _headers(member_name, ["admin"]), _headers(admin_name, ["image.manage"])):
            rejected = api_client.post(
                download_path, headers=headers, params={"admin": True}, json=download_body,
            )
            assert rejected.status_code == 403, rejected.text
        missing = api_client.post(
            download_path, headers=admin_headers, params={"admin": True},
            json={**download_body, "storageUuid": str(uuid4())},
        )
        assert missing.status_code == 404
        assert missing.json()["detail"]["code"] == "storage_not_found"
        assert api_client.post(download_path, headers=scoped_headers, json=download_body).status_code == 404
        allowed = api_client.post(
            download_path, headers=scoped_headers,
            json={**download_body, "storageUuid": storage_ids[0]},
        )
        assert allowed.status_code == 200, allowed.text
        with SessionLocal() as db:
            assert db.query(TaskModel).filter(
                TaskModel.user_id.in_([admin_name, member_name]), TaskModel.resource == "image",
            ).count() == 2
    finally:
        with SessionLocal.begin() as db:
            db.query(TaskModel).filter(TaskModel.user_id.in_([admin_name, member_name])).delete(synchronize_session=False)
            db.query(DomainModel).filter(DomainModel.uuid.in_(vm_ids)).delete(synchronize_session=False)
            db.query(ProjectModel).filter(ProjectModel.id == project_id).delete()
            db.query(StoragePoolModel).filter(StoragePoolModel.name.in_(nodes)).delete(synchronize_session=False)
            db.query(NetworkPoolModel).filter(NetworkPoolModel.name.in_(nodes)).delete(synchronize_session=False)
            db.query(NodeModel).filter(NodeModel.name.in_(nodes)).delete(synchronize_session=False)
            db.query(FlavorModel).filter(FlavorModel.name.in_(nodes)).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username.in_([admin_name, member_name])).delete(synchronize_session=False)
