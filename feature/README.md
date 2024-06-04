


```
docker compose up -d --build 
docker compose exec ubuntu bash
```

apt install patchelf ccache

python3 -m  nuitka --onefile --follow-imports main.py --include-module=sqlalchemy.orm.dependency