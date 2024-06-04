#!/bin/bash
docker compose build
docker compose up -d
docker compose exec -it ubuntu pip install /opt/lib

docker compose exec -it ubuntu python3 -m nuitka \
    --onefile \
    --standalone \
    --include-package=typer \
    --include-package=tabulate \
    --include-package=virty \
    --follow-imports main.py