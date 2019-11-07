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

Container login & Use public key authentication to allow SSH without input

```
make login
```

DB Initialization

```
http://VIRTY/setup
```

