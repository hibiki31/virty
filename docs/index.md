# Virty

低コストですぐに導入できるKVM管理WEBアプリケーションです。Virtyはコントローラとして、SSH経由でLibvirt-API、Ansibleを実行してノードを管理します。
SSH可能なLinuxノードをWEBダッシュボードからプロビジョニングできます。

## 免責事項

このソフトウェアの使用によって生じたいかなる損害についても作者は一切責任を負いません。

## クイックスタート

Virtyは管理予定のノード上でも、手元のPCでも運用できます。

1. [Docker](https://docs.docker.com/engine/install/)のインストール　※コンテナが起動できればDockerである必要はありません

2. Docker composeを使用したVirtyの起動

```
mkdir virty
cd virty
wget https://raw.githubusercontent.com/hibiki31/virty/refs/heads/master/compose.example.yml -O compose.yml
docker compose up -d
```

3. ブラウザで、`http://localhost:8765`または、`http://IP:8765`へアクセス　※デフォルトで0.0.0.0が許可されています

