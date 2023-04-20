
## Test



## Celery

```bash
# ダッシュボード
celery --app=worker flower --port=5555
# 12サブプロセス
celery --app=worker worker --pool prefork --concurrency 12
# オートスケール
celery --app=worker worker --autoscale=32,4
```

## Alembic

```bash
alembic revision --autogenerate -m "Added columns."
alembic revision --autogenerate
alembic upgrade head
alembic downgrade base
dropdb -U postgres -h db mydatabase
psql -U postgres -h db -c "create database mydatabase"
```

## マージ手順

- APIとWEBのバージョンを更新して`Update v2.0.0`でコミット
- masterブランチでマージする`Merge branch 'develop' v2.0.0`
- バージョンタグをつけてリモートにもpush`v2.0.0`
- masterブランチをpushする

## コミット手順

タイトルの先頭には以下をつける

```
Fix バグ修正
Add 機能追加
Change バグではないコードの修正
Update 動作に関係ない修正やドキュメントの修正、masterマージ前の変更履歴など
Remove 不要なコードの削除
Revert 変更取り消し
Move ファイルの移動
```

## Git設定

fast-forwardは無効化

```
git config --global --add merge.ff false
git config --global --add pull.ff only
```

ログ確認

```
git log --date=short --no-merges --pretty=format:"%cd %s %h (@%cn) "
```

## Docker image 公開

```
ls -la ./api/data

VER=2.2.0
docker build --no-cache --pull -t hibiki131/virty-api:$VER ./api/
docker push hibiki131/virty-api:$VER
docker build --no-cache --pull -t hibiki131/virty-web:$VER ./web/
docker push hibiki131/virty-web:$VER
docker build --no-cache --pull -t hibiki131/virty-proxy:$VER ./proxy/
docker push hibiki131/virty-proxy:$VER
```

```
VER=`cat ./next/package.json |grep '"version":' |sed -E 's/.*\"(.*)\".*/\1/g'`
docker build -t virty-next:$VER -f ./next/Dockerfile ./next
docker tag virty-next:$VER virty-next:latest

VER=`cat ./web/package.json |grep '"version":' |sed -E 's/.*\"(.*)\".*/\1/g'`
docker build -t virty-web:$VER -f ./web/Dockerfile ./web
docker tag virty-web:$VER virty-web:latest

VER=`cat ./api/settings.py |grep 'API_VERSION' |sed -E "s/.*'(.*)'.*/\1/g"`
docker build -t virty-api:$VER -f ./api/Dockerfile ./api
docker tag virty-api:$VER virty-api:latest

docker build -t virty-proxy:$VER -f ./proxy/Dockerfile ./proxy
docker tag virty-proxy:$VER virty-proxy:latest
```

## 定数一覧

### task
0 sucsess
1 error
2 skip
3 running
4 init

### domain
1 ON
5 OFF
7 node is maintenance mode
10 deleted domain
20 lost node

### node
10 Up
20 Maintenance
30 Down
40 Error
50 Lost