# Virty

## Install

### Docker

Package

- git
- docker-compose

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

```
http://IP/setup
```

## Start up

### Add node

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
http://192.168.203.88/node/add
```

