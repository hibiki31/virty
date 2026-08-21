# アーキテクチャ

## この文書の役割

Virtyのcomponent境界、主要なdata flow、変更時に保持すべき設計上の不変条件を説明する。
全file、endpoint、class、DB列の一覧は持たず、詳細はコードとOpenAPIを正本とする。

## System context

```text
Browser ---------------------------> web: Nginx + Vue SPA
web -- /api -----------------------> api: FastAPI
web -- /novnc ---------------------> proxy: websockify -- console token照会 --> api
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

### 非同期resource操作

1. task routerが`method.resource.object`の組とrequest情報をDBへ保存する。
2. 後続処理がある場合は依存taskを`wait`で登録し、先行taskのUUIDを関連付ける。
3. workerは`init`と`wait`をpollし、実行可能なtaskを`start`へ遷移させる。
4. 登録済みhandlerがlibvirt、Ansible、SSHを介して処理し、`finish`または`error`、message、
   失敗時のtracebackを記録する。
5. worker起動時に残っていた実行途中のtaskは`lost`へ遷移する。

taskは外部message brokerではなくPostgreSQLをqueueと状態storeに兼用する。workerを増やす変更では、
row lockだけでなく、外部resourceへの重複実行と冪等性を再検討する。

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
- 管理node操作はbackend interfaceを越えて行い、標準testからproduction adapterへ接続しない。
