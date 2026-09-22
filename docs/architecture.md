# アーキテクチャ

## この文書の役割

Virtyのcomponent境界、主要なdata flow、変更時に保持すべき設計上の不変条件を説明する。
全file、endpoint、class、DB列の一覧は持たず、詳細はコードとOpenAPIを正本とする。

## System context

```text
Browser -- HTTP -------------------> web: Nginx + Vue SPA
Browser -- HTTPS --> operator TLS proxy -- HTTP --> web
web -- /api -----------------------> api: FastAPI
web -- /novnc ---------------------> proxy: websockify -- console token照会 --> api
Codex Desktop -- stdio ------------> virty-mcp helper
virty-mcp -- HTTPS/DPoP --> operator TLS proxy --> web --> api: Agent API
api -------------------------------> PostgreSQL
worker: task scheduler <-----------> PostgreSQL
api -- on-demand SSH --------------> Managed Linux nodes
worker -- SSH / Ansible / libvirt -> Managed Linux nodes
```

配布する`web`はHTTPで待ち受け、そのNginxが同一originのAPIとnoVNCを内部serviceへ転送する。
TLSが必要な環境では、運用者が管理するreverse proxyまたはload balancerを`web`の前段に置く。
同一hostでTLS終端する場合は`web`をloopbackへbindし、別hostの場合はprivate interfaceとfirewallで
TLS proxyだけから到達可能にする。`VIRTY_PUBLIC_URL`は内部HTTP URLではなくbrowserから見えるoriginを
表し、AgentのDPoPとWebAuthn検証もこの固定値を使う。`proxy`はreverse proxy用Nginxではなく、
noVNCのwebsockify serviceである。

## Componentの責務

| Component | 責務 | 主な正本 |
|---|---|---|
| Web | file-based routingの管理UI、日英localeと辞書、Bearer token保持、型付きAPI client、noVNCへの導線 | `vue/src/`, `vue/nginx.conf` |
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

ユーザ管理は管理者用CRUDと本人用APIを分離する。本人用APIの対象はJWTから決定し、scopeや他人の
usernameを更新入力として受け付けない。公開鍵候補は管理者用一覧でなく本人profileから取得する。
RESTとAgentの作成・公開鍵保存・password更新は共通serviceを使い、transactionのcommitは呼出し側が行う。
ユーザ編集・本人設定では公開鍵と新規password fieldを共用する。未保存入力はdialog終了、route離脱、
browser離脱で確認し、logout時は共通の取消可能eventを認証情報の破棄前に発行する。

Web JWTはユーザごとのsession generationを持ち、requestごとにDBと照合する。password変更はhashと
generationを同一transactionで更新する。migration前のユーザのみgenerationをNULLとして旧JWTを受理し、
初回変更後は旧JWTを拒否する。新規ユーザにはUUIDを付与し、同名再作成でも旧JWTを再利用できない。
Agent credentialの失効はこのgenerationから独立する。downgradeはgeneration列を削除するため、
失効保証を維持したrollbackにはWeb JWT署名鍵のrotationが必要となる。

1. WebがAPIのversion/初期化状態を確認する。
2. 利用者が存在しない場合だけ、初期管理利用者を作成する。
3. loginはOAuth2 formを受け取り、利用者ID、scope、projectを含む期限付きBearer JWTを返す。
4. frontend API clientはAuthorization headerを付加し、backendは依存関数でtokenと必要scopeを検証する。

JWT signing keyはprocess再起動をまたいで同じ値を使う必要がある。productionでは明示的なsecretを与え、
repositoryやimageへ埋め込まない。

Web UIのBearer JWTはissuerとaudienceを検証する短命tokenとし、scopeは完全一致または明示的wildcardで評価する。
Project操作ではJWTのProject IDとDB上のmembershipを対象objectごとに照合する。member追加は既発行JWTを拡張せず
再login後に有効にし、member削除はDB上のmembership確認によって既発行JWTより優先して即時失効させる。
noVNCはVM UUIDをtokenとして使わず、対象VMのobject認可後に発行する60秒のconsole ticketをresolverへ渡す。
ticketはhashだけを保存して一度だけ消費し、NginxとAPIのaccess logにはticketを含むresolver pathを記録しない。

