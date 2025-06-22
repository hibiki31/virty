# Tailscale

Tailscale subnet routerと連携し、Virtyで作成したNWにアクセスできるようにします。

!!! note
    Tailscaleアカウントの登録、サーバの追加は完了している前提で記載

## Subnetrouter

[Tailscale公式ドキュメント](https://tailscale.com/kb/1019/subnets)

IP転送を有効にする

```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

サブネットをアドバタイズする

```bash
sudo tailscale set --advertise-routes=192.168.0.0/24,10.0.0.0/16
```

!!! note
    virtyで作成予定のサブネットが含まれるように、あらかじめ/16等大きく広告することをお勧めします。そうすればダッシュボードで10.0.3.0/24などを追加した際、ノード上でアドバタイズ、Tailscaleダッシュボードで承認する作業が不要になります。

## ネットワークの作成

virtyダッシュボードで`route`モードのネットワークを作成します。以上でTailscaleネットワークを経由したアクセスが可能になります。

!!! warning
    アクセスができない場合は、ノードのファイアウォール、Tailscale ACLをご確認ください。

## インターネット接続

現時点では、tailscaleネットワーク経由でVMにアクセス可能ですが、VMはインターネットに出れません。Routeing/NATの2種類でVMにインターネット接続を提供できます。

!!! warning
    ネットワーク同士の接続など、Linuxのネットワーク、ファイアウォールを考慮して適切に設定してください。

### Routing

ネットワークを`route`モードで作成すると、ノード上にL2仮想ネットワークが作成されます。このネットワークを、ノードが接続するゲートウェイ等に登録すれば一般的なL3ルーティングでインターネットに出ることができます。

```text
GWに登録するサブネット: 作成したネットワーク/作成予定のサブネット範囲 (例 10.0.0.0/16)
GWに登録するネクストホップ: ノードのIPアドレス(例 192.168.0.10)　
```

### NAT

ゲートウェイにネットワークが登録できない場合は、ノードのIPを用いたNAPTでインターネットに接続できます。

!!! warning
    VMはノードのIPを使用して、ノードが接続できるすべてのネットワークにアクセスできるようになります。適切にiptablesで制限をかける必要があります。

作成したネットワークのサブネットが`10.0.0.0/16`、インターネットに出れるインターフェイス`enp0s9`

```bash
sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/16 -o enp0s9 -j MASQUERADE 
```
