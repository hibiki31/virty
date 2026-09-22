# プロダクト要件

## この文書の役割

Virtyが現行実装として提供する価値、利用者、機能境界、品質上の不変条件を定義する。
endpointやDB列のreferenceではない。詳細なAPI契約は実行中APIのOpenAPI、
実装状況はコードを正本とする。

## 目的と対象利用者

Virtyは、SSHで到達できるLinux上のKVM/libvirt環境を、Web UIとAPIから一元管理するための
軽量なcontrol planeである。主な利用者は、自身が管理権限を持つ小規模な仮想化環境を
構築・運用する管理者と、同じProjectでVMやresourceを共同管理する複数の利用者である。

管理対象nodeにはSSH公開鍵認証と、必要なsystem package・sudo権限を設定できることを前提とする。
Virtyは管理対象nodeの代替hypervisorではなく、libvirt、Ansible、SSHを介して既存基盤を操作する。

## 現行実装で提供する機能

### 初期設定・認証・利用者

- 初回アクセス時に最初の管理利用者を作成できる。
- OAuth2 password flowでBearer JWTを発行し、保護されたAPIとWeb UIで利用する。
- APIから利用者の作成、一覧、更新、削除を行い、scopeと複数のSSH公開鍵を保持できる。
- 管理者はWebから利用者を作成・削除し、scopeと公開鍵を編集し、他人のpasswordを再設定できる。
  自己削除、最後の管理者の削除・降格、Project最後のmemberの削除を拒否する。
- 全利用者はアカウント設定で自分の権限・所属を参照し、公開鍵とpasswordを変更できる。
  本人のpassword変更には現在のpasswordを必要とし、変更・再設定後は全Web端末で再loginする。
  Agent端末・leaseの失効は既存の独立した管理操作で行う。
- 新規passwordは8文字以上、英小文字・英大文字・数字・記号を含み、空白なし、UTF-8で72byte以下とする。
  初期設定・REST・Agentで同じ検証を行い、既存passwordのlogin互換性は保持する。
- 公開鍵は名前とOpenSSH形式の鍵を組として管理し、秘密鍵・不正形式・名前重複を拒否する。
  作成・編集は明示保存とし、失敗時は入力を保持し、未保存入力を破棄する前に確認する。
- scopeをAPI認可に利用し、Project IDをtokenに含める。実効権限は操作scopeと対象Projectへの所属を
  ともに満たす場合だけ与え、VM・Project・関連resourceの一覧と詳細を同じ境界で絞り込む。
- Project membershipはProject APIだけから変更する。member追加後の権限は再loginで取得したJWTから有効になり、
  member削除はDB上の所属をrequestごとに再確認して次のrequestから失効させる。
- scopeは完全一致または末尾の明示wildcardだけで評価し、各endpointでactionと対象objectを再認可する。
- Web UI用JWTとAI agent用credentialを分離し、Web UI用JWTをagentへ渡さない。

### Codex Agent操作

- Codex Desktopから起動するローカルstdio MCP helperを介し、Virtyをinternetへ公開せずに操作できる。
- helperはOS credential storeにP-256端末鍵を保持し、管理者がVirty Web UIで端末pairingと能力leaseを
  WebAuthn承認する。秘密鍵、password、Web UI用Bearer tokenはhelperへ渡さない。
- 能力leaseはprincipal、device、許可action、project・node、破壊操作、期限、変更回数へ制限し、
  device鍵のproof-of-possessionを全requestで確認する。既定期限は30分、変更上限は20件とする。
- MCPにはreview済みaction catalogだけを公開する。任意shell、任意HTTP API proxy、認証・setup、
  内部console resolver、秘密値のreadbackは提供しない。新しいREST endpointもcatalog更新までは公開しない。
- Projectの名称、member、resource grantは専用actionで変更する。利用者作成・更新actionからmembershipを変更せず、
  resource grantの完全置換はglobal adminだけに許可するR3 actionとして扱う。
- 読取結果にはVM名、IP、XML、task logなどの運用情報を含められるが、access token、password hash、
  VNC password、SSH秘密鍵を含めない。credential投入はwrite-only actionとする。
- Agentからのimage downloadは管理者が列挙したHTTPS hostだけを許可し、private・link-local・metadata宛と
  redirectを拒否する。allowlistが空の場合はdownload actionをfail closedにする。
