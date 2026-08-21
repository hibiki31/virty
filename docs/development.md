# 開発・検証ガイド

## この文書の役割

現行repositoryで再現できる開発環境、変更種別ごとの検証手順、安全な外部結合testの境界を定義する。
製品利用者向けの導入・運用手順は`mkdocs/`、エージェント向けの短い強制規則は`AGENTS.md`に置く。

## 前提と唯一の入口

hostに必要なのはLinux、Docker Engine、Docker Compose v2、Bashと標準的なLinux userlandだけである。
`devctl`は利用する`realpath`、`sha256sum`、`install`、`flock`等を開始時に検査する。Python、Node.js、
pnpm、PostgreSQLをhostへ導入しない。repository rootの`./devctl`を唯一の開発入口とし、文書やCIから
個別の`docker compose`、`pytest`、`pnpm`を直接呼ばない。

`devctl`はworktreeの絶対pathからproject名を自動生成する。同じrepositoryの別worktreeはcontainer、
network、volume、依存cache、host portを共有しない。利用者が`-p`や空きportを選ぶ必要はない。
API/WebのDev Containerも同じroot Compose serviceを使う。初期化scriptはcanonicalなrepository pathの
SHA-256先頭12桁からCLIと同じproject名を作り、repository rootのignored `.env`へ保存する。他の環境値は
保持するため、同名directoryの別worktreeとも資源を共有しない。remote userと共有serviceはhost UID/GIDへ
合わせ、固定host port forwardは持たない。

| 目的 | コマンド | 実行内容 |
|---|---|---|
| 編集中の高速確認 | `./devctl quick` | APIとWebの安全なcheckを並列実行 |
| APIだけ高速確認 | `./devctl quick api` | Ruff、mypy、unit test |
| Webだけ高速確認 | `./devctl quick web` | ESLint、incremental型check、Vitest |
| 完了前の必須確認 | `./devctl verify` | API、Web、Proxyの完全検証とimage build |
| 対象限定の完全確認 | `./devctl verify api\|web\|proxy` | CIや原因調査用。完了時は引数なしを使う |
| 常駐環境 | `./devctl up` | DB、API、worker、Viteを起動しURLを表示 |
| 状態確認 | `./devctl ports` / `./devctl logs [service]` | 割当portまたはlogを表示 |
| container shell | `./devctl shell api\|web` | 対象の開発containerへ入る |
| 終了・掃除 | `./devctl down` / `./devctl clean` | 現worktreeのprojectだけを停止・削除 |
| 生成型更新 | `./devctl generate openapi\|web-types` | 明示した追跡済み生成型だけを更新 |
| 実機test | `./devctl infra --config /absolute/path/env.json` | 専用labで外部結合testを直列実行 |

各コマンドは前提を検査し、失敗した検査の非0終了codeを保持する。`quick`と`verify`はsourceを
自動修正しない。修正commandを使う場合はcontainer shellから対象fileを限定し、差分をreviewする。

## Compose構成と分離規則

`compose.dev.yml`は開発、check、tool、外部結合testをprofilesとone-shot serviceで分離する。

- check serviceはhost portを公開しない。開発用Web/APIとpgAdminは`127.0.0.1`の自動割当portだけを使う。
- `quick` serviceはnetwork namespaceを持たず、`verify` serviceは外部へrouteしないinternal networkだけを使う。
- 開発DBと依存cacheはCompose project配下のnamed volume、verify用DBはtmpfsを使う。
- 開発serviceの前にproject内のone-shot初期化serviceがSSH/data/node_modules volumeをhost UID/GIDへ揃える。
- `container_name`、固定volume `name`、external volumeを使わず、Compose projectによる分離を保持する。
- PostgreSQLは配布環境と同じ18系を使い、healthcheck成功後にmigrationとtestを開始する。
- Python、Node、PostgreSQL、pgAdminのimageと開発toolは追跡fileで固定し、container起動後に
  `apt`、`pip install`、`pnpm install`で環境を作り直さない。
- source変更では依存layerを再構築しないCOPY順とBuildKit cacheを維持する。
- `clean`は現worktree由来のprojectだけを対象にする。`docker system prune`や他projectのvolume削除を
  開発手順へ含めない。

## 高速確認と完全検証

### API

`quick api`はDB、SSH、実libvirt node、外部URLを使わず、次を一度ずつ実行する。

1. Python 3.12をtargetにした`ruff check`。標準実行から除外するexternal sourceもunit contractでAST解析する。
2. maintained application codeとunit/integration testに対するincremental mypy。
3. `tests/unit`だけのpytest。依存manifestと完全lockの整合もここで検査する。

`verify api`は同じ静的検査を重複させず、freshなPostgreSQLへAlembic migrationを適用し、
`tests/integration`を実行する。worker integrationではSSH、Ansible、libvirt、download backendを
deterministic fakeへ差し替える。最後にproduction API imageをbuildする。
FastAPI schemaから生成したWeb OpenAPI型も一時volume内で追跡版と比較し、API契約driftを検出する。

pytestは`unit`、`integration`、`external`を物理的に分ける。標準testpathsはunitとintegrationだけで、
externalを暗黙に収集しない。testは単独実行可能で、file名順、共有DBの残存状態、実行中workerへ依存させない。
unitは10秒、integrationは60秒、fake task待機は30秒を上限とし、timeout時はtask UUID、status、logを出す。

