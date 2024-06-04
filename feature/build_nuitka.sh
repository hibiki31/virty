python3 -m  nuitka --onefile --follow-imports main.py \
    --include-module=sqlalchemy.orm.dependency \
    --include-package=gunicorn

du -h main.bin 