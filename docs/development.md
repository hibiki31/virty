# 開発・検証ガイド

## この文書の役割

現行repositoryで再現できる開発環境、変更種別ごとの検証手順、安全な外部結合testの境界を定義する。
製品利用者向けの導入・運用手順は`mkdocs/`、エージェント向けの短い強制規則は`AGENTS.md`に置く。
現行codeに残る検証gapと改善完了条件は[known-issues.md](known-issues.md)を正本とする。

## 前提と唯一の入口

hostに必要なのはLinux、Docker Engine、Docker Compose v2、Bashと標準的なLinux userlandだけである。
`devctl`は利用する`realpath`、`sha256sum`、`install`、`flock`等を開始時に検査する。Python、Node.js、
pnpm、PostgreSQLをhostへ導入しない。repository rootの`./devctl`を唯一の開発入口とし、文書やCIから
個別の`docker compose`、`pytest`、`pnpm`を直接呼ばない。

`devctl`はworktreeの絶対pathからproject名を自動生成する。同じrepositoryの別worktreeはcontainer、
network、volume、依存cache、host portを共有しない。利用者が`-p`や空きportを選ぶ必要はない。
`devctl`は初回実行時にJWT、Agent lease、task暗号化、PostgreSQLの開発credentialを生成し、
worktree固有のignored `/.env`へ`0600`で保存する。追跡fileに固定keyやpasswordを置かず、
このcredential fileを別worktreeやproductionと共有しない。既存fileは実行user所有のregular
non-symlink fileかつ`0600`の場合だけ利用し、`quick`と`verify`はmode、owner、symlink、special fileの
contract self-testをcontainer起動前に行う。
API/WebのDev Containerも同じroot Compose serviceを使う。初期化scriptはcanonicalなrepository pathの
SHA-256先頭12桁からCLIと同じproject名を作り、repository rootのignored `.env`へ保存する。他の環境値は
保持するため、同名directoryの別worktreeとも資源を共有しない。remote userと共有serviceはhost UID/GIDへ
合わせ、固定host port forwardは持たない。

| 目的 | コマンド | 実行内容 |
|---|---|---|
| 編集中の高速確認 | `./devctl quick` | API、Web、MCP helperの安全なcheckを並列実行 |
| APIだけ高速確認 | `./devctl quick api` | Ruff、mypy、unit test |
| Webだけ高速確認 | `./devctl quick web` | ESLint、incremental型check、Vitest |
| MCPだけ高速確認 | `./devctl quick mcp` | Ruff、unit・contract test |
| 完了前の必須確認 | `./devctl verify` | API、Web、全層E2E、Proxy、MCP helperの完全検証とimage build |
| 対象限定の完全確認 | `./devctl verify api\|web\|e2e\|proxy\|mcp` | CIや原因調査用。完了時は引数なしを使う |
| 常駐環境 | `./devctl up` | DB、API、worker、Viteを起動しURLを表示 |
| 状態確認 | `./devctl ports` / `./devctl logs [service]` | 割当portまたはlogを表示 |
| container shell | `./devctl shell api\|web` | 対象の開発containerへ入る |
| 終了・掃除 | `./devctl down` / `./devctl clean` | 現worktreeのprojectだけを停止・削除 |
| 生成型更新 | `./devctl generate openapi\|web-types` | 明示した追跡済み生成型だけを更新 |
| 実機の事前確認 | `./devctl infra preflight --config /absolute/path/env.json` | lab資源を変更せず、設定と到達性を確認 |
| 実機test | `./devctl infra --config /absolute/path/env.json [--scenario SCENARIO]` | 承認済み専用labで指定scenarioを実行 |

各コマンドは前提を検査し、失敗した検査の非0終了codeを保持する。`quick`と`verify`はsourceを
自動修正しない。修正commandを使う場合はcontainer shellから対象fileを限定し、差分をreviewする。

## Compose構成と分離規則

`compose.dev.yml`は開発、check、tool、外部結合testをprofilesとone-shot serviceで分離する。

- check serviceはhost portを公開しない。開発用Web/APIとpgAdminは`127.0.0.1`の自動割当portだけを使う。
- `quick` serviceはnetwork namespaceを持たず、`verify` serviceは外部へrouteしないinternal networkだけを使う。
- 開発DB、external実機testの復旧用DB、依存cacheはCompose project配下のnamed volume、
  verify用DBはtmpfsを使う。external DB volumeはscenario、cleanup、独立inventoryがすべて成功した場合だけ削除する。
