#!/bin/bash

apt-get install -y wget git

pip install --upgrade pip
pip install ruff pytest
pip install -r /workspaces/api/requirements.txt