- 変更actionは一意なidempotency keyと対象generationを必須とし、受理後はoperation IDで非同期に追跡・取消できる。
- 全agent操作をtask履歴とは別のappend-only監査eventへ記録する。秘密入力の値は記録しない。

### 管理nodeとinventory

- SSH接続情報を持つnodeを登録し、roleを割り当てられる。
- global adminはnode管理画面でProject未割当のnodeも一覧・詳細・診断情報を参照できる。
  管理用readは`admin=true`の明示指定とserver側のadmin権限確認を必要とし、Project filter指定時は
  所属Projectのresource境界を維持する。
- 同じ管理用readをVM、storage、image、network、storage/network pool、flavor、Projectの一覧と
  提供済みの詳細・XML、dashboardにも適用する。dashboardは全resourceと全taskを集計する。
  通常read、Projectを選択する作成・変更操作、Agentの参照範囲は拡張しない。
- nodeのOS、CPU、memory、libvirt/QEMU、network、filesystemなどの情報を取得できる。
- libvirt上のVM、storage pool・volume、virtual networkを再走査し、control planeのDBへ反映できる。

### VM lifecycle

- VMの一覧、詳細、libvirt XML、電源状態を確認できる。
- VM詳細では、接続networkへの導線と、disk容量、pathから識別できるfile名を確認できる。
  diskのfull pathは必要なときだけfile名chipから展開する。
- storageとnetworkを選択し、空diskまたは既存imageのcopyからVMを作成できる。
- cloud-init user data、CD-ROM、network interface、Project割り当てを扱える。通常の新規VMは所有Projectを必須とし、
  選択Projectへgrantされたstorage・network・flavorだけを同じProject境界内で組み合わせる。
  copy元imageにflavorがある場合はそのflavorも選択Projectのgrantを必須とし、flavor未設定imageは
  OS flavorに依存しない汎用imageとして利用できる。
- global adminには通常のProject作成とは別に、Projectを指定せず全node・storage・network・imageから選べる
  管理者用VM作成dialogを提供する。同じnode上のresourceだけを組み合わせ、作成者を個人ownerとして保存する。
  API受付時とworker実行時にadmin権限を検査し、AgentのProject作成経路にはこの例外を適用しない。
- 既存の未所属VMと管理者用作成経路のVMはpersonal VMとして保持する。Projectへ移動すると個人ownerを解除し、既存diskとnetworkが
  移動先Projectのgrantを満たさない場合は移動を拒否する。
- WebのCreate VM dialogは、初期user名、password・password認証、SSH公開鍵、初回起動scriptを
  cloud-initへ設定するguided formを提供し、認証利用者に登録済みの公開鍵を候補として補完できる。
- guided formは明示的な適用操作で管理対象の設定だけをraw user dataへ一方向にmergeし、その他の設定を保持する。
  raw YAMLを送信内容の正本として適用後も自由に編集でき、raw側の変更をformへ逆同期しない。
- cloud-init user dataは`#cloud-config`から始まる単一のYAML mappingとして厳密に検証し、不正な内容を
  VM作成へ送信しない。平文passwordがuser dataとrequestへ含まれること、初回起動scriptがroot権限で
  実行されることをWeb UIで警告する。
- VMの起動・停止・削除と、noVNC経由のconsole接続を提供する。console接続は所有者、所属Projectの
  member、または管理者に許可する。管理者が他人のVMへ接続する場合は明示的な管理用指定を要する。
  接続には短命・一回限りのopaque ticketを使い、ticketをreverse proxyやAPIのaccess logへ残さない。

### Storage・image・network

- storage poolの発見、登録、metadata更新、再走査、削除を行える。
- global adminは明示的な管理用指定により、Project未割当を含む全storageのmetadataを更新できる。
  通常のmetadata更新は所属Projectからgrantされたstorageに限定する。
- volume/imageの一覧、metadata更新、HTTP download、削除を行える。
- global adminは明示的な管理用指定により、Project未割当を含む全storageへimageをdownloadできる。
  通常のdownloadは所属Projectからgrantされたstorageに限定する。
- libvirt networkの発見、作成、削除と、Open vSwitchのport group追加・削除を扱える。
- 複数のstorageやnetworkを、Projectへgrantする共有resource poolとしてまとめられる。pool自体は複数Projectから
  参照でき、poolの構成変更・削除とProjectへのgrant変更はglobal adminだけが行う。