- 開発serviceの前にproject内のone-shot初期化serviceがSSH/data/node_modules volumeをhost UID/GIDへ揃える。
- `container_name`、固定volume `name`、external volumeを使わず、Compose projectによる分離を保持する。
- PostgreSQLは配布環境と同じ18系を使い、healthcheck成功後にmigrationとtestを開始する。
- Python、Node、PostgreSQL、pgAdminのimageと開発toolは追跡fileで固定し、container起動後に
  `apt`、`pip install`、`pnpm install`で環境を作り直さない。
- source変更では依存layerを再構築しないCOPY順とBuildKit cacheを維持する。
- `clean`は現worktree由来のprojectだけを対象にする。`docker system prune`や他projectのvolume削除を
  開発手順へ含めない。

## 高速確認と完全検証

### 全層E2E

全層E2Eは`./devctl verify e2e`を入口とし、引数なし`verify`と専用CI jobにも組み込む。
引数なし`verify`ではAPI・Web・MCPの並列検証が成功してから全層E2Eを実行し、2種類の
browser suiteが同時にCPUを奪い合わないようにする。
配布用Web bundleから実API、専用PostgreSQL、workerまでを通し、SSH・Ansible・libvirtなどの
外部境界だけをdeterministic fakeへ置き換える。既存のbrowser側API代替testはWeb単体の
言語・表示幅・操作性の検証として維持する。

全層E2E用DBとnetworkはAPI integrationから分離し、host portを公開しない。testの前提dataは
試験専用DBへ準備し、各testを単独実行可能にする。初期設定・認証切れ、権限差、Projectとgrant、
resource一覧とfilter、VM作成、taskの成功・失敗を対象とする。HTTP responseの代替だけで成功させず、
実APIの結果とtaskの終端状態を確認する。実機境界は標準verify後の専用lab受入で補完する。

試験専用entrypointはproduction appをそのままmountし、productionと同じstartup処理を行う。
`/api/__e2e/`配下のreset・故障注入・期限切れtoken・task診断はこのentrypointだけに存在し、通常APIと
OpenAPIへ追加しない。`VIRTY_TESTING=1`、`VIRTY_BACKEND_MODE=e2e`、PostgreSQLの専用DB名
`virty_test_e2e`を必須とし、reset直前にも実接続先DBを検査する。未完了taskがあるresetを拒否し、
browserは有限時間で完了を待つ。resetのDB lock競合はrollbackして409を返し、browserが上限時間内で
再試行する。fake adapterはAPIとworkerで状態を共有し、対応していない外部操作は
成功を返さず拒否する。

失敗時も`devctl`がcleanup前に`/.artifacts/e2e/<run_id>/`へreport、HTTP/taskの診断、service状態を
取り出す。reportにはtest名、source位置、結果、時間を、診断にはHTTP method/path/statusと
task UUID/status/error code、許可された例外型と実在するsource位置だけを記録する。
認証入力、cookie、response本文、任意log、画面snapshot、
trace、videoは保存しない。まずreportの失敗位置と対応する診断を照合し、同じ`verify e2e`で再確認する。
CIでも同じ成果物だけを7日間保持する。実機のraw logやmanifestをこのartifactへ混ぜない。

専用lab受入は設定本文を表示せずread-only preflightを行い、別途承認された5 scenarioを
直列実行する。各runの独立inventoryが残存0件を証明できなければ後続scenarioへ進まない。

| 対象 | 標準検証の責任 | 専用labの責任 |
|---|---|---|
| 初期設定・認証・権限 | browserから実APIでsetup/login、session失効、管理者・member・非member境界を確認 | lab接続用の最小setupのみ |
| Project・grant | 作成・変更後の再取得、grant外資源の拒否、一覧filterを確認 | VM作成の前提を準備 |
| VM・非同期task | UIから投入し実workerの終端状態とinventory反映、失敗表示を確認 | disk、libvirt XML、power、CD-ROM、networkの実状態を確認 |
| node・storage・network・image | API契約、認可、UI表示、外部失敗時のtask制御を確認 | SSH/SFTP/sudo、Ansible、作成・download・copy・削除のpostconditionを確認 |
| worker停止・process signal | 状態遷移とcleanup判断をunit/integrationで確認 | worker停止・再開とINT/TERM後の独立inventoryを確認 |
| 日英・画面幅・入力分岐 | unitとAPI代替型browser testで検証 | 対象外 |

