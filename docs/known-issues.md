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
| 開発credential fileのmode・owner・file種別が安全でない | `devctl`が実行user所有のregular non-symlink fileかつ`0600`だけを受理し、境界self-testを標準check前に行う | `./devctl quick`、`./devctl verify` |
| 標準testからSSH、Ansible、libvirt、downloadへ接続 | backend factory、deterministic fake、networkなしquick、internal network verifyを使う | `./devctl verify api` |
| API-001: pathと異なるuser更新、または部分commit | path `username`を更新対象の正本とし、`scopes`と`publickeys`を単一transactionで更新する | user API integration、OpenAPI drift check |
| user作成時のscope・公開鍵の保存漏れ、本人設定による権限変更 | REST・Agentの共通保存処理と、本人から変更可能なfieldだけの専用schemaを使う | user management integration、Web user CRUD E2E |
| password変更後や同名user再作成後のWeb JWT再利用 | DB上のsession generationを照合し、hash変更と同時に更新する | user management integration、migration upgrade/downgrade test |
| API-002: 必須bodyの欠落をoptionalと公開 | VM、network、node、storageの対象9 endpointを必須bodyに統一し、欠落時の422を契約化する | API contract integration、OpenAPI drift check |
| API-003: Pydantic warningによるschema driftの見逃し | FastAPI互換versionを固定し、対象warningをpytestでerrorにする | `./devctl quick api`、`./devctl verify api` |
| WEB-002: 未参照legacy SFCが削除済みaxios adapterへ依存 | 対象5 SFCを削除し、coverageの個別除外も外す | ESLint、forced型check、Vitest、production build |
| TEST-001: lab不要な契約とexternal helperの静的不備 | externalをRuff対象にし、auth/user/project/flavorを標準integrationへ移管する | `./devctl quick api`、`./devctl verify api` |
| TEST-002: worker外部処理の失敗pathを未検証 | SSH timeout、Ansible nonzero、libvirt例外、download metadata失敗をproduction handler境界で注入し、親taskの`error`と後続非実行を検証する | worker failure integration |
| INFRA-002: cleanupが想定名の再構築だけに依存 | mutation前のversion付きmanifestと作成UUIDを永続化し、manifestだけを削除allowlistにする。DB/worker起動前のidentity guardと依存tier間のfailure barrierも必須化する | manifest/cleanup unit test、`infra cleanup`後の独立inventory |
| 実機testによる既存lab資源の再利用・削除 | run ID、exact name、lab側read-only preflight、serial lock、manifest-only cleanupを必須化する | `./devctl infra preflight --config ...`、external support unit test |
| CIがimage buildだけを行いlint・test失敗を見逃す | API、Web、Proxy、MCP jobがcomponent別`devctl verify`を実行し、publish前にも同じgateを置く | GitHub Actions workflow |

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

### TYPE-001: production backend内部がmypy対象外である

- 優先度: P2
- 状態: 未解決
- 影響: maintained API code 74 fileはmypyを通るが、第三者stub不足とlegacy実装のため
  `ansiblelib`、`cloudinitlib`、`paramikolib`、`virtlib`、`xmllib`内部はdirect checkから除外される。
  Protocol境界の利用側は検査できても、production adapter内部の型不整合はruntimeまで残り得る。
- 根拠: [`api/pyproject.toml`](../api/pyproject.toml)のmypy `exclude`と`follow_imports = "skip"`。
- 改善方針: 利用中adapterと未使用legacy moduleを分類し、未使用codeは削除する。利用中adapterは
  第三者objectを局所Protocolまたは最小stubで包み、module単位でmypy対象へ戻す。
- 完了条件: 利用中production adapterがdirect mypy対象となり、全module除外が第三者import単位の
  overrideだけになる。

### WEB-001: Webの自動test coverageが低い

- 優先度: P2
- 状態: 未解決
- 影響: 最新`master`統合後にVitest 100件とPlaywright 3 flowは成功し、認証、API error、
  pagination、task polling、VM/network/node/storage/image dialogの主要分岐を標準verifyへ取り込んだ。
  ただし全srcのcoverageにglobal gateは置いておらず、未抽出のpage/componentには依然として
  測定とtestの薄い範囲が残る。全体coverageの実測はstatements 43.17%、branches 45.65%、
  functions 36.24%、lines 44.74%である。
- 根拠: [`vue/vitest.config.mts`](../vue/vitest.config.mts)と
  [`vue/src/__tests__/`](../vue/src/__tests__)、[`vue/e2e/`](../vue/e2e/)。実測手順と環境は
  [development.md](development.md)に記録する。
- 改善方針: 全体値は推移値として記録し、根拠のないglobal閾値は置かない。抽出済みの認証、
  error整形、pagination、poller helperだけはlines/statements 90%、branches/functions 80%でgateし、
  今後触るpage/componentへ境界値と失敗pathのtestを追加する。
- 完了条件: 残る主要利用者flowへ自動testを追加し、対象helper gateとcoverage推移を標準verifyで
  継続確認できる。全体値だけを目的に、重要度の低いtestを水増ししない。

### INFRA-001: production adapterを使う専用lab testが未実測である

- 優先度: P1
- 状態: 未解決
- 影響: fail-closed preflight、fake integration、cleanup判断は検証済みだが、実SSH、Ansible、libvirt、
  image downloadを組み合わせたsuiteはまだ実行していない。OS、libvirt、network、storage固有の
  差異と、実worker停止・INT・TERM時の診断とcleanupは標準verifyだけでは保証できない。
  提供済みlocal configは親directoryがmode `0775`、fileがmode `0664`であり、`devctl`が求める
  `0700`/`0600`を満たさないため、現状のままではpreflightもfail closedする。
- 根拠: [`api/tests/external/`](../api/tests/external/)と
  [`api/tests/external/infra-config.example.json`](../api/tests/external/infra-config.example.json)。
- 改善方針: operatorが設定のmetadataを`0700`/`0600`へ修正した後、標準verifyと
  read-only preflightの成功を確認し、破壊的実行の別承認を得る。各scenarioは新しいrun IDで
  `happy`、`task-failure`、`worker-stop`、`signal-int`、`signal-term`の順に直列実測する。
  credentialや管理node固有値はrepositoryへ保存しない。
- 完了条件: 5 scenarioが有限時間で診断付き終了し、各run後にrun ID所有の
  DB resource、libvirt resource、remote pathが0件になることを独立inventoryで確認する。

## 更新規則

- 関連codeを変更する前に該当項目を読み、完了条件をtest計画へ含める。
- 問題を解決した変更では、項目を放置して「解決済み」と追記せず、再発防止controlとして残す必要があるか判断する。
  controlとして不要なら削除し、必要なら「現行基盤が防止する失敗」へ移す。
- 数値を更新するときは実行command、日付、対象範囲を確認し、測定不能な値を推測で記載しない。
- external labのcredential、秘密鍵、password、実node名、resource UUID、cleanup logはこの文書へ記録しない。
