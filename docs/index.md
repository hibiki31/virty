---
hide:
  - navigation
---

# Home

Virtyは、低コストでの運用を目的としたKVM管理用のWebアプリケーションです。コントローラとして、SSH経由でLibvirt APIやAnsibleを実行し、ノードの管理を行います。SSH接続が可能なLinuxノードに対して、Webダッシュボードからプロビジョニングを実施できます。

![メインイメージ](https://github.com/user-attachments/assets/f6d7e081-f327-4cfb-8d5a-9dbeaf274c7d)

<a href="https://github.com/hibiki31/virty/wiki/Preview-Image-v5" target="_blank">他のプレビューイメージ(v5.0.0)</a>

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

詳細は[最小構成での構築](/virty/setup/minimum/)をご確認ください。

## コンセプト

もともとは、主催するコンテストや講義で提供するVMの作成に利用していたコードを、オープンソースとして公開しました。

1. 仮想マシンの利用者、管理者、両方が利用しやすいWEBダッシュボード
2. すぐに立てて、すぐに壊せる、雑に扱っても壊れないコントローラ
3. Pythonスクリプト等からAPIを叩いて同じ形式のVMを一括作成できる
4. VMware ESXiのような使用感で複数のサーバを管理できる
