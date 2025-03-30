#!/bin/bash

apt install -y \
    git jq iproute2 htop vim \
    unzip zip wget net-tools openssh-client \
    rsync curl

pip install ruff pytest