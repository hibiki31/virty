# Home

Virtyは、低コスト運用を目的とした、KVM管理WEBアプリケーションです。Virtyはコントローラとして、SSH経由でLibvirt-API、Ansibleを実行してノードを管理します。
SSH可能なLinuxノードをWEBダッシュボードからプロビジョニングできます。

<img width="1436" alt="スクリーンショット 2025-06-22 3 00 45" src="https://github.com/user-attachments/assets/f6d7e081-f327-4cfb-8d5a-9dbeaf274c7d" />

[他のプレビューイメージ(v5.0.0)](https://github.com/hibiki31/virty/wiki/Preview-Image-v5)

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

