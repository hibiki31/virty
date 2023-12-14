#!/bin/bash
docker compose build
docker compose run ubuntu python3 -m nuitka \
    --onefile \
    --standalone \
    --include-package=typer \
    --include-package=tabulate \
    --follow-imports virty.py
# python3 -m  nuitka --onefile --follow-imports virty.py