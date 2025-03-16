#!/bin/bash

git config --global --add safe.directory /workspaces

apt-get install -y wget git

python3 -m venv /opt/venv

pip install -r /workspaces/api/.devcontainer/requirements.txt
pip install -r /workspaces/api/requirements.txt