### Web UIの操作モード

Webのauth storeはJWTの付与scopeと操作モードを分離し、既存の画面・routerが参照する`scopes`を
実効scopeとして導出する。一般モードでは`admin`の包括権限を通常の`user`参照権限に置き換え、
明示的な個別scopeは保持する。切替可能性は元の付与scopeから判定する。
App barはtab内のsessionStorageへ利用者名と選択を保存し、切替時にdashboardを再読込する。
この境界で全画面とtask pollerを破棄・再作成し、setup時に確定するqueryや遅延responseの持越しを避ける。
対象はdashboard、VM・Project・node・storage・image・network・taskの一覧と詳細、管理専用route、
作成・変更dialog、navigation、App barのtask監視である。APIの認可は引き続きserverが担当する。

### Web UIのlocale

WebはVue I18nの`en`・`ja`辞書を表示文言の正本とし、Vuetifyの組込文言もadapterを介して同じ
reactive localeへ接続する。起動時は`localStorage`の`virty:locale`、`navigator.languages`内で最初に
一致する対応言語、英語の順に解決し、applicationをmountする前に適用する。切替時は保存値、Vue・Vuetify、
`html`の`lang`、route title、日時・数値formatterを一体で更新する。
localeはURL、cookie、利用者DB、API request headerへ持たせず、Webは`Accept-Language`を送信しない。

APIへ送るstatusやmethodなどの値はlocaleにかかわらず固定し、既知値の表示labelだけを翻訳する。
resource名、利用者入力、XML・JSON・YAML、taskのrequest・message・log、管理node出力はuntrustedな
運用dataとして原文を保持し、辞書keyや翻訳対象として解釈しない。

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
Projectの名称変更、member追加・削除、resource grant更新も独立actionとし、利用者作成・更新adapterはmembershipを
変更しない。Project generationは名称、member、非強制limit、storage/network pool、flavor grantから計算し、
並行変更を古いgenerationで上書きしない。grant候補の全pool・flavor取得はglobal admin専用のR0 actionとして明示し、
grant更新はglobal adminのR3 actionとしてrequest解析時と実行直前に再認可する。
共有poolやstorage等を介して制約外Project・nodeへ影響が波及しないよう、global mutationはProject・node制約を
どちらも持たない能力leaseとDB上のglobal adminだけに許可し、制約付きleaseでは受付時とworker dispatch時に拒否する。

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

登録済みSSH公開鍵の補完では、本人profile APIを使い、認証状態のuser名と完全一致した利用者の公開鍵だけを候補にする。
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

Project未割当resourceも管理できるよう、VM、node、storage、image、network、各pool、flavor、Projectの
一覧と提供済みの詳細・XML・node診断、dashboardには`admin=true`で明示する管理用readを設ける。
VMのconsole ticket発行も`admin=true`指定時だけ管理者に他人のVMへの接続を許可する。
VMのISO候補一覧とCD-ROM更新も管理画面から`admin=true`を明示し、同じnode上の登録済みISOを管理者が利用できる。
CD-ROM更新は受付時にDB・token双方のadmin scopeを確認し、workerはVM ownerの変化と実行時のDB admin scopeを再確認する。
明示的な管理用CD-ROM更新では、個人・Projectのownerがともに未設定の旧VMも許可する。taskには未設定のownerを
そのまま固定し、実行までにownerが割り当てられた場合は拒否する。通常taskではowner必須、全taskで二重ownerは禁止する。
通常利用者のProject grant検査とAgent taskの境界は維持する。
image downloadも`admin=true`指定とDB・token双方のadmin scopeを条件に全storageを保存先にできる。
管理用download dialogは一覧取得と送信の双方で管理用指定を送り、通常のdownloadとAgentのgrant境界は維持する。
storage metadata更新にも同じ明示的な管理用指定を設け、管理画面の編集dialogから送信する。
APIはmetadata保存前にDB・token双方のadmin scopeとstorageの存在を確認し、通常更新のgrant境界は維持する。
共通判定でDBとtoken双方のadmin scopeを検査し、Project filterがない場合だけ全体参照を許可する。
Project filter指定時は従来のmembershipとgrant、networkのportgroup単位grantを維持する。
共通の`allowed_*`は変更せず、通常read、変更操作、AgentのProject境界を保持する。

