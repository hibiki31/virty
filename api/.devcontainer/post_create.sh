#!/bin/bash

git config --global --add safe.directory /workspaces

apt-get install -y wget git

pip install ruff
pip install -r /workspaces/api/requirements.txt