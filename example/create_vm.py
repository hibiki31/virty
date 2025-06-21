import requests

BASE_URL = 'http://localhost:8765'
TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"


def main():
    servers = [
        ["dev-nuxt-server",      "192.168.19.1/24"],
        ["prod-nuxt-server",     "192.168.19.2/24"],
        ["prac-apache-server",   "192.168.19.3/24"],
        ["dev-django-server",    "192.168.19.4/24"],
        ["prod-django-server",   "192.168.19.5/24"],
        ["test-node-server",     "192.168.19.6/24"],
        ["prac-nginx-proxy",     "192.168.19.7/24"],
        ["dev-mysql-server",     "192.168.19.8/24"],
        ["prod-mysql-server",    "192.168.19.9/24"],
        ["dev-redis-cache",      "192.168.19.10/24"],
        ["prod-redis-cache",     "192.168.19.11/24"],
        ["monitoring-prometheus","192.168.19.12/24"],
        ["logging-fluentd",      "192.168.19.13/24"],
        ["test-elasticsearch",   "192.168.19.14/24"],
        ["backup-nfs-server",    "192.168.19.15/24"],
        ["test-grafana",         "192.168.19.16/24"],
        ["prod-kibana",          "192.168.19.17/24"],
        ["dev-rabbitmq-broker",  "192.168.19.18/24"],
        ["prod-rabbitmq-broker", "192.168.19.19/24"],
        ["test-kafka-cluster",   "192.168.19.20/24"],
        ["dev-zookeeper-node",   "192.168.19.21/24"],
        ["prod-postgresql-db",   "192.168.19.22/24"],
        ["dev-mongodb-server",   "192.168.19.23/24"],
        ["test-cassandra-db",    "192.168.19.24/24"],
        ["dev-elasticsearch",    "192.168.19.25/24"],
        ["prod-cdn-edge",        "192.168.19.26/24"],
        ["test-lb-haproxy",      "192.168.19.27/24"],
        ["dev-vault-server",     "192.168.19.28/24"],
        ["prod-vault-server",    "192.168.19.29/24"],
        ["test-smoketests",      "192.168.19.30/24"],
    ]

    for i in servers:
        create_vm(
            # Spec
            vm_name    = i[0],
            node_name  = "node-02",
            core= 8,
            memory= 16,

            # Storage
            src_sotrage_uuid="4df226bb-1a73-4d47-990d-xxxxxxxxxxxx",
            dst_storage_uuid="2ab906b3-8f19-4018-b542-xxxxxxxxxxxx",
            copy_image="noble-server-cloudimg-amd64.img",
            disk_size=128,
            
            # Login
            login_user="user",
            login_pw="password",
            pubkey="ssh-ed25519 XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            
            # Network
            ip_address=i[1],
            gateway="192.168.19.254",
            nameserver="1.1.1.1",
            network_uuid="bec29dff-21ed-46c1-a526-xxxxxxxxxxxx",
        )



def create_vm(vm_name, node_name, core, memory, src_sotrage_uuid, dst_storage_uuid, copy_image, disk_size, network_uuid, login_user, login_pw, pubkey, ip_address, gateway, nameserver):
    userData = f"""
#cloud-config
password: {login_pw}
chpasswd: {{expire: False}}
user: {login_user}
ssh_pwauth: True
ssh_authorized_keys:
  - {pubkey}
timezone: "Asia/Tokyo"
write_files:
  - path: /etc/netplan/50-cloud-init.yaml
    owner: root:root
    permissions: '0644'
    content: |
      network:
        ethernets:
            ens3:
                dhcp4: false
                addresses:
                - {ip_address}
                routes:
                - to: default
                  via: {gateway}
                nameservers:
                  addresses:
                  - {nameserver}
        version: 2
runcmd:
  - [ netplan, apply ]
"""

    request_data = {
        "type": "manual",
        "name": vm_name,
        "nodeName":node_name,
        "memoryMegaByte": memory*1024,
        "cpu":core,
        "disks":[
            {
                "id":1,
                "type":"copy",
                "savePoolUuid": dst_storage_uuid,
                "originalPoolUuid": src_sotrage_uuid,
                "originalName": copy_image,
                "sizeGigaByte": disk_size
            }
        ],
        "interface":[
            {
                "type":"network",
                "networkUuid":network_uuid,
            }
        ],
        "cloudInit":{
            "hostname": vm_name,
            "userData": userData
        }
    }
    res = requests.request(method="post",url=f'{BASE_URL}/api/tasks/vms', headers=HEADERS, json=request_data)
    print(f"CreateVM: {res.status_code}")



HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ja",
    "authorization": f"Bearer {TOKEN}",
}


if __name__ == "__main__":
    main()