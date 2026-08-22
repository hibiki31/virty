# 専用lab test

このdirectoryのtestはSSH・Ansible・libvirt資源とDBを変更する。通常の`pytest`では収集されない。
直接`pytest`を実行せず、repository rootから`devctl`だけを入口にする。

## 設定受け入れタスク

### 起動条件と安全境界

利用者が「試験用情報を提供します」と述べた場合、または同じ意味で専用lab設定の作成を申し出た場合に
このタスクを開始する。設定の準備と実機testの実行は別の許可として扱い、このタスクでは
`./devctl infra`を実行しない。

最初に、password、秘密鍵、tokenなどの機密情報を会話へ貼らないよう利用者へ伝える。
credentialや署名tokenを含むdownload URLは処理中のlogへ残り得るため使用せず、認証不要の専用test URLを用意する。
内部host名、IP address、usernameも組織上秘匿する場合は質問へ回答せず、最後の手動置換対象にできる。
機密情報が貼られた場合は値を使用、復唱、設定fileへ転記せず、露出済みとして失効・rotationを依頼する。

### 1. 非機密情報をヒアリングする

毎回、現在追跡されている`infra-config.example.json`を読み、次の順番でexample値からの変更点を質問する。
回答されていない値を推測しない。実際に使う非機密値は、回答済み、example値を明示承認済み、
手動置換指定のいずれかへ分類する。配列は各1件以上必要で、同じ種類の名前は重複できない。
この受け入れtaskでは、resourceへ使うbase nameを`[a-z0-9][a-z0-9-]{0,31}`に限定する。
storage template pathは空白、`.`、`..`を含まない正規化済み絶対pathとし、symlinkや共有範囲の広いparentを使わない。

| 順序 | JSON項目 | 確認内容 |
|---|---|---|
| 1 | `lab_id` | 本番・共有環境ではない専用labであることと、同じ物理labで安定したID。形式は`[A-Za-z0-9][A-Za-z0-9_.-]{0,63}` |
| 2 | `servers[]` | 各管理nodeの`name`、`domain`、SSH `username`。port 22の鍵認証、SFTP、passwordless sudo、libvirt/qemu/virshを利用できること。root権限が必要なpathは作成とcleanupの両方で同じ`become`境界を使う |
| 3 | `storages[]` | 管理node上の相互に異なる専用template path。名前の末尾`test-cloud`、`test-iso`、`test-img`を維持する。実行時にbasenameへrun IDを付けた派生pathは未存在で、共有範囲の広い親directoryを避け、接続userがpasswordless sudoで安全に作成・削除できること |
| 4 | `networks[]` | 末尾`test-nat`の名前、固定値`nat`の`type`、0〜255でlab内重複のない`octet`。`10.144.<octet>.0/24`が全nodeに作成される。別typeの検証はこの定型taskへ混在させない |
| 5 | `username`、`users[]`、`projects[]` | API管理者名、test user名、project名の変更有無。passwordと現行suiteで未使用の`users[].publickey`は質問しない |
| 6 | `vms[]` | VMのbase nameと台数。各VMを各serverへ4 vCPU、4 GiB RAM、64 GiB diskで作成できること。`network`は`networks[].name`のexact nameを参照し、VMの接続・更新postconditionに使用する。現行suiteで未使用の`image`はexample値を維持できる |
| 7 | `image_url`、`iso_url` | 認証情報を含まないHTTP(S) URL。末尾にfile名があり、test containerからHEAD・Range request、全nodeから通常downloadが可能であること。imageはqemuで64 GiBへcopy/resizeしてVM起動でき、ISOはCD-ROMへattachできる形式にする |

`users[].publickey`と`vms[].image`だけが現行testで未使用である。`vms[].network`は実際に使用し、
`projects[]`は検証・run固有prefix・manifest/cleanupで参照するため、いずれのfieldも削除しない。
全serverで使う`key`と対になる`pub`は、
一致を保つため最後に利用者が同時に手動置換する。
serverが2台以上ならnode間copy testも実行される。storage容量は、各serverとVMの組合せごとのdiskに加え、
image作成・download・copy分も見込んでoperatorが事前確認する。

作成とcleanupは同じpasswordless `become`境界を使い、cleanup直後にremote pathの不在を確認する。
rootでのSSH接続は必要なく、専用の非root SSH userと必要最小限のpasswordless sudoを用意する。

