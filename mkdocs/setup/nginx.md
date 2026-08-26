---
title: 任意のHTTPSと閉域公開
---

`compose.example.yml`のWeb serviceはHTTPで待ち受け、証明書を読み込まない。
同じhostからの利用や信頼済み閉域ではHTTPのまま利用でき、HTTPSが必要な環境では
運用者が管理するNginx、Caddy、load balancerなどでTLSを終端する。

!!! warning
    平文HTTPではlogin password、Bearer token、noVNC通信が暗号化されない。
    internetへ直接公開せず、loopbackまたは接続元を制限した管理networkだけで使用する。

## HTTPで直接利用する

同じhostのbrowserだけから利用する最小設定では、Web serviceをloopbackへbindする。

```bash
export VIRTY_BIND_ADDRESS="127.0.0.1"
export VIRTY_PUBLIC_URL="http://localhost:8765"
export VIRTY_WEBAUTHN_RP_ID="localhost"
```

`VIRTY_PUBLIC_URL`にはbrowserから見えるoriginを指定する。private network上の別端末から
直接HTTPで接続する場合は実際のIP addressまたはhost名へ置き換え、host firewallでも接続元を制限する。

BrowserのWebAuthnはsecure contextを必要とし、production MCP helperも平文HTTPを拒否する。
そのためAgentのpairing、能力lease、管理操作を利用する環境では、次の外部HTTPS終端を構成する。

## 外部でHTTPSを終端する

内部CAまたは組織で利用しているCAから、Virty用FQDNをSANに含む証明書を発行する。
管理者browserとCodex端末の両方でCAを信頼させ、証明書errorを無視して運用しない。

TLS proxyをVirtyと同じhostで動かす例では、次の値を使用する。RP IDにはschemeやportを含めない。

```bash
export VIRTY_BIND_ADDRESS="127.0.0.1"
export VIRTY_PUBLIC_URL="https://virty.internal"
export VIRTY_WEBAUTHN_RP_ID="virty.internal"
```

次は外部Nginx用の設定例である。`map`は`http` contextへ置き、証明書pathとhost名を環境に合わせる。
WebSocketのUpgrade headerを転送し、SPA、API、noVNCを同じoriginのままVirty Web serviceへ渡す。

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    server_name virty.internal;
    return 308 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name virty.internal;

    ssl_certificate     /etc/nginx/tls/virty.crt;
    ssl_certificate_key /etc/nginx/tls/virty.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    add_header Strict-Transport-Security "max-age=31536000" always;

    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_http_version 1.1;
        proxy_set_header Host              $http_host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Upgrade           $http_upgrade;
        proxy_set_header Connection        $connection_upgrade;
        proxy_read_timeout 600s;
    }
}
```

TLS proxyを別hostで動かす場合は、`VIRTY_BIND_ADDRESS`をproxyから到達できるprivate addressへ変更し、
firewallでproxy以外から8765番への接続を拒否する。Virty Web serviceへのupstreamはHTTPのままとする。

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
curl http://127.0.0.1:8765/api/version
curl --cacert /path/to/internal-ca.crt https://virty.internal/api/version
```

`AGENT_PUBLIC_BASE_URL`と`AGENT_WEBAUTHN_ORIGIN`はComposeが`VIRTY_PUBLIC_URL`から設定する。
外部TLS終端時も内部の`http://127.0.0.1:8765`ではなく、browserから見えるHTTPS URLを指定する。
Host headerやproxy headerから公開URLを動的に推測させない。

## 組み込みTLSからの移行

以前の配布設定でWeb containerへ証明書をmountしていた環境では、更新後の8765番はHTTPSではなくHTTPになる。
先に外部TLS proxyを用意してupstreamを`http://VIRTY_HOST:8765`へ向け、外部URLでの動作を確認してから更新する。
更新後は`VIRTY_TLS_CERT`と`VIRTY_TLS_KEY`をenvironment fileから削除できる。
