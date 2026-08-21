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

Agent APIのunit・contract testはfake database/session、固定clock、fake WebAuthn verifier、fake task adapterを使い、
SSH、Ansible、libvirtへ接続しない。少なくとも次を副作用なしで検証する。

- principal、scope、project、node、resourceの認可matrixと既存REST経路
- WebAuthn challenge replay、RP ID・origin不一致、device鍵・DPoP不一致
- lease期限・失効・変更上限、global/device kill switch、breaker、同時実行上限
- idempotency keyの同時retry、request hash相違、stale generation、取消、worker crash、`unknown`
- 監査保存失敗時のfail closedと、秘密入力が監査event・task logへ残らないこと
- VM名、description、task logへprompt injection文字列を入れてもpolicy判断が変化しないこと
- project pool外のstorage/network/image/flavor/nodeをAgentと既存RESTの双方が404/403で拒否すること
- image downloadのDNS rebinding、private/link-local address、redirect、既存fileへの同時downloadを拒否し、
  no-clobber失敗後も既存dataと一時file cleanupが保たれること

Agent関連を検証するときも既存の統合pytest全体は起動せず、安全なtest fileを明示する。

### virty-mcp helper

helperはAPI imageと分離したPython packageであり、stdoutをMCP JSON-RPC以外へ使わない。testではmemory credential storeと
fake HTTP transportを使い、実端末のcredential storeやVirty productionへ接続しない。

`AGENT_TASK_ENCRYPTION_KEY`はAES-256用の32 byteをbase64/base64url化した値である。hex 32 byte値は
base64として48 byteに復号されるため使用せず、`openssl rand -base64 32`等で生成する。

```bash
cd virty_mcp
python -m venv .venv
.venv/bin/pip install -e '.[test]'
.venv/bin/ruff check .
.venv/bin/pytest
```

local Codexへ登録するときは、venv内の絶対pathと内部HTTPS URL、必要ならprivate CA fileを指定する。
秘密鍵やlease tokenを`.codex/config.toml`や環境変数へ記載しない。

```toml
[mcp_servers.virty]
command = "/absolute/path/to/virty-mcp"
env = { VIRTY_AGENT_BASE_URL = "https://virty.internal", VIRTY_TLS_CA_FILE = "/absolute/path/to/ca.pem" }
```

pairingとleaseはMCP lifecycle toolで申請し、承認操作はVirty Web UIのAgent画面で行う。

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

## Agent機能のproduction導入

production以外の管理nodeへ向けたcanaryがない場合、機能flagを段階的に有効化すること自体をWebAuthn付き管理操作として扱う。

1. 最初の7日間は`shadow_mode=true`かつmutation停止でreadとpolicy・監査結果だけを評価する。
2. R1を有効化し、単一resourceの低risk操作、retry、取消、breakerを確認する。
3. R2を有効化し、対象制約とgeneration conflictを確認する。
4. R3は同時1件を維持し、削除・network変更の残存riskを運用者が明示的に受容した場合だけ有効化する。

既存RESTやWeb UIから同じresourceを変更するときは、先にAgent global controlでmutationを停止する。
同期REST mutationはAgentのtarget reservationへ参加しないため、移行期間中の同時変更を安全とは扱わない。

backup、snapshot、帯域外network復旧がない環境では、補償統制が働いても削除後の復元や管理network断からの復旧を
保証できない。`allow_delete_without_recovery`と`allow_network_change_without_oob`を恒常的な既定値として有効にしない。
