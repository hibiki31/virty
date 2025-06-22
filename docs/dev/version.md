# バージョン履歴

## v0.0.8

<img width="1628" alt="スクリーンショット 2025-06-22 15 02 51" src="https://github.com/user-attachments/assets/87779a6d-71e2-4dc6-843b-8eac3c000b89" />

- CenOS 8ベース
- Flask Bootstrap
- sqlite3

!!! note
    2025年6月22日 動作確認
    - Version 0.0.8 release
    - c9df3ad49b22da02a582aecbabb4815b329fa7aa

`docker/virty-nginx/Dockerfile`と`/home/akane/virty/docker/virty-main/Dockerfile`を編集

```dockerfile
FROM rockylinux:8.9
```

`/home/akane/virty/docker-compose.yml`

```yaml
    ports:
      - "8989:80"
```

ssh-keygen

```bash
$ docker exec -it virty-main-1 bash
[root@078eb1f8e015 main]# ssh-keygen 
```

DB Initialization

```bash
http://IP/setup
```

500が発生するため`@login_required`を外す

```bash
VER=0.0.8
docker build --no-cache --pull -t hibiki31/virty-api:$VER ./docker/virty-main
docker push hibiki31/virty-api:$VER
docker build --no-cache --pull -t hibiki31/virty-web:$VER ./docker/virty-nginx
docker push hibiki31/virty-web:$VER
```

## v1.6.1

<img width="1436" alt="スクリーンショット 2025-06-22 15 57 39" src="https://github.com/user-attachments/assets/af81f465-3b8e-4d01-a41d-4d2980cdf034" />

- fastapi 0.65.2
- node 14.19
- vue 2.6.12

!!! note
    2025年6月22日 動作確認
    - Update v1.6.1
    - 183dacdc5bfad872c20bb4097dd08786fd5cc34f

`docker-compose.example.yml`

```yaml
ports:
  - "8989:80"
```

Buildが失敗するため、以下編集 `main/requirements.txt`

```bash
uvicorn==0.17.0
```

ssh-keygen

```bash
$ docker exec -it virty-virty-main-1 bash
root@d13a9cf36698:/opt/virty/app# ssh-keygen 
root@d13a9cf36698:/opt/virty/app# ssh-copy-id ubuntu@100.64.45.66
```

Dockerhub push

```bash
VER=1.6.1
docker build --no-cache --pull -t hibiki31/virty-api:$VER ./main
docker push hibiki31/virty-api:$VER
docker build --no-cache --pull -t hibiki31/virty-web:$VER ./web
docker push hibiki31/virty-web:$VER
```

## v2.3.0

<img width="1888" alt="スクリーンショット 2025-06-22 16 34 50" src="https://github.com/user-attachments/assets/62d6d86f-99c2-4ed6-9b3e-5d7fc2450448" />

- VNC Proxy Console対応
- VMのユーザとグループに対応

!!! note
    2025年6月22日 動作確認
    - Update v2.3.0
    - 22b4856cfd0918ff1d4a701680f0471ddf2b0e42

up

```bash
docker compose -f docker-compose.dev.yml up -d
```

logs

```bash
docker compose -f docker-compose.dev.yml logs -f
api-1    | INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
api-1    | INFO  [alembic.runtime.migration] Will assume transactional DDL.
api-1    | ERROR [alembic.util.messaging] Can't locate revision identified by 'e8ddc480d179'
api-1    | FAILED: Can't locate revision identified by 'e8ddc480d179'
```

db init

```bash
docker compose -f docker-compose.dev.yml down
docker volume rm virty_virty-postgres-data
docker volume rm virty_postgres-data
docker volume rm virty_api-data
```

build up

```bash
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml up -d
```

Dockerhub push

```bash
VER=2.3.0
docker build --no-cache --pull -t hibiki31/virty-api:$VER ./api
docker push hibiki31/virty-api:$VER
docker build --no-cache --pull -t hibiki31/virty-web:$VER ./web
docker push hibiki31/virty-web:$VER
docker build --no-cache --pull -t hibiki31/virty-proxy:$VER ./proxy
docker push hibiki31/virty-proxy:$VER
```

