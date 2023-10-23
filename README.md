# Virty

[![Docker Image CI](https://github.com/hibiki31/virty/actions/workflows/docker-image.yml/badge.svg)](https://github.com/hibiki31/virty/actions/workflows/docker-image.yml)
[![Docker publish api](https://github.com/hibiki31/virty/actions/workflows/docker-publish-api.yml/badge.svg)](https://github.com/hibiki31/virty/actions/workflows/docker-publish-api.yml)

KVM management web application for low cost and immediate deployment.
Manage nodes with SSH access using Libvirt-API, Ansible, etc.

Nodes are Linux with SSH connectivity and provisioning can be done through the UI.

### Disclaimer

The author is not responsible for any damage caused by the use of this software.

### Quick Start

Nothing needs to be edited.
Start with Docker compose and connect to localhost:8765.

This can be done on the host that will be the hypervisor, or on the laptop at hand.

```
mkdir virty
cd virty
wget https://raw.githubusercontent.com/hibiki31/virty/master/docker-compose.example.yml -O docker-compose.yml
docker compose up -d
```

Once activated, access http://localhost:8765 with a web browser.

### Preparation of managed nodes

Select the text editor to use (optional).

```
sudo update-alternatives --config editor
```

Grant sudo privileges without password to the user connecting to SSH.

```
sudo visudo
-- end --
username ALL=(ALL) NOPASSWD: ALL
```

Use public key authentication.
The key registered here will be added on the dashboard.

```
ssh-copy-id user@host
```

### Open vSwitch (Optional)

#### Configuration

This example has only one nic.
It is recommended to do this from the Console since the network is usually disconnected once.

<img src="https://user-images.githubusercontent.com/35087924/179314489-b8a5e48b-368a-4274-b3ef-9ec67810805c.png" width="800px"/>

| name               | value            |
| ---------------------- | ------------- |
| Bridge name               | ovs-br0       |
| Physical interface | eth0          |
| Native VLAN            | 100           |
| VLAN to configure IP       | 200           |
| IP                     | 192.168.200.1 |

#### Package (Ubuntu)

```bash
sudo apt update
sudo apt install openvswitch-common openvswitch-switch
sudo systemctl status openvswitch-switch.service
```

#### Creating Bridges

```bash
ovs-vsctl add-br ovs-br0
ovs-vsctl add-port ovs-br0 eth0
ovs-vsctl set port ovs-br0 tag=200
ovs-vsctl set port eth0 tag=100 vlan_mode=native-untagged
ovs-vsctl show
```

#### Configure IP (Ubuntu)

```yaml
network:
  ethernets:
    eth0:
      dhcp4: false
    ovs-br0:
      dhcp4: false
      addresses:
        - 192.168.200.1/24
      gateway4: 192.168.200.254
      nameservers:
        addresses: [ 192.168.200.254 ]
  version: 2
```

### Backup

```
docker-compose exec db pg_dump -U postgres mydatabase > virty_db_`date -Iseconds`.dump
```