### 2. `.secrets/`へ設定を作成する

ヒアリング完了後にだけ、repository rootで次の配置を作る。`.secrets/infra-config.json`が既に存在する場合は
中身を表示せず停止し、利用者自身がbackup、移動、削除のいずれかを完了するまで上書きしない。

```console
install -d -m 0700 .secrets
if test -e .secrets/infra-config.json; then
  printf '%s\n' '.secrets/infra-config.json already exists; not overwritten' >&2
else
  install -m 0600 api/tests/external/infra-config.example.json .secrets/infra-config.json
fi
```

exampleのfield順と構造を維持し、確認済みの非機密値だけを反映する。次の値はplaceholderのままにし、
`allow_destructive`も`false`から変更しない。

- `password`: `__REPLACE_MANUALLY_ADMIN_PASSWORD__`
- `users[].password`: `__REPLACE_MANUALLY_USER_PASSWORD__`
- `key`: `__REPLACE_MANUALLY_OPENSSH_PRIVATE_KEY__`
- `pub`: `__REPLACE_MANUALLY_OPENSSH_PUBLIC_KEY__`
- 現行suiteで未使用の`users[].publickey`: `__UNUSED_BY_CURRENT_SUITE__`
- 利用者が手動置換を選んだ内部情報: field名を含む`__REPLACE_MANUALLY_...__`

作成後は`git check-ignore .secrets/infra-config.json`でignore対象であることを確認する。
file本文は出力せず、反映したJSON pathと未置換placeholderのJSON pathだけを利用者へ報告する。

### 3. 利用者へ秘密値の手動置換を依頼する

最後に、安全なlocal editorで`.secrets/infra-config.json`を開き、次を利用者自身で行うよう依頼する。

1. `password`と各`users[].password`を置換する。このtaskの安全policyとして両方を8〜128文字、空白なし、
   小文字・大文字・数字・記号を各1文字以上とする。test user passwordはAPI schemaもこの条件を強制する。
2. `key`をpassphraseなしのRSAまたはEd25519 OpenSSH秘密鍵、`pub`を同じkey pairの公開鍵へ置換する。
   JSON文字列内の秘密鍵の改行は`\n`とする。
3. 手動置換を選んだ内部情報があれば置換する。
4. `__REPLACE_MANUALLY_...__`、`replace-me`、`replace-with-dedicated-lab-id`、`example.invalid`、
   documentation用の`192.0.2.0/24`が残っていないこと、
   専用labだけを指していること、既存資源へ衝突しないこと、接続userが作成とcleanupの両方で
   必要なpasswordless sudoを使えることをreviewし、最後に`allow_destructive`を`true`へ変更する。

秘密値や完成した設定本文を返信させず、利用者からは置換完了の申告だけを受ける。
置換後のfileを表示、diff、stage、commitしない。`devctl`は親directoryがmode `0700`、fileがmode `0600`、
かつ両方が実行user所有でなければ本文を読む前に拒否する。

設定受け入れtaskではpreflightも実機testも実行しない。利用者がread-only到達性確認を依頼した後に、
標準`./devctl verify`の成功を確認してから次を実行する。

```console
./devctl infra preflight --config "$(realpath .secrets/infra-config.json)"
```

preflightの成功、collision/capacity結果と次の5 commandを示し、破壊的実行の明示承認を改めて得る。
承認後も各commandは別run IDを自動生成するため、1つずつ直列実行する。

```console
./devctl infra --config "$(realpath .secrets/infra-config.json)" --scenario happy
./devctl infra --config "$(realpath .secrets/infra-config.json)" --scenario task-failure
./devctl infra --config "$(realpath .secrets/infra-config.json)" --scenario worker-stop
./devctl infra --config "$(realpath .secrets/infra-config.json)" --scenario signal-int
./devctl infra --config "$(realpath .secrets/infra-config.json)" --scenario signal-term
```

`--scenario`を省略した場合は`happy`になる。各run後のcleanupと独立inventoryが0件を証明できなければ
そこで停止し、後続scenarioを実行しない。

## 実行時の安全境界

