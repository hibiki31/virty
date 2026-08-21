# 専用lab test

このdirectoryのtestはSSH・Ansible・libvirt資源とDBを変更する。通常の`pytest`では収集されない。
直接`pytest`を実行せず、repository rootから次の一意な入口を使う。

```console
cp api/tests/external/infra-config.example.json /safe/private/path/infra-config.json
# 専用labの値へ置換し、最後にallow_destructiveをtrueへ変更する
./devctl infra --config /absolute/path/to/infra-config.json
```

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
./devctl infra cleanup --config /absolute/path/to/infra-config.json \
  --run-id run-YYYYMMDDhhmmss-PID-RANDOM \
  --project virty-WORKTREE_HASH-infra-EPOCH-PID
```

設定へ格納する公開鍵の準備

```
cat ~/.ssh/id_ed25519 | sed ':a;N;$!ba;s/\n/\\n/g'
```
