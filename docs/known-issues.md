# 既知の問題と改善バックログ

## この文書の役割

現行codeで根拠を確認できる未解決の問題、検証上の制約、次の改善完了条件を管理する。
個別taskの進捗日誌やcommit履歴は置かず、解決時は同じ変更でcode、test、関連文書を更新する。
安全な開発手順は[development.md](development.md)、component境界は[architecture.md](architecture.md)を正本とする。

優先度は次の意味で使う。

| 優先度 | 判断基準 |
|---|---|
| P1 | 誤ったresource更新、API契約不整合、remote資源残留など、正しさや安全性へ直接影響する |
| P2 | testの検出力、型保証、保守性が不足し、将来の変更で不具合を見逃しやすい |
| P3 | 現行機能は保てるが、実行時間や開発体験をさらに改善できる |

## 現行基盤が防止する失敗

次の項目は単なる実行手順ではなく、再発させないために維持する設計上のcontrolである。

| 失敗mode | 現在の防止策 | 回帰を検出する入口 |
|---|---|---|
| Web型checkの重複実行と生成型更新との競合 | `quick`と`verify`で型checkを各1回に限定し、生成後のforced checkを順序付ける | `./devctl quick web`、`./devctl verify web` |
| test失敗の終了code消失、syntax errorの見逃し | `devctl`が終了codeを集約し、unit contractがexternalを含むPython sourceをAST解析する | `./devctl quick api` |
| worktree間のport、container、network、volume、DB、依存cache衝突 | canonical pathのSHAからCompose project名を生成し、portをloopback自動割当にする | 2 worktreeでの`up`、`quick`、`verify`、片側`clean` |
| image tagやpost-create installによる環境drift | base imageをtagとdigestで固定し、Python依存lockと`pnpm --frozen-lockfile`をbuild layerへ入れる | `./devctl quick`、production image build |
| 標準testからSSH、Ansible、libvirt、downloadへ接続 | backend factory、deterministic fake、networkなしquick、internal network verifyを使う | `./devctl verify api` |
| 実機testによる既存lab資源の再利用・削除 | run ID、exact name、read-only collision preflight、serial lock、独立cleanupを必須化する | `./devctl infra --config ...`のpreflight |
| CIがimage buildだけを行いlint・test失敗を見逃す | API、Web、Proxy jobがcomponent別`devctl verify`を実行し、publish前にも同じgateを置く | GitHub Actions workflow |

## 未解決の課題

### ENV-001: pristine Linux hostでの受入を自動化していない

- 優先度: P2
- 状態: 未解決
- 影響: cold相当の計測はbase image取得済みhostで依存layerから再buildした値であり、Docker Engineと
  Compose以外の言語runtimeを持たない新規host、空のDocker layer cache、低速networkを組み合わせた
  end-to-end受入ではない。`devctl`のhost tool preflightとcontainer内実行は確認済みでも、将来の変更が
  暗黙にhost Python、Node、pnpmへ依存しないことを継続的に保証できない。
- 根拠: [development.md](development.md)の基準計測条件と[`devctl`](../devctl)の`require_base_tools`。
- 改善方針: disposable Linux VMまたは専用CI runnerへDocker EngineとComposeだけを導入し、空cacheの
  `quick`・`verify`、2回目のwarm実行、2 worktree同時実行を定期的に行う。host PATHにPython、Node、pnpmが
  なくても成功することを明示検査する。
- 完了条件: pristine環境で全commandが成功し、cold/warm時間、dependency cache hit、型check各1回、
  worktree資源の非共有をCI artifactまたは保守記録で確認できる。

### API-001: 利用者更新endpointがpathのusernameを使用しない

- 優先度: P1
- 状態: 未解決
- 影響: `PUT /api/users/{username}`のpathと実際の更新対象が一致しない。handlerはbodyの
  `request.username`で対象を選ぶため、URLと異なる利用者を更新できる。生成OpenAPIにもpath parameterが
  現れず、clientが正しい契約を構築できない。またpublic keyをcommitした後にscopeを別commitで更新するため、
  後半が失敗すると利用者情報が部分更新される。
- 根拠: [`api/user/router.py`](../api/user/router.py)の`update_user`と
  [`api/user/schemas.py`](../api/user/schemas.py)の`UserForUpdate`。
- 改善方針: handlerへ`username: str`を受け取り、検索とscope更新の対象をpath値へ統一する。
  `UserForUpdate`は`UserForCreate`を継承せず、更新可能な`scopes`と`publickeys`だけを持つschemaへ分離する。
  public keyとscopeは一つのtransactionで更新する。
- 完了条件: path以外の利用者を変更できないintegration test、存在しない利用者の404、OpenAPIと
  `vue/src/api/openapi.d.ts`の再生成、失敗時に部分更新しないtestが同じ変更で成功する。