### Project共同管理境界

Project IDは重複しない6桁hex、名称は重複可能な表示値とする。membership、storage pool、network pool、flavorの
多対多関係には組合せ一意制約を置き、Project別roleや旧`group` tableを認可へ使わない。VMは個人ownerまたは
Project ownerを最大一つ持つ。通常の新規VMではProject ownerを必須にし、管理者用作成経路では
作成者を個人ownerとして保存する。移行前から存在する未所属VMもpersonal VMとして残す。

管理者用VM作成は専用REST endpointとtask keyで通常のProject作成から分離する。Webは同じformを別dialogとして
開き、管理用inventory readから候補を取得する。Project grantは要求せず、nodeと各resourceの存在・同一node条件は
APIとworkerの双方で検査する。workerは外部処理前に作成者の最新admin権限を再確認し、Agent taskは拒否する。
Project作成endpoint・schemaとAgent catalogの境界は維持する。

共同管理migrationは、NULL・重複membershipを整理した結果memberが0名になるProjectを検出するとupgradeを中止する。
運用者は該当Projectを確認し、`users_to_projects`へ有効な利用者を1名以上割り当ててからupgradeを再実行する。

Project固有のVM作成では、最初にProjectを一つ確定し、そのProjectへgrantされたstorage・network・flavorから
候補を導出する。copy元imageはstorageに加えて設定済みflavorも同じProjectへgrantされていることをAPI受付時と
worker実行時に検査する。flavorがNULLのimageは汎用imageとして扱う。imageのflavor更新もProject IDを必須とし、
storageとflavorを同じProjectへ照合する。所属Project全体のresource和集合を一つのVMへ混在させない。
VMのProject移動ではDomain行を
先に、source・destination Project行をID順にlockし、最新のdisk・CD-ROM・network・image flavorを移動先grantへ
再照合してから個人ownerを解除する。CD-ROM・network変更とresource削除もDomainからProjectの順でlockし、移動中の
古いowner認可や逆順lockによるdeadlockを防ぐ。Project削除はAPI受付時とworker実行時の双方で
所属VMがないことを検査し、VM、pool、flavor自体は削除しない。
RESTのVM Project移動は通常、現在のowner本人または所属Project memberに限る。管理者は明示的な`admin` scopeと
移動先Projectのmembershipを持つ場合、ownerが異なる個人VMやowner未設定の旧VMも移動できる。
この場合もlock後の認可と移動先grant検査を省略しない。
RESTのVM削除・電源・CD-ROM・network taskは受付時のprincipalとownerをrequestへ固定し、workerがDomainから
Projectの順でlockした後に最新ownerとDB membershipを再認可する。queue待機中にVMが移動した場合やmemberを
削除された場合は、管理nodeへの副作用を始める前にtaskを拒否する。personal legacy VMも受付時の個人ownerと
task principalの完全一致を必要とする。
Agentの同じVM taskも、dispatch policyの再評価に加えてDomain lock取得後にserver解決済みsource Projectと
principalの最新membershipまたはpersonal ownerを再照合し、dispatchからhandler開始までのVM移動を拒否する。

resource poolは複数Projectから共有される独立resourceである。Project grant更新はID集合の完全置換として行い、
所属VMが参照中のstorage、network、flavorをgrant外にする変更を拒否する。CPU・memory・storage limitは互換表示値で、
現時点の配置・作成処理ではquotaとして強制しない。grant編集の未grant resource候補は引き続き
Project配下のglobal admin専用candidate APIから取得する。作成・変更dialogのProject選択には所属Project一覧を使う。
管理画面の「すべて」は保存時点の候補ID集合を選択する操作であり、将来追加されるpoolやflavorへの自動grantではない。
network poolの構成置換は、変更後も共有Projectの使用中VMが必要とするnetworkとportgroupを保持する場合だけ許可する。

