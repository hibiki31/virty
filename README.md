# Virty

低コスト・即時展開を目的としたLibvirt-APIのWEBインターフェイスです．SSH経由でLibvirt-API,Ansible,コマンド実行(qemu-img)などを実行します．

> 現段階ではWEBインターフェイスをグローバルなど，信用できないネットワークに設置しないでください．

### 特徴

- Virtyは全てのノード操作をSSHを経由して行います．よってSSH接続できる全てのノードを管理できます．
- ノードの最小構成はlibvirtデーモンのインストールのみです．
- ユーザはWEBインターフェイスを利用して操作を行えます．

### サポートOS

　Virtyはdockerで動くので制約はありません、管理対象ノードのサポートOSは以下になります．確認していませんが他のOSでも動くかもしれません．

- Ubuntu 20, 18
- CentOS 8, 7

## クイックスタート

Virtyを構築し，ノードを管理対象に追加するまでを示します．

現時点ではDocker-composeでの構築のみサポートしています．

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

＊イメージのビルド中でエラーが発生する場合

```
docker image rm centos:8 
docker image prune -a
```

##### 3.管理ユーザの作成

http://localhost:80 へアクセスするとログイン画面が表示されます．
ログインボタンの隣のセットアップボタンをクリックします．
管理ユーザを登録できます，ユーザが存在しない時のみ実行できます．



### 2.ノード追加

##### 1.内容

OSによらず以下の状態を構築します．

- コンテナ内からSSHが可能
- パスワード入力なしでsudoが可能
- libvirtデーモンの起動
- qemu-imgコマンドが使用可能

##### 2. パッケージ Ubuntu 18 & 20

以下のパッケージをインストールします

```
sudo apt update
sudo apt upgrade
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils
```

```
systemcltf enable libvritd
```

##### 2. パッケージ CentOS 7 & 8

以下のパッケージをインストールします

```
yum -y install libvirt libvirt-client qemu-kvm virt-manager bridge-utils
```

```
sudo systemctl status libvirtd.service
```

##### 3.パスワード入力なしでsudo

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

##### 4.コンテナからSSHアクセス

既存の鍵を使用する場合以下のホストディレクトリに設置してください
コンテナ内の.sshにマウントされます

```
./data/key
```

コンテナに接続します

```
docker exec -it virty_virty-main_1 bash
```

コンテナ内からSSH接続し、パスワード入力無しでSSHが可能か確認

```
ssh-copy-id user@host
```

##### 5.ダッシュボードで追加

ダッシュボードにアクセス > サイドバー > Node > Add で入力し追加