### API-002: request bodyの型とoptional契約が一致しない

- 優先度: P1
- 状態: 未解決
- 影響: VM、network、node、storageの9 endpointは非optional model型へ`None`をdefault指定しており、
  OpenAPIではbodyがoptionalだがhandlerはmodelを前提に処理する。現在は既存wire contractを変えないため
  `type: ignore[assignment]`を使用しており、型checkだけではbody欠落時の挙動を保証できない。
- 根拠: [`api/domain/router_task.py`](../api/domain/router_task.py)、
  [`api/network/router_task.py`](../api/network/router_task.py)、
  [`api/node/router_task.py`](../api/node/router_task.py)、
  [`api/storage/router.py`](../api/storage/router.py)、
  [`api/storage/router_task.py`](../api/storage/router_task.py)。
- 改善方針: endpointごとにbodyを必須にするか、`Model | None`として欠落を明示処理するかを決定する。
  暗黙のcontract変更を避け、client影響を確認して段階的に移行する。
- 完了条件: body欠落時のstatusを固定するcontract test、行単位ignoreの削除、OpenAPI生成差分のreview、
  Web利用箇所の型checkが成功する。

### API-003: schema生成時にPydantic warningが発生する

- 優先度: P2
- 状態: 未解決
- 影響: `./devctl verify api`のintegration testで`UnsupportedFieldAttributeWarning`が24件発生する。
  現時点のtestは成功するが、alias metadataが無視される可能性をwarningが示しており、将来の
  FastAPI/Pydantic更新時にrequest・response名が変わっても見落としやすい。
- 根拠: 認証とworker integrationで`username`、`password`、node field等のalias生成時に再現する。
  現在の固定versionは[`api/requirements.lock`](../api/requirements.lock)を正本とする。原因がapplication
  schema、FastAPIのdependency wrapping、version組合せのどこにあるかは未切り分けである。
- 改善方針: 最小schemaでwarningを再現し、camelCaseの入力・出力・OpenAPIをassertする。
  原因に応じてschema宣言または互換versionを修正する。
- 完了条件: warningが0件となり、対象warningをerror扱いにしてもunit/integration/OpenAPI生成が成功する。

### TYPE-001: production backend内部がmypy対象外である

- 優先度: P2
- 状態: 未解決
- 影響: maintained API code 74 fileはmypyを通るが、第三者stub不足とlegacy実装のため
  `ansiblelib`、`cloudinitlib`、`ovslib`、`paramikolib`、`virtlib`、`xmllib`内部はdirect checkから除外される。
  Protocol境界の利用側は検査できても、production adapter内部の型不整合はruntimeまで残り得る。
- 根拠: [`api/pyproject.toml`](../api/pyproject.toml)のmypy `exclude`と`follow_imports = "skip"`。
- 改善方針: 利用中adapterと未使用legacy moduleを分類し、未使用codeは削除する。利用中adapterは
  第三者objectを局所Protocolまたは最小stubで包み、module単位でmypy対象へ戻す。
- 完了条件: 利用中production adapterがdirect mypy対象となり、全module除外が第三者import単位の
  overrideだけになる。

### WEB-001: Webの自動test coverageが低い

- 優先度: P2
- 状態: 未解決
- 影響: 2026-08-22の全src基準はstatements 6.99%、branches 6.54%、functions 3.95%、lines 7.29%である。
  validation、認証middleware、task変換、pagination、主要dialog smokeは開始したが、主要page、失敗response、
  form submit、router遷移の回帰検出は限定的である。
- 根拠: [`vue/vitest.config.mts`](../vue/vitest.config.mts)と
  [`vue/src/__tests__/`](../vue/src/__tests__)。実測手順と環境は[development.md](development.md)に記録する。
- 改善方針: 変更するmoduleへ境界値と失敗pathのtestを追加し、認証、resource操作dialog、task表示、
  API error通知を優先する。低い現状値に合わせた一律閾値は置かず、対象moduleの根拠が揃ってから
  module別または変更差分のgateを導入する。
- 完了条件: 主要な利用者flowごとに最低1つの自動testがあり、coverage推移をCIで比較できる。

### WEB-002: 未参照componentが削除済みAPI adapterへ依存する

- 優先度: P2
- 状態: 未解決
- 影響: 5つのlegacy SFCが存在しない`@/axios/index`をimportする。現行routeから未参照のためbuildは通るが、
  再利用すると直ちに失敗し、coverage toolもparseできないため明示除外している。
- 根拠: `NodeRolePatch.vue`、`StoragePoolAddDialog.vue`、`StoragePoolJoinDialog.vue`、
  `DomainAddTicketsDialog.vue`、`DomainGroupPut.vue`と[`vue/vitest.config.mts`](../vue/vitest.config.mts)。
