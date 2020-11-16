# Virty

低コスト・即時展開を目的としたLibvirt-APIのWEBインターフェイスです。SSH経由でLibvirt-API,Ansible,コマンド実行(qemu-img)などを実行します。

> 現段階ではWEBインターフェイスをグローバルなど信用できないネットワークにさらさないでください。



## 構成

### 概要

- VirtyはDockerコンテナで実行し、ノード上で動いているかは問いません。
- Virtyは全てのノード操作をSSHを経由して行います。よってSSH接続できる全てのノードを管理できます。
- ノードの最小構成はlibvirtデーモンのインストールのみです。手順が載っています。
- ユーザーはHTTP経由でWEBインターフェイス及びWEB-APIに接続できます。



### サポートOS

　Virty自身はdockerで動くので制約はありません、管理対象のノードOSのサポートは以下になります。確認していませんが他のOSでも動くかもしれません。

- Ubuntu 20
- Ubuntu 18
- CentOS 8
- CentOS 7



## Virty構築

現時点ではDocker-composeでの構築のみサポートしています。

### docker-compose

リポジトリのクローン（最新のみ取得）

```
git clone --branch master --depth 1 https://github.com/hibiki31/virty.git
```

Dockerイメージのビルドと起動

```
cd virty
cp docker-compose.example.yml docker-compose.yml
docker-compose build
docker-compose up -d
```

＊イメージのビルド中でエラーが発生する場合以下を試す

```
docker image rm centos:8 
docker image prune -a
```

WEBインターフェイスにアクセスできます

```
http://Dockerホスト
user=admin,password=admin
```



## ノード準備

### 1. 条件

OSによらず以下の条件を満たしている必要があります。

- コンテナ内からのSSHアクセスでノーパスワードsudoが実行可能
- libvirtデーモンが起動しSSH経由で接続できる
- qemu-imgコマンドが使用できる



### 2. Ubuntu 18 & 20

以下のパッケージをインストールします

```
sudo apt update
sudo apt upgrade
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils
```

```
systemcltf enable libvritd
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



### 2. CentOS 7 & 8

以下のパッケージをインストールします

```
yum -y install libvirt libvirt-client qemu-kvm virt-manager bridge-utils
```

```
sudo systemctl status libvirtd.service
```



### コンテナからSSHアクセス

既存の鍵を使用する場合以下のホストディレクトリに設置してください。コンテナ内の.sshにマウントされます

```
virty/data/key
```

コンテナに接続します

```
cd virty
docker exec -it virty_virty-main_1 bash
```

コンテナ内からSSH接続し、パスワード入力無しでSSHできるようにする

```
ssh-copy-id user@host
```