設定fileはread-onlyでmountされ、`allow_destructive: true`、空でない`lab_id`、専用labの
認証情報、server・storage・network・VM定義を必須とする。入口が生成する
`VIRTY_TEST_RUN_ID`はresource名とstorage pathへ付与され、同じlab内の並列runを分離する。
ただし同じ`lab_id`の同時実行は禁止し、host側lockでfail-closedにする。
設定modelは余分なfield、各配列の空・重複、server接続先、storage path、network octetの重複、非NAT、
credential/query/fragment付きURL、使用fieldのplaceholder、password policy違反、秘密鍵と公開鍵の
不一致をDBや管理nodeの起動前に拒否する。errorにはJSON pathと理由だけを出し、設定値を含めない。

`infra preflight`のreadiness phaseはproject固有SSH volumeへのkey配置を除き、専用labを変更しない。
全serverでSSH、SFTP、passwordless sudo、virsh/libvirt、qemu、Ansible facts、storage parentと容量、
download URLのHEAD/Range metadata、exact libvirt inventory、run固有remote pathの不在、および
`10.144.<octet>.0/24`と既存libvirt network・host routeの重複がないことを確認する。
衝突または容量不足ならcleanupをarmせず終了する。

mutation前に、version、lab ID、run ID、Compose project identityと、作成し得る全資源のexact name、
node、remote pathをproject-scoped volumeのmanifestへ原子的に永続化する。作成成功時は返却UUIDを追記し、
状態遷移とidentityを検証する。cleanupはmanifest記載targetだけをallowlistとし、configとrun IDからの
再構築はread-only診断にだけ使用する。破損、identity不一致、未記録targetではfail closedし、削除しない。

終了時はfixture finalizerとhost trapのcleanupが同じmanifestを読み、VM、network、storage、remote path、
project、node、userの依存順で冪等に回収する。作成時に`become`を使うremote pathはcleanupでも同じ境界を使う。
cleanup後は別serviceがmanifestのremovedを含む全targetについて、DB、virshのname/UUID、remote pathを
read-onlyで再inventoryする。manifest記載外でも同じrun ID prefixを持つDB・virsh資源は診断対象に含め、
すべて0件になった場合だけrunを成功とする。削除allowlist自体はmanifest記載targetから拡張しない。

scenario本体、cleanup、独立verifierのいずれかが失敗した場合はtest failureとして報告し、診断用の
Compose project、DB、SSH volume、manifestを保持する。signal scenarioは子processの停止を確認できない場合、
競合するcleanupを実行せずprojectを保持する。`signal-int`の130と`signal-term`の143は、
cleanupと独立inventoryが成功した場合だけscenario全体の期待終了として扱う。
external DBもproject-scoped named volumeへ保存し、失敗時にcontainerをTERM停止してもtaskとAPI inventoryを
manual cleanupへ引き継ぐ。成功時だけDBを含むproject volumeを削除する。
出力された次の形式のcommandを、障害を解消した同じ専用labで再実行する。別worktreeのprojectや任意の
project名は指定できない。

```console
./devctl infra cleanup --config "$(realpath .secrets/infra-config.json)" \
  --run-id run-YYYYMMDDhhmmss-PID-RANDOM \
  --project virty-WORKTREE_HASH-infra-EPOCH-PID
```

manual cleanupも同じlab lock、config permission、manifest identity、manifest-only allowlistと独立verifierを
必須とする。再試行成功までは保持projectを手動削除しない。

## 実機で確認するpostcondition

external suiteはproduction SSH・Ansible・libvirt・download adapter固有のpostconditionだけを担う。
auth、user、project、flavorのAPI契約は標準`tests/integration`へ移管し、実機suiteではtest前提の
最小setup以外を重複検証しない。

- 全serverでSSH/SFTP/sudo、facts、Ansible command、qemu、NAT network、3種storageを確認する。
- imageとISOを各serverへdownloadし、remote fileの存在・size・SHA-256とdelete後の不在を確認する。
- VMの作成、64 GiB disk、network interface、power遷移、CD-ROM XML、削除後のDB/virsh不在を確認する。
- networkとstorageは作成後のDB/virsh一致、および削除後の独立した不在を確認する。
- serverが2台以上なら全nodeが送信側と受信側になるring copyを行い、転送前後のSHA-256を比較する。
  1台だけの場合はnode間copyだけを理由付きskipする。

`happy`は上記全体、`task-failure`は実taskの診断付きerror、`worker-stop`は実行中workerの停止・再開、
`signal-int`/`signal-term`は資源作成後のprocess signalと回復性を、それぞれ有限時間内に確認する。
