#!/usr/bin/env bash

set -euo pipefail

printf '警告: これは旧deployment更新scriptです。開発・検証にはrootのdevctlを使用してください。\n' >&2

git pull
docker-compose build
docker-compose down
docker-compose up -d
