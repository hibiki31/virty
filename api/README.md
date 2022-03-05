## Alembic

```bash
alembic revision --autogenerate
alembic upgrade head
alembic downgrade base
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