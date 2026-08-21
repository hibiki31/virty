# virty-mcp

Codex DesktopからVirty Agent APIを閉域操作する、local stdio MCP helperである。
既存REST APIやSSHを汎用proxyとして公開せず、review済みの
[`action_catalog.json`](src/virty_mcp/action_catalog.json)だけをMCP toolへ変換する。

```text
Codex Desktop ── stdio ──> virty-mcp ── internal HTTPS + DPoP ──> Virty Agent API
```

端末のP-256秘密鍵、pairing code、能力lease tokenは`config.toml`やfileへ保存せず、
Keyring経由でOS credential storeへ保存する。LinuxではSecret Service、macOSではKeychain、
WindowsではCredential Lockerが必要であり、plaintext/fail backendでは起動を拒否する。
保存状態は正規化したVirty originへ束縛し、URL変更後に別originへtokenを送らない。
能力leaseは承認済みdevice IDにも束縛し、期限切れを送信前に拒否する。再pairingが完了した時点で
旧device用のlocal leaseは破棄する。
HTTP proxyとredirectは使用せず、internal CAを検証するTLS 1.2以上の直接接続だけを許可する。

## Install

Python 3.11以上とOS credential storeを用意してから、専用virtual environmentへinstallする。

```bash
cd /absolute/path/to/virty/virty_mcp
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install .
```

Linuxのheadless sessionではSecret ServiceのD-Bus sessionを先に構成する。
`keyrings.alt`等のplaintext file backendへfallbackしてはいけない。

## Codex Desktop登録

OpenAIの公式MCP設定では、local serverを`[mcp_servers.<name>]`の`command`で登録し、
`env`で環境変数を渡せる。Codex Desktop、CLI、IDE extensionは同じ設定を共有する。
[公式MCP設定](https://developers.openai.com/codex/mcp/)

[`config.example.toml`](config.example.toml)を`~/.codex/config.toml`へ反映し、
`command`、Virty URL、internal CAの絶対pathを端末に合わせて変更する。access tokenや秘密鍵を
`env`へ追加してはいけない。DesktopではSettings → MCP serversから同じstdio commandを登録できる。

登録後にCodex Desktopを再起動し、`/mcp`で`virty`が接続済みであることを確認する。

## Pairingとlease lifecycle

lifecycle/control toolは`virty.device.pair`、`virty.device.pairing_status`、
`virty.lease.begin`、`virty.lease.status`、`virty.session.status`、
`virty.operation.get`、`virty.operation.cancel`の7個である。

1. `virty.device.pair`へ端末名と最小scopeを渡す。
2. 返されたpairing codeをVirty Web UIでWebAuthn承認する。
3. `virty.device.pairing_status`を呼び、`active`になったdevice IDをlocal保存する。
4. `virty.lease.begin`へprincipal、scope、project/node制約、最大変更数を渡す。
5. 返されたrequest IDをVirty Web UIでWebAuthn承認する。
6. `virty.lease.status`をpollする。承認済みなら同じ端末鍵のDPoP proofでone-time exchangeし、
   取得した30分leaseをOS credential storeへ保存する。WebAuthn assertionはhelperやモデルを通らない。
7. `virty.session.status`でtokenを表示せず、有効期限と上限だけを確認する。

scopeはcatalogのaction ID完全一致（例: `vm.get`、`vm.power.update`）か、明示的な
wildcard（`vm.*`または`*`）で指定する。MCP tool名ではなく各toolの
`jp.virty/action` metadataを使用する。

鍵をrotateする場合は、先に旧deviceをVirty Web UIで失効する。
`virty.device.pair`の`replaceKey=true`はlocal鍵を置換するだけで、server上の旧deviceを失効しない。

## Actionとoperation

- 63個の管理actionを`virty.<resource>.<verb>`として公開する。auth/setup、console ticket、
  internal VNC resolver、任意shell、任意API proxyはcatalogへ含めない。
- 全input schemaはnested objectを含め`additionalProperties=false`とし、全toolがstructured contentと
  `outputSchema`、read-only/destructive/idempotent/open-world annotationを持つ。
- 変更toolは`idempotencyKey`と文字列`expectedGeneration`を必須とする。create、refresh等の
  既存target generationを持たないactionは`"0"`、既存resourceは直前のreadで得た
  `generation`または`updateToken`等をそのまま指定する。
- 同じ処理をretryするときは同じidempotency keyを使う。新しいkeyを作る前に
  `virty.operation.get`で既存operationを確認する。
- `virty.operation.cancel`は協調的な取消要求であり、すでに完了した外部処理を巻き戻さない。
- Agent API応答にaccess token、password、password hash、秘密鍵、VNC passwordが混入しても、
  helperはMCPへ返す前に再帰的にredactする。write-only inputがtask log等の自由textへ
  埋め込まれた場合も既知値を置換する。

## MCP protocol

- MCP `2026-07-28`の`server/discover`、initialize時のsession negotiation、newline-delimited stdio、
  `tools/list`、`tools/call`、structured content、output schemaに対応する。
- `io.modelcontextprotocol/tasks`をadvertiseする。対応clientが明示opt-inした変更toolは
  Agent APIのdurable operation IDをMCP task IDとして返し、`tasks/get`と`tasks/cancel`へbridgeする。
- `tasks/update`はVirty operationがclient inputを要求しないため、task所有権を確認して未知responseを
  無視し、空ackを返す。
- Tasks非対応clientには`OperationAccepted`を通常のstructured tool resultとして返すため、
  `virty.operation.get`でpollできる。
- 現行Codex hostとの互換のため、initialize-eraの`2025-11-25`、`2025-06-18`、
  `2025-03-26`、`2024-11-05` handshakeも受け付ける。Tasks拡張は`2026-07-28`でだけ有効にし、
  initializeでclientが明示した場合だけ有効化する。legacy clientには通常resultへfallbackし、
  `progressToken`等の標準または未知の`_meta` fieldは通常requestで拒否しない。

## Test

```bash
cd /absolute/path/to/virty/virty_mcp
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/pytest
```

contract testは次をfail closedで確認する。

- helper catalogと`api/agent/catalog.py`のaction ID、risk、mutation、destructive、resource typeが一致する。
- 現行routerの管理endpointがcatalogへ明示対応し、auth/setup/VNC系が除外される。
- 全schemaがJSON Schema 2020-12として有効で、rootが`additionalProperties=false`である。
- DPoP proofがmethod、URL、lease tokenの`ath`へ束縛され、ES256署名が検証できる。
- Tasks対応/非対応fallback、冪等性envelope、秘密値redaction、stdio framingが維持される。

unit/contract testはfake transportとmemory credential storeを使い、Virty、libvirt、SSH、Ansibleへ
接続せず副作用を起こさない。

## Environment

| Variable | Required | Meaning |
|---|---:|---|
| `VIRTY_AGENT_BASE_URL` | yes | VirtyのHTTPS origin。path、query、fragmentなし |
| `VIRTY_TLS_CA_FILE` | internal CA利用時 | server certificateを検証するPEM CA bundle |
| `VIRTY_AGENT_TIMEOUT_SECONDS` | no | 1〜300秒。default 30 |
| `VIRTY_MCP_PROFILE` | no | credential namespace。default `default` |
| `VIRTY_ALLOW_INSECURE_LOOPBACK` | test only | `true`ならloopback HTTPだけ許可 |
