# 開発・検証ガイド

## この文書の役割

現行repositoryで再現できる開発環境、変更種別ごとの手順、安全な検証範囲を定義する。
製品利用者向けの導入・運用手順は`mkdocs/`、強制する短い規律は`AGENTS.md`に置く。

## 正本と現在の開発入口

| 対象 | 正本・入口 | 備考 |
|---|---|---|
| 配布構成 | `compose.example.yml` | 公開済みimageを使う実行例。source build用ではない |
| API runtime | `api/Dockerfile`, `api/requirements.txt` | Python runtimeと本番dependency |
| API開発環境 | `api/.devcontainer/compose.yml` | app、PostgreSQL、pgAdmin。appは`sleep`で起動する |
| Web runtime | `vue/Dockerfile`, `vue/package.json`, `vue/pnpm-lock.yaml` | build時にtype-checkとVite buildを行う |
| Web開発環境 | `vue/.devcontainer/` | Node環境とpnpm install |
| DB migration | `api/alembic.ini`, `api/alembic/` | modelを読み込んでrevisionを管理する |
| CI | `.github/workflows/` | 現状は主にAPI/Web image build。全testを代替しない |

現在のcontainer baselineはAPIがPython 3.12、Web buildがNode 24、配布DBがPostgreSQL 18である。
個別packageのversionはmanifestとlockfileを確認し、本書へ完全な一覧を複製しない。

ルートの`dev.sh`は、`git pull`と旧`docker-compose`によるbuild・再起動を行うlegacy deployment scriptである。
OpenAPI生成、local開発、testには使わない。source build用だった`compose.dev.yml`は現行repositoryに存在しない。

## 作業開始

```bash
git status --short --branch
git switch -c codex/docs-refresh
```

Codex worktreeがdetached HEADで作られた場合も、編集前にbranchを作る。既定ブランチは現在`master`だが、
branch名の`docs-refresh`部分はtaskに合わせる。作業時は`origin/HEAD`で既定ブランチを確認する。
既存変更がある場合は所有者を推測して戻さない。

要件変更は`requirements.md`、component境界やflow変更は`architecture.md`、手順変更は本書を先に更新する。

## API開発環境

Composeを使うときは、他のworktreeとvolumeを共有しないtask固有project名を付ける。

```bash
docker compose -p virty-docs-refresh -f api/.devcontainer/compose.yml up -d --build
docker compose -p virty-docs-refresh -f api/.devcontainer/compose.yml exec app \
  bash -lc 'cd /workspaces/api && .devcontainer/post_create.sh'
docker compose -p virty-docs-refresh -f api/.devcontainer/compose.yml exec app bash
```

`docs-refresh`部分はtaskごとに一意な短い名前へ置き換える。
project名はcontainer、network、volumeを分離するが、追跡中のComposeはhostの7799番と8080番を固定公開する。
並列起動する場合は既存projectを停止するか、task固有overrideで空きportへ変更し、`docker compose config`で確認する。

devcontainerのsourceは`/workspaces/api`にmountされる。VS Code Dev Containersではcontainer作成後に
`.devcontainer/post_create.sh`が自動実行されるが、plain Composeでは上記のように明示してruff、pytestなどの
開発toolを導入する。APIとworkerは自動起動しないため、必要なprocessだけを明示して起動する。
以下のAPI用commandは、このapp shell内の`/workspaces/api`で実行する。

```bash
cd /workspaces/api
alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port 7799 --reload
```

非同期taskを動かす検証では、同じprojectの別shellから変更中のsourceを指定してworkerを起動する。

```bash
docker compose -p virty-docs-refresh -f api/.devcontainer/compose.yml exec app \
  bash -lc 'cd /workspaces/api && python worker.py'
```

終了時は対象projectだけを停止する。

```bash
docker compose -p virty-docs-refresh -f api/.devcontainer/compose.yml down
```

## 変更種別ごとの検証

### API・Python

最初に非変更checkで範囲を把握する。自動修正は必要な変更対象に限定し、差分をreviewしてから
repository全体のcheckを再実行する。

```bash
cd /workspaces/api
ruff check .
```

自動修正を行う`ruff check . --fix`は無条件に実行しない。利用者の既存変更を巻き込まないと
確認できた場合だけ変更対象に使う。

