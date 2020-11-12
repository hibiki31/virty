# Virty

低コスト・即時展開を目的としたLibvirt-APIのWEBインターフェイスです。SSH経由でLibvirt-API,Ansible,コマンド実行(qemu-img)などを使用します。

> 現段階ではWEBインターフェイスをグローバルなど信用できないネットワークにさらさないでください。



## 構成

### 概要

- Virtyは全てのノード操作をSSHを経由して行います。よってSSH接続できる全てのノードを管理できます。
- ユーザーはHTTP経由でWEBインターフェイス及びWEB-APIに接続できます。
- ノードの最小構成はlibvirtデーモンのインストールのみです。手順が載っています。



### サポートノードOS
　virty自身はdockerで動くので制約はありません、しかし管理対象のOSサポートは以下になります。

- Ubuntu 20
- Ubuntu 18
- CentOS 8
- CentOS 7



## Virty構築

現時点ではDocker-composeのみサポートしています。

### docker-compose

リポジトリのクローン（最新のみ取得）

```
git clone --branch master --depth 1 https://github.com/hibiki31/virty.git
```

リポジトリのクローン

```
git clone https://github.com/hibiki31/virty.git
```

Dockerイメージのビルドと起動

```
cd virty
docker-compose build
docker-compose up -d
```

＊イメージのビルド中でエラーが発生する場合、以下を実行してください

```
docker image rm centos:8 
docker image prune -a
```

WEBインターフェイスにアクセスできます

```
http://Dockerホスト
user=admin,password=admin
```



## ノードの準備

### Ubuntu 18

#### 最低構成

以下のパッケージをインストールします

```
sudo apt update
sudo apt upgrade
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils 
```

使用するテキストエディタを選択します

```
sudo update-alternatives --config editor
```

Virty管理用のユーザーにNOPASSWD権限を与えます

```
sudo visudo
-- 末尾 --
username ALL=(ALL) NOPASSWD: ALL
```



#### ネットワーク

ネットワーク構成はLinux bridgeかOpen vSwitchを排他的に選べます。

| 使用         | 使用できる機能                        |
| ------------ | ------------------------------------- |
| Linux bridge | 手動でのbridge,vlan-bridgeの作成      |
| Open vSwitch | Virty経由でのbridge,vlan-bridgeの作成 |

##### Linux bridge

```
sudo bridge-utils 
```

##### Open vSwitch

デフォルトのLibvirtネットワークの削除



### CentOS 7

以下のパッケージをインストールします

```
yum -y install libvirt libvirt-client qemu-kvm virt-manager bridge-utils
```



## ノードの追加

### 条件

OSによらず以下の条件を満たしている必要があります

- 管理者権限を有するユーザーのSSHアクセス
- libvirtデーモンが起動しSSH経由で接続できる
- qemu-imgコマンドが使用できる



### コンテナからSSHアクセス

既存の鍵を使用する場合以下のディレクトリに設置してください。コンテナ内の.sshと接続されています。

```
cd virty/key
```

コンテナに接続します。

```
cd virty
docker exec -it virty_virty-main_1 bash
```

コンテナ内からSSH接続し、プロンプトなしでSSHできるようにしてください。