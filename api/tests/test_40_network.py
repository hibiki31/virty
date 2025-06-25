
from tests.fixtures.network import create_network, delete_network


def test_delete_network(env, client, created_network):
    delete_network(env, client)

def test_create_network(env, client, deleted_network):
    create_network(env, client)







# @tester
# def post_network_ovs():
#     resp = httpx.request(method="get", url=f'{BASE_URL}/api/networks', params={"admin":True},headers=HEADERS)
#     print_resp(resp=resp)

#     for net in resp.json()["data"]:
#         if net["type"] == "openvswitch":
#             request_data = {
#                 "default": True,
#                 "name": "test-vlan-1919",
#                 "vlanId": 1919
#             }
#             resp = httpx.request(method="post",url=f'{BASE_URL}/api/tasks/networks/{net["uuid"]}/ovs', headers=HEADERS, json=request_data)
#             print_resp(resp=resp)
#             wait_tasks(resp)


# @tester
# def delete_network_ovs():
#     resp = httpx.request(method="get", url=f'{BASE_URL}/api/networks', params={"admin":True},headers=HEADERS)
#     print_resp(resp=resp)

#     for net in resp.json()["data"]:
#         if net["type"] == "openvswitch":
#             resp = httpx.request(method="delete",url=f'{BASE_URL}/api/tasks/networks/{net["uuid"]}/ovs/test-vlan-1919', headers=HEADERS)
#             print_resp(resp=resp,allow_not_found=True)
#             if resp.status_code == 200:
#                 wait_tasks(resp)


# @tester
# def create_network_provider():
#     request_data={
#         "name": "test",
#         "dnsDomain": "test.v.",
#         "networkAddress": "10.248.10.0",
#         "networkPrefix": "24",
#         "gatewayAddress": "10.248.10.254",
#         "dhcpStart": "10.248.10.1",
#         "dhcpEnd": "10.248.10.253",
#         "networkNode": "test-r640-01"
#     }
#     resp = httpx.request(method="post",url=f'{BASE_URL}/api/tasks/networks/providers', headers=HEADERS, json=request_data)
#     print_resp(resp=resp)
#     wait_tasks(resp)