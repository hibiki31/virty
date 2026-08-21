# アーキテクチャ

## この文書の役割

Virtyのcomponent境界、主要なdata flow、変更時に保持すべき設計上の不変条件を説明する。
全file、endpoint、class、DB列の一覧は持たず、詳細はコードとOpenAPIを正本とする。

## System context

```text
Browser ---------------------------> web: Nginx + Vue SPA
web -- /api -----------------------> api: FastAPI
web -- /novnc ---------------------> proxy: websockify -- console token照会 --> api
Codex Desktop -- stdio -----------> virty-mcp helper
virty-mcp -- internal HTTPS/DPoP -> api: Agent API
api -------------------------------> PostgreSQL
worker: task scheduler <-----------> PostgreSQL
api -- on-demand SSH --------------> Managed Linux nodes
worker -- SSH / Ansible / libvirt -> Managed Linux nodes
```

production例ではbrowserに公開するのは`web`である。`web`のNginxが同一originのAPIとnoVNCを
内部serviceへ転送する。`proxy`はreverse proxy用Nginxではなく、noVNCのwebsockify serviceである。

## Componentの責務

| Component | 責務 | 主な正本 |
|---|---|---|
| Web | file-based routingの管理UI、Bearer token保持、型付きAPI client、noVNCへの導線 | `vue/src/`, `vue/nginx.conf` |
| API | 認証、同期query、on-demandのnode情報取得、validation、task投入、OpenAPIとmetricsの公開 | `api/main.py`, `api/*/router*.py` |
| Worker | DBからtaskを取得し、依存順に管理node操作を実行して状態とmessageを記録 | `api/worker.py`, `api/*/tasks.py` |
| PostgreSQL | control plane metadata、inventory cache、利用者、project、task状態の永続化 | `api/*/models.py`, `api/alembic/` |
| Managed node連携 | libvirt操作、Ansible playbook、SSH command、XML生成 | `api/module/`, `api/static/ansible/` |
| noVNC proxy | APIからconsole tokenを解決し、browserとVNC endpointを中継 | `proxy/Dockerfile`, `compose.example.yml` |
| virty-mcp helper | MCP tool、端末鍵、DPoP、pairing・lease・operation client。stdoutはJSON-RPC専用 | `virty_mcp/` |
| Agent API | action catalog、WebAuthn、能力lease、対象policy、監査、冪等性、停止制御 | `api/agent/` |

`api/domain/`はVM domainの実装packageであるが、外部APIとtask resourceでは`vms`・`vm`を使う。
名称を変更する場合は、router、task key、worker handler、frontend contractを一体として扱う。

### 管理node連携の境界

APIとworkerの業務処理は、SSH、Ansible、libvirt、downloadを直接初期化せず、それぞれのbackend
interfaceをproviderから受け取る。production providerは`api/module/`の実装へ接続し、標準integration testは
同じinterfaceのdeterministic fakeへ接続する。これによりtask登録、依存関係、状態遷移、失敗処理を
管理nodeへ接続せず検証する。

実backendそのものの互換性確認は`external` testの責務であり、標準CIの責務に混ぜない。fakeはproductionの
成功・失敗contractを再現するが、libvirtやOS固有の挙動を保証するものではない。

## 主要flow

### 初期設定と認証

1. WebがAPIのversion/初期化状態を確認する。
2. 利用者が存在しない場合だけ、初期管理利用者を作成する。
3. loginはOAuth2 formを受け取り、利用者ID、scope、projectを含む期限付きBearer JWTを返す。
4. frontend API clientはAuthorization headerを付加し、backendは依存関数でtokenと必要scopeを検証する。

JWT signing keyはprocess再起動をまたいで同じ値を使う必要がある。productionでは明示的なsecretを与え、
repositoryやimageへ埋め込まない。

Web UIのBearer JWTはissuerとaudienceを検証する短命tokenとし、scopeは完全一致または明示的wildcardで評価する。
noVNCはVM UUIDをtokenとして使わず、対象VMのobject認可後に発行する60秒のconsole ticketをresolverへ渡す。
ticketはhashだけを保存して一度だけ消費し、NginxとAPIのaccess logにはticketを含むresolver pathを記録しない。

### Agent pairingと能力lease

