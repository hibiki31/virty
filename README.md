# Virty

## Overview

1. This system is vulnerable, use only locally
2. Authentication function is prototype

## Install

### Docker

Git clone

```
git clone https://github.com/hibiki31/virty.git
```

Docker build

```
cd virty
make build
make up
```

DB Initialization

## Start up

### Add node

Container login & SSH to node with Use public key authentication to allow SSH without input

```
http://IP/setup
user=admin,password=admin
```

## Start up

### Add node

The following packages are installed on the host

```
libvirt *and start daemon
qemu-img
```

Container login & SSH to node with Use public key authentication to allow SSH without input

```
cd virty
make login
```

Add node data on web interface

```
http://IP/node/add
```

### System storage pool

Each node must have archive and iso. The directory must exist.

```
http://IP/storage/add
```

