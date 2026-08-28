from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auth.router import create_access_token
from mixin.database import SessionLocal
from network.models import NetworkModel, NetworkPoolModel, NetworkPortgroupModel
from node.models import NodeModel
from project.models import ProjectModel
from user.models import UserModel, UserScopeModel


pytestmark = [pytest.mark.integration, pytest.mark.timeout(60)]


def _headers(
    username: str,
    *,
    scopes: list[str],
    projects: list[str],
) -> dict[str, str]:
    token = create_access_token(
        data={"sub": username, "scopes": scopes, "projects": projects},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


def test_port_only_project_hides_other_ports_and_requires_admin_for_mutation(
    api_client: TestClient,
) -> None:
    suffix = uuid4().hex
    username = f"network-member-{suffix}"
    admin_username = f"network-admin-{suffix}"
    project_id = suffix[:6]
    node_name = f"network-node-{suffix}"
    network_uuid = str(uuid4())
    pool_name = f"network-pool-{suffix}"

    try:
        with SessionLocal.begin() as db:
            member = UserModel(username=username, hashed_password="unused")
            admin = UserModel(username=admin_username, hashed_password="unused")
            node = NodeModel(
                name=node_name,
                description="Project port grant test",
                domain="no-network.invalid",
                user_name="unused",
                port=22,
                core=1,
                memory=1024,
                cpu_gen="test",
                os_like="linux",
                os_name="test",
                os_version="1",
                status=10,
                ansible_facts={},
            )
            network = NetworkModel(
                uuid=network_uuid,
                name=f"network-{suffix}",
                node_name=node_name,
                bridge=f"virbr-{suffix[:8]}",
                type="openvswitch",
                active=True,
                auto_start=True,
                update_token=suffix,
            )
            network.description = "Project port grant test"
            network.dhcp = False
            granted_port = NetworkPortgroupModel(
                network=network,
                name="tenant-a",
                is_default=False,
                update_token=suffix,
            )
            granted_port.vlan_id = "101"
            denied_port = NetworkPortgroupModel(
                network=network,
                name="tenant-b",
                is_default=False,
                update_token=suffix,
            )
            denied_port.vlan_id = "202"
            pool = NetworkPoolModel(name=pool_name, ports=[granted_port])
            project = ProjectModel(
                id=project_id,
                name=f"network-project-{suffix}",
                users=[member],
                network_pools=[pool],
            )
            db.add_all([admin, node, project, denied_port])
            db.add_all([
                UserScopeModel(user_id=username, name="user"),
                UserScopeModel(user_id=username, name="network.read"),
                UserScopeModel(user_id=username, name="network.manage"),
                UserScopeModel(user_id=admin_username, name="admin"),
            ])

        member_headers = _headers(
            username,
            scopes=["user", "network.manage"],
            projects=[project_id],
        )
        list_response = api_client.get(
            "/api/networks",
            headers=member_headers,
            params={"projectId": project_id, "limit": 0},
        )
        assert list_response.status_code == 200, list_response.text
        assert list_response.json()["count"] == 1
        assert [
            port["name"] for port in list_response.json()["data"][0]["portgroups"]
        ] == ["tenant-a"]

        detail_response = api_client.get(
            f"/api/networks/{network_uuid}",
            headers=member_headers,
            params={"projectId": project_id},
        )
        assert detail_response.status_code == 200, detail_response.text
        assert [
            port["name"] for port in detail_response.json()["portgroups"]
        ] == ["tenant-a"]

        # XMLはnetwork全体のportgroup構成を含むため、port単位grantでは
        # 存在自体を公開しない。
        xml_response = api_client.get(
            f"/api/networks/{network_uuid}/xml",
            headers=member_headers,
            params={"projectId": project_id},
        )
        assert xml_response.status_code == 404

        dashboard_response = api_client.get(
            "/api/dashboard",
            headers=member_headers,
        )
        assert dashboard_response.status_code == 200, dashboard_response.text
        assert dashboard_response.json()["networks"] == {
            "count": 1,
            "portGroupCount": 1,
            "types": [{"name": "openvswitch", "count": 1}],
        }

        admin_without_membership = _headers(
            admin_username,
            scopes=["admin"],
            projects=[],
        )
        admin_list = api_client.get(
            "/api/networks",
            headers=admin_without_membership,
            params={"limit": 0},
        )
        assert admin_list.status_code == 200, admin_list.text
        assert admin_list.json() == {"count": 0, "data": []}
        admin_filtered_detail = api_client.get(
            f"/api/networks/{network_uuid}",
            headers=admin_without_membership,
            params={"projectId": project_id},
        )
        assert admin_filtered_detail.status_code == 404
        assert api_client.get(
            f"/api/nodes/{node_name}/facts",
            headers=admin_without_membership,
        ).status_code == 404
        # Project認可はSSH backendを作る前に評価される。
        assert api_client.get(
            f"/api/nodes/{node_name}/info",
            headers=admin_without_membership,
        ).status_code == 404

        # network構成変更はglobal admin操作なので、read境界とは独立して
        # membershipなしでも対象の存在確認と依存guardまで到達する。
        admin_create_port = api_client.post(
            f"/api/tasks/networks/{network_uuid}/ovs",
            headers=admin_without_membership,
            json={"default": False, "name": "tenant-c", "vlanId": 303},
        )
        assert admin_create_port.status_code == 200, admin_create_port.text
        admin_delete_port = api_client.delete(
            f"/api/tasks/networks/{network_uuid}/ovs/tenant-a",
            headers=admin_without_membership,
        )
        assert admin_delete_port.status_code == 409, admin_delete_port.text
        admin_delete_network = api_client.delete(
            f"/api/tasks/networks/{network_uuid}",
            headers=admin_without_membership,
        )
        assert admin_delete_network.status_code == 409, admin_delete_network.text

        create_port = api_client.post(
            f"/api/tasks/networks/{network_uuid}/ovs",
            headers=member_headers,
            json={"default": False, "name": "tenant-c", "vlanId": 303},
        )
        delete_port = api_client.delete(
            f"/api/tasks/networks/{network_uuid}/ovs/tenant-a",
            headers=member_headers,
        )
        delete_network = api_client.delete(
            f"/api/tasks/networks/{network_uuid}",
            headers=member_headers,
        )
        assert create_port.status_code == 403
        assert delete_port.status_code == 403
        assert delete_network.status_code == 403
    finally:
        with SessionLocal.begin() as db:
            db.query(ProjectModel).filter(ProjectModel.id == project_id).delete(
                synchronize_session=False,
            )
            db.query(NetworkPoolModel).filter(
                NetworkPoolModel.name == pool_name,
            ).delete(synchronize_session=False)
            db.query(NetworkPortgroupModel).filter(
                NetworkPortgroupModel.network_uuid == network_uuid,
            ).delete(synchronize_session=False)
            db.query(NetworkModel).filter(
                NetworkModel.uuid == network_uuid,
            ).delete(synchronize_session=False)
            db.query(NodeModel).filter(NodeModel.name == node_name).delete(
                synchronize_session=False,
            )
            db.query(UserModel).filter(
                UserModel.username.in_([username, admin_username]),
            ).delete(synchronize_session=False)
