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
| 2 | `servers[]` | 各管理nodeの`name`、`domain`、SSH `username`。port 22の鍵認証、SFTP、passwordless sudo、libvirt/qemu/virshを利用でき、接続userが`/tmp`、`/var/lib/libvirt/test`、storage親directoryでrun専用pathを直接作成・削除できること |
| 3 | `storages[]` | 管理node上の相互に異なる専用template path。名前の末尾`test-cloud`、`test-iso`、`test-img`を維持する。実行時にbasenameへrun IDを付けた派生pathは未存在で、共有範囲の広い親directoryを避け、接続userが安全に作成・削除できること |
| 4 | `networks[]` | 末尾`test-nat`の名前、固定値`nat`の`type`、0〜255でlab内重複のない`octet`。`10.144.<octet>.0/24`が全nodeに作成される。別typeの検証はこの定型taskへ混在させない |
| 5 | `username`、`users[]`、`projects[]` | API管理者名、test user名、project名の変更有無。passwordと現行suiteで未使用の`users[].publickey`は質問しない |
| 6 | `vms[]` | VMのbase nameと台数。各VMを各serverへ4 vCPU、4 GiB RAM、64 GiB diskで作成できること。現行suiteで未使用の`image`、`network`はexample値を維持できる |
| 7 | `image_url`、`iso_url` | 認証情報を含まないHTTP(S) URL。末尾にfile名があり、test containerからHEAD・Range request、全nodeから通常downloadが可能であること。imageはqemuで64 GiBへcopy/resizeしてVM起動でき、ISOはCD-ROMへattachできる形式にする |

`users[].publickey`、`vms[].image`、`vms[].network`は現行testで未使用、`projects[]`は検証・prefix・cleanupだけで
参照されるが、いずれもschema上は必須なので削除しない。全serverで使う`key`と対になる`pub`は、
一致を保つため最後に利用者が同時に手動置換する。
serverが2台以上ならnode間copy testも実行される。storage容量は、各serverとVMの組合せごとのdiskに加え、
image作成・download・copy分も見込んでoperatorが事前確認する。

現行suiteには、`become`でroot所有のpathを作る処理に対し、cleanup playbookが`become`を使わない経路がある。
接続userがrun専用の`/tmp`、`/var/lib/libvirt/test`、storage派生pathをsudoなしで削除できることを
専用labで保証できなければ、設定の準備までで停止し、`allow_destructive`を`true`にせず実機testを拒否する。
この制約を回避するためにrootでのSSH接続を推奨しない。

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
   専用labだけを指していること、既存資源へ衝突しないこと、接続userがrun専用pathを直接削除できることをreviewし、最後に
   `allow_destructive`を`true`へ変更する。

秘密値や完成した設定本文を返信させず、利用者からは置換完了の申告だけを受ける。
置換後のfileを表示、diff、stage、commitしない。実機testは、利用者が別途明示的に依頼した場合だけ次のcommandを対象にする。

```console
./devctl infra --config "$(realpath .secrets/infra-config.json)"
```

## 実行時の安全境界

設定fileはread-onlyでmountされ、`allow_destructive: true`、空でない`lab_id`、専用labの
認証情報、server・storage・network・VM定義を必須とする。入口が生成する
`VIRTY_TEST_RUN_ID`はresource名とstorage pathへ付与され、同じlab内の並列runを分離する。
ただし同じ`lab_id`の同時実行は禁止し、host側lockでfail-closedにする。
設定の配列型、重複名、URL、絶対storage pathと、suiteが使う`test-cloud`、`test-iso`、
`test-img`、`test-nat`の名前suffixはDBや管理nodeを起動する前に検査する。

資源作成前に管理node上のexact resource名とremote pathをread-onlyでinventoryし、衝突があればcleanupを
有効化せず終了する。終了時は成功・失敗にかかわらず、このrun IDのexact名に一致する資源だけをVM、
network、storage、remote path、project/user、nodeの順で削除する。

cleanupに失敗した場合はtest failureとして報告し、診断用のCompose project、DB、SSH volumeを保持する。
出力された次の形式のcommandを、障害を解消した同じ専用labで再実行する。別worktreeのprojectや任意の
project名は指定できない。

```console
./devctl infra cleanup --config "$(realpath .secrets/infra-config.json)" \
  --run-id run-YYYYMMDDhhmmss-PID-RANDOM \
  --project virty-WORKTREE_HASH-infra-EPOCH-PID
```