## v3.0.3

![image](https://github.com/user-attachments/assets/0c4591d0-dfef-4347-9f08-0d9b4befb5e3)

- チケットの概念追加
- Open vSwitchとポートグループに対応
- Docer hubでのイメージ公開を開始
- Github Actionを追加
- 一番長く運用したバージョン

!!! note
    2025年6月22日 動作確認
    - Fix can't add portgroup
    - 7f1ab96a60361361df51e0bc2259611c725c1f0a

down

```bash
docker compose -f docker-compose.dev.yml down 
docker volume rm virty_virty-postgres-data
```

build up

```bash
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml up -d
```

Dockerhub push

```bash
VER=3.0.3
docker build --no-cache --pull -t hibiki31/virty-api:$VER ./api
docker push hibiki31/virty-api:$VER
docker build --no-cache --pull -t hibiki31/virty-web:$VER ./web
docker push hibiki31/virty-web:$VER
docker build --no-cache --pull -t hibiki31/virty-proxy:$VER ./proxy
docker push hibiki31/virty-proxy:$VER
```

## v4.1.0

<img width="1888" alt="スクリーンショット 2025-06-22 18 29 42" src="https://github.com/user-attachments/assets/2ab3fdd7-a29d-450a-bb61-83485f06b9d6" />

- WEBをNextで実装
- APIにPagenation、Qeuryを実装

!!! note
    2025年6月22日 動作確認
    - 2025/4/25 hibiki31修正 動く
      - Merge commit 'e19cbe202909c9e8ea7796cfb9f68bb1cee04156' into develop
      - 3ffeb3bdc934ec6b7b2c74b3d41fe5a25127af3a
    - 2024/6/30 pagenation修正 Failed `Fix useFormExtraData to store by propertyName`
      - Merge pull request #118 from hibiki31/update/support-pagination
      - 810ad1c051988ac734735f5913d1d9566e4bbe69

down

```bash
docker compose -f docker-compose.dev.yml down 
docker volume rm virty_virty-postgres-data
```

fix `docker-compose.dev.yml` 2025/6/30まではこのバグが入る

```yaml
    ports: 
      - 0.0.0.0:8765:80
```

build up

```bash
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml logs -f
```

Failed `Fix useFormExtraData to store by propertyName`ここでバグが入る

```bash
20.56 Failed to compile.
20.56 
20.56 ./components/JtdForm/index.tsx:18:30
20.56 Type error: Expected 1 arguments, but got 0.
20.56 
20.56   16 | export const JtdForm: FC<Props> = ({ prefixPropertyName, propertyJtd, rootJtd, isEditing, isError = false }) => {
20.56   17 |   const { reset } = useJtdForm(rootJtd);
20.56 > 18 |   const { resetExtraData } = useFormExtraData();
20.56      |                              ^
20.56   19 | 
20.56   20 |   useEffect(
20.56   21 |     () => () => {
------
failed to solve: process "/bin/sh -c yarn build" did not complete successfully: exit code: 1
```

2025/4/25時点のAPIだと5.0.0になっている。`Merge pull request #102 from hibiki31/fix/vm-network-ovs`では4.1.0である。

fix `next/lib/api/index.ts` envが上手く機能していないので以下の修正を行う。push時は消す。

```yaml
const config = new Configuration({
  basePath: "http://100.81.114.103:8765",
  accessToken: () => {
    const { token } = parseCookies();
    return token;
  },
});
```

Dockerhub push

```bash
VER=4.1.0
docker build --no-cache --pull -t hibiki31/virty-api:$VER ./api
docker push hibiki31/virty-api:$VER
docker build --no-cache --pull -t hibiki31/virty-web:$VER ./next
docker push hibiki31/virty-web:$VER
docker build --no-cache --pull -t hibiki31/virty-proxy:$VER ./proxy
docker push hibiki31/virty-proxy:$VER
```

Clean

```bash
docker compose -f docker-compose.dev.yml down
docker volume rm virty_postgres-data 
```