- 改善方針: route・component参照を再確認し、不要なら削除する。必要なら`openapi-fetch`を使う現行
  [`vue/src/api/index.ts`](../vue/src/api/index.ts)へ移行し、component testを追加する。
- 完了条件: `@/axios/index`参照とcoverage除外がなくなり、lint、forced型check、Vitest、production buildが成功する。

### TEST-001: external suiteの静的検査範囲が限定的である

- 優先度: P2
- 状態: 未解決
- 影響: standard quickはexternal PythonのAST parseを行うが、`tests/external`はRuffとmypyの対象外である。
  endpoint typo、response未assert、fixture順序依存など、実機labを使わず検出できる不具合が残りやすい。
- 根拠: [`api/pyproject.toml`](../api/pyproject.toml)と
  [`api/tests/unit/test_source_contracts.py`](../api/tests/unit/test_source_contracts.py)。
- 改善方針: endpointとpayloadのcontractをfake integrationへ移し、externalにはproduction adapter固有の確認だけを残す。
  external helperを段階的にRuff対象へ入れ、設定modelとcleanup判断はunit testする。
- 完了条件: external sourceのRuffが成功し、主要endpointのpath・status・response assertionをlabなしで検証できる。

### TEST-002: fake backendの失敗pathをintegration testしていない

- 優先度: P2
- 状態: 未解決
- 影響: 現行fake backendは成功値または空inventoryだけを返し、worker integrationもtaskが`finish`する
  happy pathを確認する。SSH timeout、Ansible nonzero、libvirt例外、download metadata失敗時にtaskが
  `error`へ遷移し、message・logを残し、依存taskを誤実行しないことを標準verifyで保証していない。
- 根拠: [`api/module/backends.py`](../api/module/backends.py)のfake実装と
  [`api/tests/integration/test_worker_task.py`](../api/tests/integration/test_worker_task.py)。
- 改善方針: 呼出単位でtimeout、例外、nonzero、遅延を選べるfault-injectable fakeを追加する。
  production adapterの例外型をbackend境界で正規化し、workerの診断情報と依存task状態をintegration testする。
- 完了条件: backend失敗scenarioが30秒以内に終了し、task UUID、`error` status、message、logをassertでき、
  後続taskが外部操作を実行しない。

### INFRA-001: production adapterを使う専用lab testが未実測である

- 優先度: P1
- 状態: 未解決
- 影響: fail-closed preflight、fake integration、cleanup判断は検証済みだが、実SSH、Ansible、libvirt、
  image downloadを組み合わせたsuiteは専用lab設定がないため未実行である。OS、libvirt、network、storage固有の
  差異と、実worker停止時の診断・cleanupは標準verifyだけでは保証できない。
- 根拠: [`api/tests/external/`](../api/tests/external/)と
  [`api/tests/external/infra-config.example.json`](../api/tests/external/infra-config.example.json)。
- 改善方針: disposableな専用labを用意し、通常成功、task失敗、worker停止、INT/TERMを順番に実測する。
  credentialや管理node固有値はrepositoryへ保存しない。
- 完了条件: 各scenarioが有限時間で診断付き終了し、run ID資源とremote pathが0件になることを独立inventoryで確認する。

### INFRA-002: cleanupが作成資源の永続manifestを持たない

- 優先度: P2
- 状態: 未解決
- 影響: 現行cleanupはcollision preflight後、configとrun IDからexact resource名・pathを再構築する。
  通常の衝突や部分一致削除は防げるが、run途中でconfigが失われた場合や、APIが返したUUIDと想定名が
  ずれた場合に「実際に作成成功した資源」だけを証明してcleanupする台帳がない。
- 根拠: [`api/tests/external/conftest.py`](../api/tests/external/conftest.py)、
  [`api/tests/external/cleanup.py`](../api/tests/external/cleanup.py)、[`devctl`](../devctl)のinfra cleanup。
- 改善方針: 作成成功直後にresource種別、UUID、node、exact pathをproject-scoped volumeのmanifestへ追記し、
  cleanupはmanifestを第一の対象にする。config/run ID再構築はread-only診断用fallbackに限定する。
- 完了条件: 部分作成、途中失敗、config変更、cleanup再試行をunit/fake integrationで再現し、manifest記載外の
  resourceを削除しないことを確認する。

## 更新規則

- 関連codeを変更する前に該当項目を読み、完了条件をtest計画へ含める。
- 問題を解決した変更では、項目を放置して「解決済み」と追記せず、再発防止controlとして残す必要があるか判断する。
  controlとして不要なら削除し、必要なら「現行基盤が防止する失敗」へ移す。
- 数値を更新するときは実行command、日付、対象範囲を確認し、測定不能な値を推測で記載しない。
- external labのcredential、秘密鍵、password、実node名、resource UUID、cleanup logはこの文書へ記録しない。