### Web

`quick web`は次を一度ずつ実行する。

1. 非修正modeのESLint。warningも失敗にする。
2. `vue-tsc --build`によるincremental型check。
3. watchへ入らないVitest unit test。

`verify web`はVite buildでrouter、component、auto-import型を生成した後、forced型check、ESLint、Vitestを
一度ずつ実行し、そのbuild layerからproduction imageを作る。生成結果は一時container内で追跡版と比較し、
不一致ではworking treeを書き換えず失敗する。OpenAPI型もAPI schemaから再生成して比較する。
更新が必要な場合だけ`./devctl generate web-types`または`./devctl generate openapi`を使う。

coverage summaryは`verify web`とCIのlogへ記録するが、既存codeへ根拠のない一律閾値は設定しない。新規・変更する処理には、
境界値、失敗path、API response変換を対象にしたtestを追加する。

### 2026-08-22の基準計測

Docker Engine 29.7.2、Compose 5.4.0、x86_64、8 CPU、62.7 GiB memoryの開発hostで計測した。
base imageは取得済みで、cold相当はdevelopment Dockerfile変更により依存layerから再buildした値である。
wall timeは環境比較用の基準であり、性能SLOではない。

| 実行 | wall time | 確認内容 |
|---|---:|---|
| `./devctl quick` cold相当 | 50.90秒 | API/Web development・check layerを再buildして成功 |
| `./devctl quick` warm | 12.00秒 | install layerはcache hit、API/Webを並列実行 |
| `./devctl quick api` warm | 9.28秒 | Ruff、mypy、unit testを各1回 |
| `./devctl quick web` warm | 14.19秒 | ESLint、incremental型check、Vitestを各1回 |
| `./devctl verify` warm | 75.31秒 | migration、integration、生成型drift、coverage、3 production image |

warm logでは`apt`、`pip install`、`pnpm install`の再実行がなく、API/Web各componentの型checkは1回だった。
引数なしquickはcomponent別実行時間の合計ではなく、並列実行時間で完了した。初回実装時の権限不備を含む
失敗計測は基準値へ採用せず、修正後の成功runだけを記録している。

## 実機SSH・Ansible・libvirt test

`tests/external`は標準verifyと通常CIから分離する。Compose projectを分けても管理node上のVM、network、
storageは自動分離されないため、次の条件をすべて満たす場合だけ`devctl infra`で実行する。

- `api/tests/external/infra-config.example.json`をrepository外へcopyし、絶対pathで渡す。
- operatorが必要なSSH接続と空き容量を事前確認する。`devctl`のpreflightはnested構造、専用lab宣言、
  URL、path、必須resource suffixを資源作成前に検査する。
- resource名へrun IDを付け、既存resourceをskip、再利用、削除しない。
- cleanupを有効化する前に、管理nodeのexact resource名とremote pathをread-onlyでinventoryし、衝突時は終了する。
- testを直列実行し、fixture finalizerに加えて独立cleanup containerを`devctl`の終了trapから再実行する。
  成功・失敗・INT・TERMのすべてでrun IDに一致する資源だけを回収する。
- worker待機、Ansible、downloadに有限timeoutを設ける。

設定不足、共有環境の疑い、既存resourceとの衝突があれば変更前にfail closedする。cleanup失敗時は診断用の
Compose project、DB、SSH volumeを削除せず、同じconfig、run ID、projectを使う復旧commandを表示する。
実機test未実施の場合は、標準verifyの結果と未実施理由を完了報告へ記載する。

## API契約と生成型

API契約を変更した場合はschema、router、利用側を同じ変更で更新し、次を実行する。

```bash
./devctl generate openapi
./devctl verify
```

OpenAPI schemaと`openapi-typescript`の出力は一時directoryを介してone-shot container間で渡す。
host portやhost pnpmを使わず、最後だけhost userとして追跡fileへinstallするため所有者を変えない。
追跡する`vue/src/api/openapi.d.ts`を手編集しない。

## DB schema変更

1. SQLAlchemy modelとAlembic metadataへのimportを更新する。
2. `./devctl up`後に`./devctl shell api`からdisposableな開発DBへrevisionを生成する。
   shellはhost UID/GIDで入るため、生成fileをroot所有にしない。
3. revisionのupgrade、downgrade、constraint、data移行をreviewする。
4. `./devctl verify api`でfresh DBへのupgradeとintegration testを確認する。

既存revisionを履歴から消したり書き換えたりしない。`alembic downgrade base`やversion file削除を含む
legacy scriptは通常手順に使わない。

## CI、文書、Git

- CIはAPI、Web、Proxyを分離して`./devctl verify <component>`を実行する。tag publishも同じverifyを
  registry loginより前に必須化し、component別cache scopeを使う。
- `docs/development.md`を手順の正本とし、component READMEやCIへcommand列を複製しない。
- 文書だけの変更でも`git diff --check`と内部linkの存在を確認する。
- 完了前に引数なしの`./devctl verify`を実行する。実行できない項目と理由は明記する。
- commit前に`git status --short`、`git diff`、`git diff --cached --check`、staged diffを確認する。
- release時だけ`api/settings.py`と`vue/package.json`のversion整合を確認する。