各層の成功はその層の境界だけを保証する。全層E2Eのfake adapter成功を実libvirtの動作実績として
扱わず、標準検証と実機受入の結果を別々に記録する。

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
認証、user、project、flavorのようにlab固有adapterを使わないAPI契約は`integration`で検証し、
external suiteへ重複させない。

API errorのcontract testは、通常APIとAgent APIの4xx・5xxが共通envelopeを返すこと、codeが
`lower_snake_case`であること、parameterが許可型だけであることを確認する。422ではfield errorを
安定したcodeへ正規化し、入力値、validatorのraw message、内部contextがresponseへ含まれないことを
検査する。旧`detail` string・listやAgent API固有形式は互換対象にせず、testで再導入を拒否する。

### Web

`quick web`は次を一度ずつ実行する。

1. 非修正modeのESLint。warningも失敗にする。
2. `vue-tsc --build`によるincremental型check。
3. watchへ入らないVitest unit test。

`verify web`はVite buildでrouter、component、auto-import型を生成した後、forced型check、ESLint、Vitestを
一度ずつ実行し、そのbuild layerからproduction imageを作る。生成結果は一時container内で追跡版と比較し、
不一致ではworking treeを書き換えず失敗する。OpenAPI型もAPI schemaから再生成して比較する。
更新が必要な場合だけ`./devctl generate web-types`または`./devctl generate openapi`を使う。

日英辞書のcontract testはleaf key、補間parameter、複数形の定義を比較し、片方だけの追加、空文言、
不一致を失敗にする。locale処理は保存値、browser言語、英語fallbackの優先順位と不正保存値をunit testし、
Vue・Vuetify、`html lang`、route title、日時・数値が一つのlocaleへ追従することを検査する。
Playwrightでは英語localeを明示した既存critical flowに加え、日本語への切替、再読込後の保持、login・初期設定、
Vuetify組込文言を確認する。task logなど原文dataがlocale切替で変化しないことも検査する。

coverage summaryは`verify web`とCIのlogへ記録するが、既存codeへ根拠のない一律閾値は設定しない。新規・変更する処理には、
境界値、失敗path、API response変換を対象にしたtestを追加する。
認証、API error整形、pagination、task pollingのように複数画面へ影響する共通処理はpure helperへ分離し、
lines/statements 90%以上、branches/functions 80%以上を対象moduleの回帰gateとする。全体coverageは
重要flowの代替指標にせず、同じ対象範囲の推移を比較するために記録する。

API代替型のWeb受入は`verify web`で実行し、`quick web`へ含めない。Playwrightは
production buildと同じbundleをHTTP専用test runtimeで配信し、browser側の`page.route`で必要なAPI responseを
deterministicにinterceptする。production Nginx設定は別のsmoke testで構文とHTTP配信を確認し、
別のAPI stub serviceは起動しない。
認証redirect、一覧から詳細への遷移、主要dialogのdesktop/narrow viewportを少数のcritical flowとして確認し、
external labへは接続しない。
VitestとAPI代替型browser testは2 worker、全層E2Eは1 workerで実行し、worktreeを並行検証するときの
CPU競合を抑える。再試行で失敗を隠さず、各testのtimeout内に完了することを要求する。

### 2026-09-22の基準計測

最新`master`統合後、8 CPUのLinux開発hostで再計測した。base imageと依存layerは取得済みであり、
同じhostの別worktreeの検証負荷も変動するため、所要時間を性能SLOとして扱わない。

| 実行 | 確認した基準 |
|---|---|
| `./devctl quick api` | Ruff、mypy 163 source、unit 325件成功、Pydantic warning 0 |
| `./devctl quick web` | ESLint、incremental型check、Vitest 31 file・156件成功 |
| `./devctl verify e2e` | 実API・DB・workerを接続した14件成功、診断artifactの回収成功 |
| `./devctl verify` | API 413件、Vitest 156件、API代替型Playwright 48件、全層E2E 14件、MCP 51件成功。migration、生成型drift 0、Proxyを含むproduction imageも確認 |

