#!/bin/bash
pyinstaller -y \
    --hidden-import gunicorn.glogging \
    --hidden-import gunicorn.workers.sync \
    --onefile \
    server.py

du -hs ./dist

./dist/server