1. Codexが起動した`virty-mcp`はP-256端末鍵をOS credential storeに作り、公開JWKと要求scopeでpairingを申請する。
2. 管理者はVirty Web UIでpairing内容を確認し、Virty originのWebAuthn assertionで端末を承認する。
3. helperは端末鍵DPoP付きで能力leaseを申請する。管理者はWeb UIでprincipal、scope、project・node、
   変更上限と破壊操作flagを確認してWebAuthn承認する。
4. helperだけがDPoP付きone-time exchangeで短命leaseを取得する。Web UIへlease tokenを返さない。
5. Agent APIはlease JWTだけで許可せず、DB上のlease・device失効、global control、breaker、対象policyをrequestごとに確認する。

WebAuthnはrelying party originに束縛されるため、assertionをstdio helperで生成しない。初回credential登録では
管理者passwordの再入力を要求し、challengeは短命かつ一度だけ使用する。

### Agent actionとoperation

MCP toolとAgent API actionはchecked-in catalogで一対一に対応する。catalogはread/mutation、risk、scope、
入力・出力schemaと対象解決規則を持つ。REST routerやOpenAPIを自動的に全公開せず、catalog未登録actionは拒否する。

外部URLを受け取るimage downloadはAgent経路だけ追加policyを適用する。HTTPSの完全一致host allowlist、
管理node上での名前解決後の全address検査、検証済みIPへの接続固定とTLS hostname検証、redirect・proxyの
無効化をnetwork access直前にも行い、URLそのものはtask messageや監査detailへ保存しない。downloadは同じ
directoryの一時fileへ保存してからatomicなno-clobber linkで確定し、既存image/fileを上書きしない。

mutationは`idempotencyKey`、正規化request hash、`expectedGeneration`を検証してから既存task queueへ投入する。
同じprincipal・key・同じhashは既存operationを返し、同じkeyで異なるhashはconflictにする。Agent APIの
operation IDはroot taskとその依存taskをまとめ、clientが切断しても状態取得と取消要求を継続できる。

同じresourceへ別端末から届くmutationは、`target_key`とcorrelationごとのdurable reader/writer reservationで
operation完了まで直列化する。通常のobject変更はexact targetをexclusive、resource familyをsharedで予約し、
inventory全体を書き換えるrefreshはfamilyをexclusiveで予約する。SSH資格情報の更新はglobal exclusive、
SSHを使う処理は同じglobal keyをsharedで予約する。workerは同じmodeのPostgreSQL session advisory lockを取得してから
generationとpolicyを再検査し、外部handlerの完了までlockを保持する。依存taskの全副作用範囲も受付時に予約し、
直列chainの完了まで解放しない。これにより、同じgenerationを見た複数端末が同時に副作用を開始するTOCTOUと、
object変更中のinventory再構築を防ぐ。process停止後のreservationは、対応operationがすべて確定したterminal状態だと
確認できた場合だけ回収し、`unknown`では保持する。

SSH鍵pairの最終交換は共有volume上のprocess間file lockでも直列化し、既存RESTとAgent workerの同時交換で
private/public keyが混在しないようにする。一方、既存の同期RESTによるDB resource変更はAgent reservationへ参加しない。
移行期間に同じresourceをRESTとAgentから同時変更する場合はraceが残るため、運用者は先にglobal Agent mutationを停止する。

workerはdispatch直前にAgent policyを再評価する。外部resource変更後にDB更新へ失敗した場合は、二重効果を避けるため
自動で同じhandlerを再実行せず、`unknown`のreconciliation対象としてreservationを保持する。管理者が実状態を
確認し、WebAuthn付き管理操作で結果を確定するまで、同じ対象への後続mutationを許可しない。

### Agent監査と停止制御

監査eventはtask logと分離し、actor、device、lease、action、対象、正規化引数hash、policy判断、operation、
結果、correlation IDをappend-onlyで保存する。秘密値そのものは保存しない。mutationは監査eventの保存に失敗すると拒否する。

VM名、description、task log、facts、raw XMLなど管理対象由来の文字列はuntrusted dataとして扱い、そこに含まれる
命令やtool呼出し表現を認可・承認根拠にしない。LLMの解釈に関係なく、scope、対象、generation、停止制御は
構造化fieldだけからAPIとworkerが再検証する。

global mutation停止、device失効、device breakerはLLM/MCP経路から独立したWeb管理操作とする。
R3とmutation全体の同時実行上限、30分の失敗windowはAgent APIとworkerの双方で強制する。

### Create VMのcloud-init補助