Web全体coverageはstatements 40.75%、branches 42.13%、functions 36.31%、lines 42.31%である。
個別gateはcomposableの`auth.ts`、`pagination.ts`、`notify.ts`、`projectFilter.ts`が全指標100%、
`taskPolling.ts`がstatements 94.11%、branches 84%、functions/lines 100%で成功した。
標準検証は外部labへ接続しない。実機受入の成功は上記件数へ含めない。

## 実機SSH・Ansible・libvirt test

`tests/external`は標準verifyと通常CIから分離する。Compose projectを分けても管理node上のVM、network、
storageは自動分離されないため、次の条件をすべて満たす場合だけ`devctl infra`で実行する。

- 設定受け入れ手順は`api/tests/external/README.md`を正本とする。`infra-config.example.json`を基に
  repository rootのignored directory `.secrets/`内へ`infra-config.json`を作成し、directoryを`0700`、fileを`0600`にする。
- operatorが必要なSSH接続と空き容量を事前確認する。`devctl`のpreflightはnested構造、専用lab宣言、
  URL、path、必須resource suffix、SSH/SFTP/sudo、Ansible facts、qemu/libvirt、容量と衝突を
  lab資源を変更せずreadiness phaseで検査する。
- resource名へrun IDを付け、既存resourceをskip、再利用、削除しない。
- cleanupを有効化する前に、管理nodeのexact resource名とremote pathをread-onlyでinventoryし、衝突時は終了する。
- testを直列実行し、fixture finalizerに加えて独立cleanup containerを`devctl`の終了trapから再実行する。
  成功・失敗・INT・TERMのすべてでrun IDに一致する資源だけを回収する。
- worker待機、Ansible、downloadに有限timeoutを設ける。

設定検証、task応答のpolling、resource名の導出、cleanup判断はlabへ接続しないunit testの対象にする。
mutation前にproject-scoped volumeのversion付きmanifestへexact resource名、node、remote pathを記録し、
作成成功後にAPI UUIDを追記する。cleanupはmanifestを唯一の削除allowlistとし、configとrun IDからの再構築は
read-only診断に限定する。cleanup開始時はDB migrationやworker起動より先にmarkerとmanifest identityを
networkなしで検証する。VMなど同じ依存tierはまとめて回収し、そのtierに失敗があればnetwork、storage、
nodeなど下位tierへ進まない。cleanup後は別processがDB、virsh inventory、remote pathをread-onlyで確認し、
run所有資源が残る場合はprojectとvolumeを保持する。

`devctl infra preflight`は設定fileと親directoryが実行user所有かつ`0600`/`0700`であることを先に検査し、
設定、SSH/SFTP、passwordless sudo、容量、download metadata、exact collisionをlab側への変更なしで検査する。
破壊的scenarioは`happy`、`task-failure`、`worker-stop`、`signal-int`、`signal-term`を同一lab lock下で直列実行し、
各scenarioを別run IDへ分離する。signal scenarioは子processの130/143終了とcleanup完了の両方を成功条件にする。

設定不足、共有環境の疑い、既存resourceとの衝突があれば変更前にfail closedする。scenario、cleanup、
または独立inventoryが失敗した場合は診断用のCompose project、DB、SSH volume、manifestを削除せず、
同じconfig、run ID、projectを使う復旧commandを表示する。
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

error codeまたはfield error codeを追加・変更するときは、backendのcode定義とschema、OpenAPI、
frontendの日英辞書、API・辞書contract testを同じ変更で更新する。共通error envelopeへの移行では
旧形式とのdual response期間を設けず、すべての通常API・Agent APIと利用側を一度に切り替える。

## DB schema変更

1. SQLAlchemy modelとAlembic metadataへのimportを更新する。
2. `./devctl up`後に`./devctl shell api`からdisposableな開発DBへrevisionを生成する。
   shellはhost UID/GIDで入るため、生成fileをroot所有にしない。
3. revisionのupgrade、downgrade、constraint、data移行をreviewする。
4. `./devctl verify api`でfresh DBへのupgradeとintegration testを確認する。