- global adminは管理画面でstorage poolとnetwork poolを作成・編集・削除し、各poolに含めるresourceを設定できる。
  Projectのresource grant編集では、種類ごとに現在存在する候補を「すべて」選択できる。

### Project・flavor・非同期task

- Projectは複数人でVMとresourceを共同管理する唯一の境界であり、旧`group`とは別概念を併存させない。
  memberはProject内で同格とし、Project別roleは持たない。名称は重複可能な1〜64文字、識別子は6桁hexとし、
  UIでは曖昧さを避けるため名称とIDを併記する。
- global adminは1名以上の既存利用者を指定してProjectを作成し、VMが残っていないProjectだけを削除できる。
  `project.manage`を持つmemberは名称とmemberを管理できるが、最後のmemberは削除できない。
- Projectはstorage pool、network pool、flavorのgrantを保持する。grant更新は集合の完全置換とし、所属VMが使用中の
  resourceを失う変更は拒否する。imageと利用可能nodeはgrant済みresourceから導出する。
- Project modelのCPU・memory・storage上限は互換情報として表示するが強制しない。完全なquota強制や
  tenant isolationとは扱わない。
- flavor APIはOS、manual、icon、cloud-initなどのmetadataを管理し、imageと関連付けられる。imageへの
  flavor関連付けはProjectを明示し、imageのstorageとflavorが同じProjectへgrantされている場合だけ許可する。
- 時間のかかる変更操作はDB-backed taskとしてqueueし、状態、依存関係、message、失敗時tracebackを確認できる。
- worker再起動時に既存RESTの未完了taskを成功扱いせず`lost`として識別する。Agent taskは未dispatchのqueueを保持し、
  実行開始後のtaskは自動再実行せず`unknown`として識別する。
- Agent経由のtaskはprincipal、device lease、risk、解決済み対象、request hash、correlation IDを保持する。
  同一対象のmutationは端末をまたいでoperation完了まで予約し、workerは対象lock取得後にもlease失効、
  kill switch、対象generationを検査する。
- 外部処理の成否が確定できない場合は即時再実行せず、`reconciling`または`unknown`として実状態の確認対象にする。
  `unknown`は対象reservationを保持し、管理者が実状態を確認してWebAuthn付き管理操作で結果を確定するまで
  同じ対象のmutationを拒否する。

### 可観測性

- FastAPI request metricsと、VM・taskの集計値をPrometheus text formatで公開する。
- API/workerのlogをtext、JSON、または両方で出力できる。

## 提供中のWeb UI範囲

admin権限を持つ利用者はApp barのswitchで「一般モード」と「管理者権限モード」を明示的に切り替える。
新規loginは一般モードで開始し、選択は同じtabの再読込で保持する。logout・別利用者のloginでは解除する。
現在のモードは狭い画面でも文字で表示する。切替時は未保存編集の破棄を確認し、dashboardへ再読込して
一覧・詳細・dialog・task監視に以前の管理用dataを残さない。
管理者権限モードだけで管理用read、管理専用menu・route、管理者用作成・変更操作を提供する。
一般モードでは所属Project・本人の通常参照範囲と明示的な個別scopeを使う。
これはWeb UIの操作モードであり、accountの付与権限・JWTやserverの認可規則を変更するものではない。

Web UIには、login・初期設定、VM、Project、node、storage、image、network、利用者管理・本人設定、task一覧・詳細、
Agent端末・能力lease・global停止・`unknown` operation整合確認の管理画面がある。
Project画面は一覧・詳細、使用量と非強制limit、member、resource grantを表示し、権限に応じて作成、名称変更、
member変更、grant変更、削除を行う。VM、node、storage、image、network一覧のProject filterはApp barの
共通selectorで操作し、各ページ内には重複配置しない。名称とIDを併記し、clear操作で絞り込みを解除する。
選択状態はURL queryを正本とし、再読込・履歴移動・Project詳細からの絞り込みリンクに追従する。
サイドナビゲーションでresource一覧を移動すると選択を引き継ぐ。対象外の画面ではselectorを表示せず、
最後の選択を次のresource一覧への移動に使う。作成・変更dialogのProject指定は操作対象として個別に保持する。
App barのselectorは幅を制限し、狭い画面ではApp bar内の次行へ配置して操作領域を確保する。
dashboardは、認証利用者が参照できるVM、node、storage、image、network、taskの件数、状態、容量を、
DB上のinventory cacheとtask recordから集約した現在値のsnapshotとして表示する。
表示と再読込はread-onlyであり、管理nodeへのSSH・libvirt接続、inventory再走査、task投入を行わない。
集計対象は各APIの認可とprojectによる絞り込みに従い、利用者が参照できないresourceを含めない。

