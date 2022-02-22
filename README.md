# Virty

低コスト・即時展開を目的としたLibvirt-APIのWEBインターフェイス

SSH経由でLibvirt-API,Ansible,コマンド(qemu-img)などを実行

![2022-02-16 023805](https://user-images.githubusercontent.com/35087924/154118366-c61572bc-ee45-4a97-a825-2e5f95cc5cd5.png)

> 現段階ではWEBインターフェイスをグローバルなど、信用できないネットワークに設置しない

### 特徴

- Virtyは全てのノード操作をSSHを経由して行います。よってSSH接続できる全てのノードを管理可能
- ノードの最小構成はlibvirtデーモンのインストールのみ

### サポートOS

Virtyはdocker-composeが利用できるx86_amd64環境で動作

管理対象ノードのサポートOS

- Ubuntu 18, 20
- CentOS 7, 8

## クイックスタート

現時点ではDocker-composeでの構築のみサポート

### 1.Virtyの構築

##### 1.リポジトリのクローン（最新のみ取得）

```
git clone --branch master --depth 1 https://github.com/hibiki31/virty.git
```

##### 2.Dockerイメージのビルドと起動

```
cd virty
cp docker-compose.example.yml docker-compose.yml
docker-compose build
docker-compose up -d
```

##### 3.データベースの初期化

```
docker-compose run main alembic upgrade head
```


##### 4.管理ユーザの作成

http://localhost:80 

へアクセスするとログイン画面が表示される

回起動時はセットアップダイアログが表示される

表示されない場合は何らかのエラーが発生している

ブラウザコンソールログとDockerログを確認する


### 2.ノード追加

##### 1.内容

OSによらず以下の状態を構築

- SSH公開鍵の設置
- パスワードレスsudo
- libvirtデーモンの起動
- qemu-imgコマンドが使用可能

##### 2. パッケージ Ubuntu 18 & 20

以下のパッケージをインストール

```
sudo apt update
sudo apt upgrade
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils
```

```
systemcltl enable libvritd
```

##### 2. パッケージ CentOS 7 & 8

以下のパッケージをインストール

```
yum -y install libvirt libvirt-client qemu-kvm virt-manager bridge-utils
```

```
sudo systemctl status libvirtd.service
```

##### 3.パスワードレスsudo

使用するテキストエディタを選択

```
sudo update-alternatives --config editor
```

Virty管理用のユーザーにNOPASSWD権限を付与

```
sudo visudo
-- 末尾 --
username ALL=(ALL) NOPASSWD: ALL
```

##### 4.SSH公開鍵の設置

何らかの方法で管理対象ノードに公開鍵を設置

```
ssh-copy-id user@host
```

> この後、ダッシュボードから鍵を登録すると`./data/key`に格納される


## 3. Open vSwitch(Option)

##### 1. 構成

物理インターフェイスに複数のVLAN Bridgeを作成

| 設定項目               | 値            |
| ---------------------- | ------------- |
| Bridge名               | ovs-br0       |
| Bridgeインターフェイス | eth0          |
| Native VLAN            | 100           |
| IPを設定するVLAN       | 200           |
| IP                     | 192.168.200.1 |

##### 2. パッケージ Ubuntu 18 & 20

```bash
sudo apt update
sudo apt install openvswitch-common openvswitch-switch
sudo systemctl status openvswitch-switch.service
```

##### 2. パッケージ CentOS 7 & 8

```bash
yum install -y openvswitch python-openvswitch
systemctl start openvswitch
systemctl enable openvswitch
```

##### 3. ブリッジの作成

```bash
# ブリッジの作成
ovs-vsctl add-br ovs-br0
# 物理インターフェイスを接続
ovs-vsctl add-port ovs-br0 eth0
# ブリッジ名と同名の自動作成されたポートにTAGを指定
# IPを設定するインターフェイスになる
ovs-vsctl set port ovs-br0 tag=200
# 物理インターフェイスにNative VLANを指定
ovs-vsctl set port eth0 tag=100 vlan_mode=native-untagged
# 確認
ovs-vsctl show
```

##### 4. IPを設定 Ubuntu 18 & 20

```yaml
network:
  ethernets:
    eth0:
      dhcp4: false
    ovs-br0:
      dhcp4: false
      addresses:
        - 192.168.200.1/24
      gateway4: 192.168.200.254
      nameservers:
        addresses: [ 192.168.200.254 ]
  version: 2
```

##### 4. IPを設定 CentOS 7 & 8

未検証