既存revisionを履歴から消したり書き換えたりしない。`alembic downgrade base`やversion file削除を含む
legacy scriptは通常手順に使わない。

## Agent APIとMCP helperの安全検証

Agent APIのunit・contract testは固定clock、fake WebAuthn verifier、fake task adapterを使い、
SSH、Ansible、libvirt、downloadのproduction backendへ接続しない。次の境界を標準checkから外さない。

- principal、scope、project、node、resourceの認可matrixと既存REST経路
- WebAuthn challenge replay、RP ID・origin不一致、device鍵・DPoP不一致
- lease期限・失効・変更上限、global/device kill switch、breaker、同時実行上限
- idempotency keyの同時retry、request hash相違、stale generation、取消、worker crash、`unknown`
- 監査保存失敗時のfail closedと、秘密入力が監査event・task logへ残らないこと
- VM名、description、task logのprompt injection文字列がpolicy判断を変えないこと
- project pool外のstorage、network、image、flavor、nodeをAgentと既存RESTの双方が拒否すること
- image downloadのDNS rebinding、private・link-local address、redirect、同時downloadを拒否し、
  no-clobber失敗後も既存dataと一時file cleanupが保たれること

SQLiteで完結するtestは`tests/unit`、PostgreSQLのunique constraint、advisory lock、transaction競合を
必要とするtestは`tests/integration`へ置く。後者はworkerが利用するDBと分離したfresh DBで実行し、
共有DBやproduction workerへ接続しない。

`virty-mcp`はAPI imageと分離したPython packageである。helperのcontract testはmemory credential storeと
fake HTTP transportを使い、実端末のcredential storeやVirtyへ接続しない。stdoutをMCP JSON-RPC以外へ
使わないこと、API/helper catalogのbyte一致、schema、DPoP、Tasks fallback、秘密値redactionを検査する。
helperのcheckもhost Pythonから直接実行せず、`./devctl quick mcp`または
`./devctl verify mcp`のnetworkなしone-shot serviceで実行する。helperの変更に加え、
APIの管理routeやAgent catalogの変更でもMCPのCI gateを起動する。

`AGENT_TASK_ENCRYPTION_KEY`はAES-256用の32 byteをbase64またはbase64url化した値とする。
hex 32 byte値はbase64として48 byteに復号されるため使用しない。test用固定値とproduction secretを分離し、
秘密鍵やlease tokenを設定file、log、test artifactへ保存しない。

## CI、文書、Git

- master向けPRとmaster pushのCIはAPI、Web、全層E2E、Proxy、MCP helperを分離して
  `./devctl verify <component>`を実行する。API・Web・共通基盤の変更で全層E2E jobを起動する。
  tag publishは公開対象componentのverifyをregistry loginより前に実行する。cache scopeはcomponentごとに分ける。
- `docs/development.md`を手順の正本とし、component READMEやCIへcommand列を複製しない。
- 文書だけの変更でも`git diff --check`と内部linkの存在を確認する。
- 完了前に引数なしの`./devctl verify`を実行する。実行できない項目と理由は明記する。
- commit前に`git status --short`、`git diff`、`git diff --cached --check`、staged diffを確認する。
- release時だけ`api/settings.py`と`vue/package.json`のversion整合を確認する。

## Agent機能のproduction導入

production以外の管理nodeへ向けたcanaryがない場合、機能flagを段階的に有効化すること自体を
WebAuthn付き管理操作として扱う。

1. 最初の7日間は`shadow_mode=true`かつmutation停止でreadとpolicy・監査結果だけを評価する。
2. R1を有効化し、単一resourceの低risk操作、retry、取消、breakerを確認する。
3. R2を有効化し、対象制約とgeneration conflictを確認する。
4. R3は同時1件を維持し、削除・network変更の残存riskを運用者が明示的に受容した場合だけ有効化する。

既存RESTやWeb UIから同じresourceを変更するときは、先にAgent global controlでmutationを停止する。
同期REST mutationはAgentのtarget reservationへ参加しないため、移行期間中の同時変更を安全とは扱わない。

backup、snapshot、帯域外network復旧がない環境では、補償統制が働いても削除後の復元や管理network断からの
復旧を保証できない。`allow_delete_without_recovery`と`allow_network_change_without_oob`を
恒常的な既定値として有効にしない。