Create VM dialogはguided formの状態とraw `userData`をbrowser内で分離して保持する。利用者が適用を指示したときだけ、
Webが現在のraw dataを単一の`#cloud-config` YAML mappingとして厳密に検証し、formが管理する初期user、password認証、
SSH公開鍵、package更新・install一覧、初回起動scriptの設定をmergeする。構文や構造が不正な場合はraw dataを変更せず、
VM作成も許可しない。
管理対象外のkeyは保持し、適用後はraw dataを送信内容の正本とする。raw側の手編集をformへ逆同期せず、再適用時だけ
formの値で管理対象を更新する。平文passwordとroot権限で実行するscriptの安全上の警告もWebの責務である。

登録済みSSH公開鍵の補完では、認証状態のuser名と既存の利用者取得APIを使い、完全一致した利用者の公開鍵だけを候補にする。
取得失敗や候補なしはmanual入力を妨げない。この補助処理とYAML生成はWeb内で完結し、APIは従来どおり
`cloudInit.userData`をopaqueな文字列として受け取る。form用schemaやendpointを追加せず、既存API契約を変更しない。

### 非同期resource操作

1. task routerが`method.resource.object`の組とrequest情報をDBへ保存する。
2. 後続処理がある場合は依存taskを`wait`の直列chainとして登録し、直前taskのUUIDを関連付ける。
3. workerは`init`と`wait`をpollし、実行可能なtaskを`start`へ遷移させる。
4. 登録済みhandlerがlibvirt、Ansible、SSHを介して処理し、`finish`または`error`、message、
   失敗時のtracebackを記録する。
5. worker起動時に残っていた既存REST taskは`lost`へ遷移する。Agent taskは、未dispatchのqueueを維持し、
   `start`、`reconciling`、`cancel_requested`を二重実行しない`unknown`へ遷移する。

taskは外部message brokerではなくPostgreSQLをqueueと状態storeに兼用する。workerを増やす変更では、
row lockだけでなく、外部resourceへの重複実行と冪等性を再検討する。

既存RESTのobject認可は、利用者の所属projectからstorage/network/flavor poolをたどって許可resourceを
server側で導出する。nodeは許可VM・storage・networkが存在するnodeだけを参照できる。projectへ安全に
対応付けられない全体再走査、node診断、SSH鍵、resource新規作成はadmin限定とする。

### Inventory同期

VM、storage、image、networkの一覧は、管理node上のlibvirt状態を走査してDBへcacheする。
走査ごとの更新tokenで現在見つかったresourceを識別し、見つからなかった古いcacheを除去する。
したがってDBだけを編集しても管理nodeの実状態は変わらず、次の走査で上書きされ得る。

### API契約とfrontend型

application schemaの多くは共通baseでcamelCase aliasを生成し、OAuth2の固定形式などは例外とする。
FastAPIが`/api/openapi.json`を公開し、
`vue/src/api/openapi.d.ts`はそのschemaから生成し、`openapi-fetch` clientが利用する。
backend schemaと生成型は独立した仕様ではなく、一つの契約の生成元と生成物である。

### Runtimeと永続data

配布構成は`api`、`worker`、`web`、`proxy`、`db`のserviceからなる。APIとworkerは同じAPI image、
DB接続、`/opt/data`、SSH鍵volumeを共有する。API container起動時にAlembic upgradeを実行し、
PostgreSQL、application data、SSH鍵はnamed volumeへ保存する。

runtimeのmajor versionとimageはDockerfileおよび`compose.example.yml`、Python packageは
`api/requirements.txt`、frontend packageとpackage managerは`vue/package.json`とlockfileを正本とする。

## 変更時に保持する不変条件

- `web`からAPIとnoVNCへ到達するsame-origin経路を維持する。
- APIとworkerでDB接続、data path、SSH credential、task keyの解釈を一致させる。
- routerが投入するtask keyには、workerが読み込むhandlerを必ず一つ対応させる。
- 管理nodeの実状態とDB cacheを区別し、変更後に必要なinventory再走査をqueueする。
- schema変更ではOpenAPIとfrontend生成型を同期し、生成型へ手修正を加えない。
- model変更では既存DBを移行できる新規Alembic revisionを追加する。
- destructive operationでは、対象node、VM、storage、networkを一意なIDで解決してから実行する。
- Agent API以外の既存REST経路も同じscope・project・object境界を迂回できないようにする。
- MCP annotationはclient表示のhintに限り、認可やrisk判定の入力にしない。
- 管理node操作はbackend interfaceを越えて行い、標準testからproduction adapterへ接続しない。
