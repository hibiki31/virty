# Virty

## Note

1. This system is vulnerable, use only locally
2. Authentication function is prototype

## Virty setup

### Docker

Git clone

```
git clone https://github.com/hibiki31/virty.git
```

Docker build & up

```
cd virty
docker-compose build     # make build
docker-compose up -d     # make up
```

If an error with pip

```
docker image rm centos:8 
 or docker image prune -a
```

Login

```
http://<host ip>
user=admin,password=admin
```

## Node setup

### Add node

The following packages are installed on the host

```
libvirt *and start daemon
qemu-img
```

Container login & SSH to node with Use public key authentication to allow SSH without input

```
cd virty
docker exec -it virty_main_1 bash     # make login
```

### System storage pool

Each node must have `archive` and `iso`. The directory must exist.

```
http://IP/storage/add
```

## Packages

### CentOS 7

```
yum -y install libvirt libvirt-client qemu-kvm virt-manager bridge-utils
```

### Ubuntu 18

```
sudo apt update
sudo apt upgrade
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils 
```

select editor

```
sudo update-alternatives --config editor
```

add

```
sudo visudo
-- tail --
username ALL=(ALL) NOPASSWD: ALL
```

