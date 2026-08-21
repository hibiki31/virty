from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from domain.models import DomainModel
from mixin.database import SessionLocal
from network.models import NetworkModel, NetworkPortgroupModel
from node.models import AssociationNodeToRoleModel, NodeModel, NodeRoleModel
from project.models import ProjectModel
from storage.models import ImageModel, StorageModel
from task.models import TaskModel
from user.models import (
    UserModel,
    UserScopeModel,
    association_users_to_projects,
)


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _headers(username: str, scopes: list[str]) -> dict[str, str]:
    token = create_access_token(
        data={"sub": username, "scopes": scopes, "projects": []},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


def _task(
    *,
    uuid: str,
    user_id: str,
    status: str,
    post_time: datetime,
    private_value: str,
) -> TaskModel:
    task = TaskModel(
        uuid=uuid,
        post_time=post_time,
        user_id=user_id,
        status=status,
        resource="vm",
        object="power",
        method="patch",
        request=private_value,
        result={"private": private_value},
    )
    task.run_time = 1.25
    task.message = private_value
    task.log = private_value
    return task


def test_dashboard_requires_authentication(api_client: TestClient) -> None:
    response = api_client.get("/api/dashboard")

    assert response.status_code == 401


def test_dashboard_returns_zero_summaries_for_empty_inventory(
    api_client: TestClient,
) -> None:
    username = f"dashboard-empty-{uuid4().hex}"

    try:
        with SessionLocal.begin() as db:
            db.add(UserModel(username=username, hashed_password="unused"))
            db.add(UserScopeModel(user_id=username, name="user"))

        response = api_client.get(
            "/api/dashboard",
            headers=_headers(username, ["user"]),
        )
        assert response.status_code == 200, response.text
        body = response.json()

        assert body["visibility"] == "assigned"
        assert datetime.fromisoformat(body["generatedAt"]).tzinfo is not None
        assert body["nodes"] == {
            "count": 0,
            "core": 0,
            "memoryGib": 0.0,
            "roles": [],
        }
        assert body["vms"] == {
            "count": 0,
            "core": 0,
            "memoryGib": 0.0,
            "statuses": {
                "running": 0,
                "stopped": 0,
                "maintenance": 0,
                "deleted": 0,
                "lostNode": 0,
                "unknown": 0,
            },
        }
        assert body["storages"] == {
            "count": 0,
            "capacityGib": 0,
            "usedGib": 0,
            "availableGib": 0,
            "highUsageCount": 0,
            "highestUsage": [],
        }
        assert body["networks"] == {
            "count": 0,
            "portGroupCount": 0,
            "types": [],
        }
        assert body["images"] == {"count": 0}
        assert body["tasks"] == {
            "incompleteCount": 0,
            "failedLast24Hours": 0,
            "recent": [],
        }
    finally:
        with SessionLocal.begin() as db:
            db.query(UserScopeModel).filter(
                UserScopeModel.user_id == username
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username == username).delete(
                synchronize_session=False
            )


def test_dashboard_normalizes_nullable_cached_values(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    username = f"dashboard-null-{suffix}"
    storage_uuids = [f"dashboard-null-storage-{index}-{suffix}" for index in range(2)]
    network_uuids = [f"dashboard-null-network-{index}-{suffix}" for index in range(2)]
    task_uuids = [f"dashboard-null-task-{index}-{suffix}" for index in range(2)]
    now = datetime.now(UTC)

    try:
        with SessionLocal.begin() as db:
            db.add(UserModel(username=username, hashed_password="unused"))
            db.add(UserScopeModel(user_id=username, name="user"))
            db.flush()
            db.execute(StorageModel.__table__.insert(), [
                {
                    "uuid": storage_uuids[0],
                    "name": None,
                    "node_name": None,
                    "capacity": None,
                    "available": None,
                    "path": None,
                    "active": None,
                    "auto_start": None,
                    "status": None,
                    "update_token": "dashboard-null-test",
                },
                {
                    "uuid": storage_uuids[1],
                    "name": "overavailable",
                    "node_name": None,
                    "capacity": 10,
                    "available": 20,
                    "path": None,
                    "active": None,
                    "auto_start": None,
                    "status": None,
                    "update_token": "dashboard-null-test",
                },
            ])
            db.execute(NetworkModel.__table__.insert(), [
                {
                    "uuid": network_uuids[0],
                    "name": "null-type",
                    "node_name": None,
                    "bridge": "virbr-null",
                    "type": None,
                    "active": None,
                    "auto_start": None,
                    "dhcp": None,
                    "update_token": "dashboard-null-test",
                },
                {
                    "uuid": network_uuids[1],
                    "name": "empty-type",
                    "node_name": None,
                    "bridge": "virbr-empty",
                    "type": "",
                    "active": None,
                    "auto_start": None,
                    "dhcp": None,
                    "update_token": "dashboard-null-test",
                },
            ])
            db.execute(TaskModel.__table__.insert(), [
                {
                    "uuid": task_uuids[0],
                    "post_time": now - timedelta(hours=26),
                    "update_time": now - timedelta(hours=1),
                    "run_time": None,
                    "user_id": username,
                    "status": "error",
                    "resource": None,
                    "object": None,
                    "method": None,
                    "request": {},
                    "result": None,
                    "message": None,
                    "log": None,
                },
                {
                    "uuid": task_uuids[1],
                    "post_time": now - timedelta(hours=27),
                    "update_time": None,
                    "run_time": None,
                    "user_id": username,
                    "status": "lost",
                    "resource": "vm",
                    "object": "root",
                    "method": "post",
                    "request": {},
                    "result": None,
                    "message": None,
                    "log": None,
                },
            ])

        response = api_client.get(
            "/api/dashboard",
            headers=_headers(username, ["user"]),
        )
        assert response.status_code == 200, response.text
        body = response.json()

        assert body["storages"] == {
            "count": 2,
            "capacityGib": 10,
            "usedGib": 0,
            "availableGib": 20,
            "highUsageCount": 0,
            "highestUsage": [
                {
                    "uuid": storage_uuids[1],
                    "name": "overavailable",
                    "nodeName": "unknown",
                    "capacityGib": 10,
                    "usedGib": 0,
                    "availableGib": 20,
                    "usagePercent": 0.0,
                },
                {
                    "uuid": storage_uuids[0],
                    "name": "unknown",
                    "nodeName": "unknown",
                    "capacityGib": 0,
                    "usedGib": 0,
                    "availableGib": 0,
                    "usagePercent": None,
                },
            ],
        }
        assert body["networks"] == {
            "count": 2,
            "portGroupCount": 0,
            "types": [{"name": "unknown", "count": 2}],
        }
        assert body["tasks"]["incompleteCount"] == 0
        assert body["tasks"]["failedLast24Hours"] == 1
        recent_task = body["tasks"]["recent"][0]
        assert datetime.fromisoformat(recent_task["postTime"]) == (
            now - timedelta(hours=26)
        )
        assert {**recent_task, "postTime": None} == {
            "uuid": task_uuids[0],
            "userId": username,
            "status": "error",
            "resource": "unknown",
            "object": "unknown",
            "method": "unknown",
            "postTime": None,
            "runTime": None,
        }
    finally:
        with SessionLocal.begin() as db:
            db.query(TaskModel).filter(TaskModel.uuid.in_(task_uuids)).delete(
                synchronize_session=False
            )
            db.query(NetworkModel).filter(
                NetworkModel.uuid.in_(network_uuids)
            ).delete(synchronize_session=False)
            db.query(StorageModel).filter(
                StorageModel.uuid.in_(storage_uuids)
            ).delete(synchronize_session=False)
            db.query(UserScopeModel).filter(
                UserScopeModel.user_id == username
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username == username).delete(
                synchronize_session=False
            )


def test_dashboard_aggregates_cache_and_respects_visibility(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    regular_user = f"dashboard-user-{suffix}"
    other_user = f"dashboard-other-{suffix}"
    admin_user = f"dashboard-admin-{suffix}"
    usernames = [regular_user, other_user, admin_user]
    project_id = suffix[:6]
    node_names = [f"dashboard-node-a-{suffix}", f"dashboard-node-b-{suffix}"]
    role_names = [f"dashboard-libvirt-{suffix}", f"dashboard-ssh-{suffix}"]
    storage_uuids = [f"dashboard-storage-{index}-{suffix}" for index in range(5)]
    network_uuids = [f"dashboard-network-{index}-{suffix}" for index in range(3)]
    vm_uuids = [f"dashboard-vm-{index}-{suffix}" for index in range(7)]
    task_uuids = [f"dashboard-task-{index}-{suffix}" for index in range(10)]
    private_value = f"NEVER_EXPOSE_DASHBOARD_PAYLOAD_{suffix}"
    now = datetime.now(UTC)

    try:
        with SessionLocal.begin() as db:
            db.add_all([
                UserModel(username=username, hashed_password="unused")
                for username in usernames
            ])
            db.add_all([
                UserScopeModel(user_id=regular_user, name="user"),
                UserScopeModel(user_id=other_user, name="user"),
                UserScopeModel(user_id=admin_user, name="user"),
                UserScopeModel(user_id=admin_user, name="admin"),
            ])
            project = ProjectModel(
                id=project_id,
                name=f"dashboard-project-{suffix}",
                is_admin=False,
                core=32,
                memory_g=64,
                storage_capacity_g=512,
                user_installable=True,
            )
            db.add(project)
            db.flush()
            db.execute(association_users_to_projects.insert().values(
                user_id=regular_user,
                project_id=project_id,
            ))

            db.add_all([
                NodeModel(
                    name=node_names[0],
                    description="dashboard test node A",
                    domain="node-a.invalid",
                    user_name="dashboard-test",
                    port=22,
                    core=16,
                    memory=64,
                    cpu_gen="test cpu",
                    os_like="debian",
                    os_name="Test Linux",
                    os_version="1",
                    status=10,
                    ansible_facts={},
                ),
                NodeModel(
                    name=node_names[1],
                    description="dashboard test node B",
                    domain="node-b.invalid",
                    user_name="dashboard-test",
                    port=22,
                    core=8,
                    memory=32,
                    cpu_gen="test cpu",
                    os_like="debian",
                    os_name="Test Linux",
                    os_version="1",
                    status=10,
                    ansible_facts={},
                ),
                NodeRoleModel(name=role_names[0]),
                NodeRoleModel(name=role_names[1]),
            ])
            db.flush()
            db.add_all([
                AssociationNodeToRoleModel(
                    node_name=node_names[0],
                    role_name=role_names[0],
                    extra_json={},
                ),
                AssociationNodeToRoleModel(
                    node_name=node_names[0],
                    role_name=role_names[1],
                    extra_json={},
                ),
                AssociationNodeToRoleModel(
                    node_name=node_names[1],
                    role_name=role_names[1],
                    extra_json={},
                ),
            ])

            vm_values = [
                (1, 2, 2048, regular_user, None),
                (5, 4, 4096, None, project_id),
                (7, 1, 512, regular_user, None),
                (10, 1, 1024, None, project_id),
                (20, 1, 1024, regular_user, None),
                (99, 3, 3072, None, project_id),
                (1, 8, 8192, other_user, None),
            ]
            vms = []
            for index, (
                status,
                core,
                memory,
                owner_user_id,
                owner_project_id,
            ) in enumerate(vm_values):
                vm = DomainModel(
                    uuid=vm_uuids[index],
                    name=f"dashboard-vm-{index}",
                    core=core,
                    memory=memory,
                    status=status,
                    update_token="dashboard-test",
                    node_name=node_names[index % len(node_names)],
                )
                vm.vnc_password = private_value
                vm.owner_user_id = owner_user_id
                vm.owner_project_id = owner_project_id
                vms.append(vm)
            db.add_all(vms)

            storage_values = [
                ("a-high", 100, 10),
                ("b-high", 100, 15),
                ("c-medium", 100, 20),
                ("d-zero", 0, 0),
                ("e-zero", 0, 0),
            ]
            db.add_all([
                StorageModel(
                    uuid=storage_uuids[index],
                    name=f"{name}-{suffix}",
                    node_name=node_names[index % len(node_names)],
                    capacity=capacity,
                    available=available,
                    path=private_value,
                    active=True,
                    auto_start=True,
                    status=2,
                    update_token="dashboard-test",
                )
                for index, (name, capacity, available) in enumerate(storage_values)
            ])

            network_values = [
                ("nat-a", "nat"),
                ("nat-b", "nat"),
                ("ovs", "openvswitch"),
            ]
            networks = []
            for index, (name, network_type) in enumerate(network_values):
                network = NetworkModel(
                    uuid=network_uuids[index],
                    name=f"{name}-{suffix}",
                    node_name=node_names[index % len(node_names)],
                    bridge=f"virbr{index}",
                    type=network_type,
                    active=True,
                    auto_start=True,
                    update_token="dashboard-test",
                )
                network.dhcp = False
                networks.append(network)
            db.add_all(networks)
            db.flush()
            port_groups = [
                NetworkPortgroupModel(
                    network_uuid=network_uuids[0],
                    name="default",
                    is_default=True,
                    update_token="dashboard-test",
                ),
                NetworkPortgroupModel(
                    network_uuid=network_uuids[0],
                    name="vlan-100",
                    is_default=False,
                    update_token="dashboard-test",
                ),
                NetworkPortgroupModel(
                    network_uuid=network_uuids[2],
                    name="vlan-200",
                    is_default=False,
                    update_token="dashboard-test",
                ),
            ]
            port_groups[1].vlan_id = "100"
            port_groups[2].vlan_id = "200"
            db.add_all(port_groups)

            db.add_all([
                ImageModel(
                    name=f"dashboard-image-{index}",
                    storage_uuid=storage_uuids[index],
                    capacity=10,
                    allocation=5,
                    path=f"{private_value}-{index}",
                    update_token="dashboard-test",
                )
                for index in range(2)
            ])

            regular_task_values = [
                ("start", now - timedelta(minutes=1)),
                ("start", now - timedelta(minutes=2)),
                ("start", now - timedelta(minutes=3)),
                ("error", now - timedelta(minutes=4)),
                ("lost", now - timedelta(minutes=5)),
                ("finish", now - timedelta(minutes=6)),
                ("finish", now - timedelta(minutes=7)),
                ("error", now - timedelta(hours=25)),
            ]
            db.add_all([
                _task(
                    uuid=task_uuids[index],
                    user_id=regular_user,
                    status=status,
                    post_time=post_time,
                    private_value=private_value,
                )
                for index, (status, post_time) in enumerate(regular_task_values)
            ])
            db.add_all([
                _task(
                    uuid=task_uuids[8],
                    user_id=other_user,
                    status="start",
                    post_time=now - timedelta(seconds=30),
                    private_value=private_value,
                ),
                _task(
                    uuid=task_uuids[9],
                    user_id=other_user,
                    status="error",
                    post_time=now - timedelta(seconds=90),
                    private_value=private_value,
                ),
            ])

        regular_response = api_client.get(
            "/api/dashboard",
            headers=_headers(regular_user, ["user"]),
        )
        assert regular_response.status_code == 200, regular_response.text
        regular = regular_response.json()

        assert regular["visibility"] == "assigned"
        assert datetime.fromisoformat(regular["generatedAt"]).tzinfo is not None
        assert regular["nodes"] == {
            "count": 2,
            "core": 24,
            "memoryGib": 96.0,
            "roles": [
                {"name": role_names[1], "count": 2},
                {"name": role_names[0], "count": 1},
            ],
        }
        assert regular["vms"] == {
            "count": 6,
            "core": 11,
            "memoryGib": 10.5,
            "statuses": {
                "running": 1,
                "stopped": 1,
                "maintenance": 1,
                "deleted": 1,
                "lostNode": 1,
                "unknown": 1,
            },
        }
        assert regular["storages"]["count"] == 5
        assert regular["storages"]["capacityGib"] == 300
        assert regular["storages"]["usedGib"] == 255
        assert regular["storages"]["availableGib"] == 45
        assert regular["storages"]["highUsageCount"] == 2
        highest_usage = regular["storages"]["highestUsage"]
        assert len(highest_usage) == 4
        assert [pool["usagePercent"] for pool in highest_usage] == [90.0, 85.0, 80.0, None]
        assert highest_usage[-1]["name"] == f"d-zero-{suffix}"
        assert regular["networks"] == {
            "count": 3,
            "portGroupCount": 3,
            "types": [
                {"name": "nat", "count": 2},
                {"name": "openvswitch", "count": 1},
            ],
        }
        assert regular["images"] == {"count": 2}
        assert regular["tasks"]["incompleteCount"] == 3
        assert regular["tasks"]["failedLast24Hours"] == 2
        assert [task["uuid"] for task in regular["tasks"]["recent"]] == task_uuids[:6]
        assert {task["userId"] for task in regular["tasks"]["recent"]} == {regular_user}
        for task in regular["tasks"]["recent"]:
            assert set(task) == {
                "uuid",
                "userId",
                "status",
                "resource",
                "object",
                "method",
                "postTime",
                "runTime",
            }
        assert private_value not in regular_response.text

        admin_response = api_client.get(
            "/api/dashboard",
            headers=_headers(admin_user, ["user", "admin"]),
        )
        assert admin_response.status_code == 200, admin_response.text
        admin = admin_response.json()

        assert admin["visibility"] == "all"
        assert admin["vms"]["count"] == 7
        assert admin["vms"]["core"] == 19
        assert admin["vms"]["memoryGib"] == 18.5
        assert admin["vms"]["statuses"]["running"] == 2
        assert admin["tasks"]["incompleteCount"] == 4
        assert admin["tasks"]["failedLast24Hours"] == 3
        assert len(admin["tasks"]["recent"]) == 6
        assert other_user in {task["userId"] for task in admin["tasks"]["recent"]}
        assert private_value not in admin_response.text
    finally:
        with SessionLocal.begin() as db:
            db.query(TaskModel).filter(TaskModel.uuid.in_(task_uuids)).delete(
                synchronize_session=False
            )
            db.query(ImageModel).filter(
                ImageModel.storage_uuid.in_(storage_uuids)
            ).delete(synchronize_session=False)
            db.query(DomainModel).filter(DomainModel.uuid.in_(vm_uuids)).delete(
                synchronize_session=False
            )
            db.query(NetworkPortgroupModel).filter(
                NetworkPortgroupModel.network_uuid.in_(network_uuids)
            ).delete(synchronize_session=False)
            db.query(NetworkModel).filter(
                NetworkModel.uuid.in_(network_uuids)
            ).delete(synchronize_session=False)
            db.query(StorageModel).filter(
                StorageModel.uuid.in_(storage_uuids)
            ).delete(synchronize_session=False)
            db.query(AssociationNodeToRoleModel).filter(
                AssociationNodeToRoleModel.node_name.in_(node_names)
            ).delete(synchronize_session=False)
            db.query(NodeModel).filter(NodeModel.name.in_(node_names)).delete(
                synchronize_session=False
            )
            db.execute(association_users_to_projects.delete().where(
                association_users_to_projects.c.project_id == project_id
            ))
            db.query(ProjectModel).filter(ProjectModel.id == project_id).delete(
                synchronize_session=False
            )
            db.query(UserScopeModel).filter(
                UserScopeModel.user_id.in_(usernames)
            ).delete(synchronize_session=False)
            db.query(UserModel).filter(UserModel.username.in_(usernames)).delete(
                synchronize_session=False
            )
            db.query(NodeRoleModel).filter(
                NodeRoleModel.name.in_(role_names)
            ).delete(synchronize_session=False)