pytest suiteは通常のunit testだけではない。`api/tests/env*.json`、専用DB、SSH鍵、download URL、
複数のlibvirt node、起動中workerを要求し、利用者全削除やnode上のVM・network・storage作成と削除を行う。
本番、共有DB、共有nodeでは実行しない。対象を限定してもfixtureの副作用を先に読む。
安全な汎用実行例はないため、隔離した統合test環境を準備し、fixtureを確認してから対象fileを明示して実行する。

前提を用意できない場合は実行したふりをせず、ruff、import、image buildなど実施可能な検証と、
未実施の統合testおよび理由を報告する。`api/test.sh`は`pytest -v -x`のwrapperに過ぎない。

### Web・TypeScript

package managerは`vue/package.json`の`packageManager`を使う。完了確認だけならdev serverは不要である。

```bash
cd vue
corepack enable
pnpm install --frozen-lockfile
pnpm run type-check
pnpm run build
```

dependencyを意図的に変更する場合だけ通常の`pnpm install`でlockfileを更新し、manifestと一緒にreviewする。

`pnpm run lint`は現在fix modeなので、実行後の差分を必ず確認する。CIに近いbuild確認は
task固有tagで`docker build -t virty-web-docs-refresh vue`のように実行できる。

### Container・proxy

変更したimageだけをbuildする。現在のbuild CIはAPIとWebのimage buildが中心で、ruff、pytest、lint、
proxy buildをすべて実行するわけではない。CI badgeだけをlocal検証の代わりにしない。

```bash
docker build -t virty-api-docs-refresh api
docker build -t virty-web-docs-refresh vue
docker build -t virty-proxy-docs-refresh proxy
```

tag末尾はtaskごとに置き換え、既存のrelease tagを上書きしない。

### 文書

- `git diff --check`で空白errorを確認する。
- `docs/README.md`の全link先が存在することを確認する。
- command、path、service名は追跡中のfileに存在することを確認する。
- `mkdocs/`を変更した場合だけ、利用可能な環境で`mkdocs build --strict`を行う。

## API契約を変更する

1. Pydantic schema、routerのrequest/response、operation IDを更新する。
2. APIを開発containerで起動し、`/api/openapi.json`を取得できることを確認する。
3. frontend生成型をOpenAPIから更新する。

```bash
cd vue
pnpm exec openapi-typescript http://localhost:7799/api/openapi.json -o src/api/openapi.d.ts
pnpm run type-check
pnpm run build
```

4. 生成差分が意図した契約変更だけであることを確認し、frontend利用箇所を同時に修正する。

`api/openapi.json`や`web/src/api.d.ts`は現行の追跡pathではない。生成元は実行中API、
追跡する生成物は`vue/src/api/openapi.d.ts`である。生成型を手で整合させない。

## DB schemaを変更する

1. SQLAlchemy modelを変更し、必要なmodelが`api/models.py`からAlembic metadataへ読み込まれることを確認する。
2. disposableな開発DBで新規revisionを生成する。
3. revisionのupgrade/downgrade、constraint、data移行を手でreviewする。
4. 既存相当DBで`alembic upgrade head`を確認し、可能ならdowngrade後の再upgradeも確認する。

```bash
cd /workspaces/api
alembic revision --autogenerate -m "変更内容"
alembic upgrade head
```

既存revisionを履歴から消したり書き換えたりしない。`api/alembic/dev.sh`はdowngrade後に
`alembic/versions/*`を削除する破壊的scriptなので、通常のmigration作業では実行しない。

## Version・release・Git

- 通常の修正ごとにversionを上げない。release対象と決めた変更で、`api/settings.py`のAPI versionと
  `vue/package.json`のapplication versionを同時に確認する。
- Git tag、Docker image tag、画面/API表示versionは別の仕組みから生成される。release時に明示的に整合を確認する。
- commit前に`git --no-pager diff`と`git status --short`を確認し、意図したfileだけをstageする。
  `git diff --cached --check`と`git --no-pager diff --cached`で、新規fileを含むcommit内容を確認する。
- 利用者が保留を指示していなければ、理解可能な単位で日本語のcommit messageを付ける。
- 既定ブランチへマージする直前に最新の既定ブランチを取り込み、競合解消後に影響範囲を再検証する。
