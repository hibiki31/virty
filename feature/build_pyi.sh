#!/bin/bash
pyinstaller -y \
    --hidden-import gunicorn.glogging \
    --hidden-import gunicorn.workers.sync \
    --onefile \
    main.py

du -hs ./dist