### Inventory同期

VM、storage、image、networkの一覧は、管理node上のlibvirt状態を走査してDBへcacheする。
走査ごとの更新tokenで現在見つかったresourceを識別し、見つからなかった古いcacheを除去する。
したがってDBだけを編集しても管理nodeの実状態は変わらず、次の走査で上書きされ得る。

### Dashboard snapshot

Web dashboardはBearer token付きの型付きclientで専用のdashboard query APIを呼び、APIが
認証利用者の参照範囲に合わせてDB上のinventory cacheとtask recordを表示用に集約する。
通常readは各resourceとtaskに既存queryと同じscope認可とproject・resource poolによる絞り込みを適用する。
管理画面が明示する`admin=true`はserverでadmin権限を検査し、全resourceと全taskを集計する。

VM、node、storage、image、network、各pool、flavorの一覧は任意のProject filterを受け取り、指定時は
Projectの存在と認可を404で秘匿したうえで、そのProjectだけから導出したresourceを返す。WebはfilterをURL queryに
保持するため、Project詳細からresource一覧へ遷移しても管理境界が失われない。
WebのVM、node、storage、image、network一覧はroute metaでProject filterの対象と宣言し、App barが
共通selectorを所有する。共通composableがURL queryを読み書きし、各一覧は変更を監視して先頭pageから
再取得する。image一覧ではnode・storage候補と選択行もリセットする。App storeは最後のfilterを
サイドナビゲーションの遷移先へ渡すためだけに保持し、直接URLや履歴からの選択を上書きしない。

このflowはread-onlyであり、表示や再読込を契機に管理nodeへのSSH・libvirt接続、inventory再走査、
task投入を行わない。表示値は取得時点のsnapshotであり、時系列dataやreal-time監視を表さない。

### API契約とfrontend型

application schemaの多くは共通baseでcamelCase aliasを生成し、OAuth2の固定形式などは例外とする。
FastAPIが`/api/openapi.json`を公開し、
`vue/src/api/openapi.d.ts`はそのschemaから生成し、`openapi-fetch` clientが利用する。
backend schemaと生成型は独立した仕様ではなく、一つの契約の生成元と生成物である。

通常APIとAgent APIのerror responseは次の共通envelopeを使う。`code`とfield errorの`code`は
`lower_snake_case`の安定した識別子、`message`は手動で定義する英語fallbackとし、Webは既知のcodeを
日英辞書で表示する。`params`は翻訳時の補間値であり、値をstring、number、boolean、nullに限定する。

```json
{
  "detail": {
    "code": "api_error_code",
    "message": "English fallback message",
    "params": {},
    "errors": [
      { "field": "body.name", "code": "field_error_code", "params": {} }
    ]
  }
}
```

`params`と`errors`は該当するときだけ返す。422 validation errorはfield、code、安全なparameterだけへ
正規化し、入力値、validatorのraw message、内部contextを返さない。従来の`detail` string・listと
Agent API固有error形式は同時対応せず、この共通契約へbreaking cutoverする。APIは表示localeを判断せず、
未知codeを受けたclientだけが英語fallbackの`message`を使用する。

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
- 公開するAPI error code、field error code、parameterとfrontendの日英辞書を同じ変更で同期する。
- model変更では既存DBを移行できる新規Alembic revisionを追加する。
- destructive operationでは、対象node、VM、storage、networkを一意なIDで解決してから実行する。
- Agent API以外の既存REST経路も同じscope・project・object境界を迂回できないようにする。
- Project membershipはProject APIだけを正本とし、利用者作成・更新から暗黙に置換しない。
- Projectの表示名を識別子として参照せず、API、Agent、task、認可では6桁IDを使う。
- MCP annotationはclient表示のhintに限り、認可やrisk判定の入力にしない。
- 管理node操作はbackend interfaceを越えて行い、標準testからproduction adapterへ接続しない。
