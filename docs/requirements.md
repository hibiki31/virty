# プロダクト要件

## この文書の役割

Virtyが現行実装として提供する価値、利用者、機能境界、品質上の不変条件を定義する。
endpointやDB列のreferenceではない。詳細なAPI契約は実行中APIのOpenAPI、
実装状況はコードを正本とする。

## 目的と対象利用者

Virtyは、SSHで到達できるLinux上のKVM/libvirt環境を、Web UIとAPIから一元管理するための
軽量なcontrol planeである。主な利用者は、自身が管理権限を持つ小規模な仮想化環境を
構築・運用する管理者である。

管理対象nodeにはSSH公開鍵認証と、必要なsystem package・sudo権限を設定できることを前提とする。
Virtyは管理対象nodeの代替hypervisorではなく、libvirt、Ansible、SSHを介して既存基盤を操作する。

## 現行実装で提供する機能

### 初期設定・認証・利用者

- 初回アクセス時に最初の管理利用者を作成できる。
- OAuth2 password flowでBearer JWTを発行し、保護されたAPIとWeb UIで利用する。
- APIから利用者の作成、一覧、更新、削除を行い、scopeと複数のSSH公開鍵を保持できる。
- scopeをAPI認可に利用し、project IDをtokenに含める。VM・project一覧は認証利用者とDB上の所属で絞り込む。
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
- 読取結果にはVM名、IP、XML、task logなどの運用情報を含められるが、access token、password hash、
  VNC password、SSH秘密鍵を含めない。credential投入はwrite-only actionとする。
- Agentからのimage downloadは管理者が列挙したHTTPS hostだけを許可し、private・link-local・metadata宛と
  redirectを拒否する。allowlistが空の場合はdownload actionをfail closedにする。
- 変更actionは一意なidempotency keyと対象generationを必須とし、受理後はoperation IDで非同期に追跡・取消できる。
- 全agent操作をtask履歴とは別のappend-only監査eventへ記録する。秘密入力の値は記録しない。

### 管理nodeとinventory

- SSH接続情報を持つnodeを登録し、roleを割り当てられる。
- nodeのOS、CPU、memory、libvirt/QEMU、network、filesystemなどの情報を取得できる。
- libvirt上のVM、storage pool・volume、virtual networkを再走査し、control planeのDBへ反映できる。

### VM lifecycle

- VMの一覧、詳細、libvirt XML、電源状態を確認できる。
- VM詳細では、接続networkへの導線と、disk容量、pathから識別できるfile名を確認できる。
  diskのfull pathは必要なときだけfile名chipから展開する。
- storageとnetworkを選択し、空diskまたは既存imageのcopyからVMを作成できる。
- cloud-init user data、CD-ROM、network interface、project割り当てを扱える。
- WebのCreate VM dialogは、初期user名、password・password認証、SSH公開鍵、初回起動scriptを
  cloud-initへ設定するguided formを提供し、認証利用者に登録済みの公開鍵を候補として補完できる。
- guided formは明示的な適用操作で管理対象の設定だけをraw user dataへ一方向にmergeし、その他の設定を保持する。
  raw YAMLを送信内容の正本として適用後も自由に編集でき、raw側の変更をformへ逆同期しない。
- cloud-init user dataは`#cloud-config`から始まる単一のYAML mappingとして厳密に検証し、不正な内容を
  VM作成へ送信しない。平文passwordがuser dataとrequestへ含まれること、初回起動scriptがroot権限で
  実行されることをWeb UIで警告する。
- VMの起動・停止・削除と、noVNC経由のconsole接続を提供する。console接続は短命・一回限りの
  opaque ticketを使い、ticketをreverse proxyやAPIのaccess logへ残さない。

### Storage・image・network

- storage poolの発見、登録、metadata更新、再走査、削除を行える。
- volume/imageの一覧、metadata更新、HTTP download、削除を行える。
- libvirt networkの発見、作成、削除と、Open vSwitchのport group追加・削除を扱える。
- 複数のstorageやnetworkを、project設計で参照するresource poolとしてまとめられる。

### Project・flavor・非同期task

- backendはproject recordの作成・一覧・削除、利用者やVMとの関連付けを扱う。
- project modelはresource上限、pool、flavorの関連を保持するが、完全なquota強制やtenant isolationとは扱わない。
- flavor APIはOS、manual、icon、cloud-initなどのmetadataを管理し、imageと関連付けられる。
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

Web UIには、login・初期設定、VM、node、storage、image、network、利用者一覧、task一覧・詳細、
Agent端末・能力lease・global停止・`unknown` operation整合確認の管理画面がある。
projectとflavorはbackend APIおよび一部の関連操作に存在するが、独立した管理画面は現時点で提供しない。
dashboardは、認証利用者が参照できるVM、node、storage、image、network、taskの件数、状態、容量を、
DB上のinventory cacheとtask recordから集約した現在値のsnapshotとして表示する。
表示と再読込はread-onlyであり、管理nodeへのSSH・libvirt接続、inventory再走査、task投入を行わない。
集計対象は各APIの認可とprojectによる絞り込みに従い、利用者が参照できないresourceを含めない。

## 品質上の不変条件

- 認証が必要なresourceは、Bearer tokenなしで管理操作を許可しない。
- 長時間の管理操作はHTTP request内で完了を待たず、taskとして追跡可能にする。
- APIとworkerは同じDB、data領域、SSH credential、task keyの規約を共有する。
- DB schema変更はAlembicで再現可能にし、既存環境と新規環境の両方をupgradeできるようにする。
- frontendが利用するAPI型はOpenAPIから生成し、backend契約と同じ変更で同期する。
- 永続dataはcontainer imageの外に置き、再作成後もDB、管理data、SSH鍵を保持できるようにする。
- 配布WebはHTTPで待ち受け、TLS終端は運用者が外部reverse proxyまたはload balancerで任意に行う。
  平文HTTPはloopbackまたは信頼済み閉域だけで使用し、AgentのWebAuthn承認とproduction MCP接続には
  browserから見えるHTTPS originを用意する。
- 管理node上の削除、disk操作、network変更は破壊的であり得るため、対象を明示して実行する。
- Agent経由のmutationは監査書込み失敗時にfail closedとし、global停止、端末失効、端末別breakerを
  AI経路とは独立して操作できるようにする。
- Agentと既存RESTの双方で、projectからresource poolをたどってstorage、image、network、flavor、nodeの
  object認可を行う。projectへ対応付け不能なglobal操作はadminだけに許可する。
- Agent image downloadは管理nodeで接続先DNSの全addressを検証し、TLS hostname検証を保ったままglobal IPへ
  接続を固定する。redirect・proxyを使わず、既存file/imageをatomicに上書きしない。
- 30分内に失敗または`unknown`が3件発生した端末はmutationを停止する。全端末・全leaseを通じて
  R3は同時1件、全mutationは同時3件までとする。
- recoveryなしの削除と帯域外復旧なしのnetwork変更は、global設定と個別leaseの双方が明示的に許可した場合だけ実行する。

## 対応済みとみなさない範囲

コードや検証根拠がない限り、次を現行機能として文書化しない。

- 高可用なcontrol plane、複数workerによる分散実行、厳密なtenant isolation
- project上限とresource poolを全操作へ強制する完全なquota管理
- project・flavorの独立したWeb管理画面
- dashboard上の時系列chartやreal-time監視
- libvirt以外のhypervisorや、SSHで到達できない管理node
- 外部identity provider連携やpassword reset workflow
- internet上のRemote MCP endpoint、Secure MCP Tunnel、無人service principal
- backup・snapshotによる削除後の復元、帯域外network復旧、production canary環境
