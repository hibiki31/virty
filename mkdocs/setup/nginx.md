---
title: HTTPSと閉域公開
---

VirtyのWebAuthnとAgent APIはHTTPS originを前提とする。`compose.example.yml`のWeb serviceは
TLS 1.2/1.3で待ち受け、HTTPをHTTPSへredirectする。

## 証明書と名前

内部CAまたは組織で利用しているCAから、Virty用FQDNをSANに含む証明書を発行する。
管理者browserとCodex端末の両方でCAを信頼させる。証明書errorを無視して運用しない。

次の値は同じhost名を指す必要がある。RP IDにはschemeやportを含めない。

```bash
export VIRTY_BIND_ADDRESS="192.0.2.10"
export VIRTY_PUBLIC_URL="https://virty.internal:8765"
export VIRTY_WEBAUTHN_RP_ID="virty.internal"
export VIRTY_TLS_CERT="/etc/virty/tls/virty.crt"
export VIRTY_TLS_KEY="/etc/virty/tls/virty.key"
```

`VIRTY_BIND_ADDRESS`にはinternetへrouteされない管理interfaceのaddressを指定し、host firewallでも
Codex端末と管理者端末からの接続だけを許可する。

## signing key

Web UI JWTと能力leaseは異なるkeyを使用する。値をrepositoryやCompose fileへ直接記載せず、
権限を制限したenvironment fileまたはsecret managerから与える。

```bash
export VIRTY_SECRET_KEY="$(openssl rand -hex 32)"
export VIRTY_AGENT_LEASE_SIGNING_KEY="$(openssl rand -hex 32)"
export VIRTY_AGENT_TASK_ENCRYPTION_KEY="$(openssl rand -base64 32)"
```

再起動時も同じ値を使う。keyを変更すると既存のWeb sessionまたは能力leaseは無効になる。
`VIRTY_AGENT_TASK_ENCRYPTION_KEY`だけはAES-256用の32 byteをbase64化した値であり、
hex文字列を指定してはいけない。

## 起動後の確認

```bash
docker compose config
docker compose up -d
curl --cacert /path/to/internal-ca.crt https://virty.internal:8765/api/version
```

`AGENT_PUBLIC_BASE_URL`と`AGENT_WEBAUTHN_ORIGIN`はComposeが`VIRTY_PUBLIC_URL`から設定する。
Virtyの前段でさらにreverse proxyを使う場合も、外部URLをこの値へ設定し、Host headerから動的に推測させない。