Web UIは日本語と英語を提供する。Virtyが所有する固定文言、入力検証、通知、accessibility文言は
自動翻訳せず、review可能な日英辞書で個別に定義する。明示した言語はbrowserへ保存し、保存値、
browserの対応言語、英語の順で選択する。loginと初期設定を含めて切替可能とし、VueとVuetify、
画面title、日時・数値表記へ同じlocaleを即時適用する。言語設定の利用者account間・端末間同期は提供しない。
READMEとMkDocs本文の完全な二言語化はこのWeb UI機能の対象に含めず、必要な場合は別変更として扱う。

resource名、利用者が入力したdescription、XML・JSON・YAML、taskのrequest・message・log、管理nodeの
command出力は運用dataであり、内容を翻訳または書き換えず原文のまま表示する。

## 品質上の不変条件

- 認証が必要なresourceは、Bearer tokenなしで管理操作を許可しない。
- 長時間の管理操作はHTTP request内で完了を待たず、taskとして追跡可能にする。
- APIとworkerは同じDB、data領域、SSH credential、task keyの規約を共有する。
- DB schema変更はAlembicで再現可能にし、既存環境と新規環境の両方をupgradeできるようにする。
- frontendが利用するAPI型はOpenAPIから生成し、backend契約と同じ変更で同期する。
- 通常APIとAgent APIのerrorは言語に依存しない安定したcode、手動で定義した英語fallback、
  構造化parameterを共通形式で返す。Web UIはcodeに対応する日英辞書を正本として表示し、
  validation errorで入力値や内部contextを応答へ漏らさない。
- 永続dataはcontainer imageの外に置き、再作成後もDB、管理data、SSH鍵を保持できるようにする。
- 配布WebはHTTPで待ち受け、TLS終端は運用者が外部reverse proxyまたはload balancerで任意に行う。
  平文HTTPはloopbackまたは信頼済み閉域だけで使用し、AgentのWebAuthn承認とproduction MCP接続には
  browserから見えるHTTPS originを用意する。
- 管理node上の削除、disk操作、network変更は破壊的であり得るため、対象を明示して実行する。
- Agent経由のmutationは監査書込み失敗時にfail closedとし、global停止、端末失効、端末別breakerを
  AI経路とは独立して操作できるようにする。
- Agentと既存RESTの双方で、projectからresource poolをたどってstorage、image、network、flavor、nodeの
  object認可を行う。一つの操作で複数Projectのresourceを混在させず、projectへ対応付け不能なglobal操作は
  adminだけに許可する。
- Agent image downloadは管理nodeで接続先DNSの全addressを検証し、TLS hostname検証を保ったままglobal IPへ
  接続を固定する。redirect・proxyを使わず、既存file/imageをatomicに上書きしない。
- 30分内に失敗または`unknown`が3件発生した端末はmutationを停止する。全端末・全leaseを通じて
  R3は同時1件、全mutationは同時3件までとする。
- recoveryなしの削除と帯域外復旧なしのnetwork変更は、global設定と個別leaseの双方が明示的に許可した場合だけ実行する。

## 対応済みとみなさない範囲

コードや検証根拠がない限り、次を現行機能として文書化しない。

- 高可用なcontrol plane、複数workerによる分散実行、厳密なtenant isolation
- project上限とresource poolを全操作へ強制する完全なquota管理
- flavorの独立したWeb管理画面
- dashboard上の時系列chartやreal-time監視
- libvirt以外のhypervisorや、SSHで到達できない管理node
- 外部identity provider連携やpassword reset workflow
- internet上のRemote MCP endpoint、Secure MCP Tunnel、無人service principal
- backup・snapshotによる削除後の復元、帯域外network復旧、production canary環境
