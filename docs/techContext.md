# Tech Context - 技術スタック・依存ライブラリ・設定

## バージョン情報

| コンポーネント | バージョン |
|--------------|----------|
| API | 5.1.2 |
| フロントエンド | 5.1.2 |
| 現在ブランチ | release-5.2.0 |

## バックエンド技術スタック

### 言語・フレームワーク

| 技術 | バージョン | 用途 |
|------|----------|------|
| Python | 3.9+ | バックエンド言語 |
| FastAPI | 0.115.13 | Webフレームワーク |
| uvicorn | 0.34.3 | ASGIサーバー |
| SQLAlchemy | 2.0.41 | ORM |
| Alembic | 1.16.2 | DBマイグレーション |
| PostgreSQL | 16 | データベース |
| psycopg2-binary | 2.9.10 | PostgreSQLドライバ |

### 仮想化・インフラ

| 技術 | バージョン | 用途 |
|------|----------|------|
| libvirt-python | 11.4.0 | libvirt API操作 |
| ansible | 11.7.0 | 構成管理・リモート実行 |
| ansible-runner | 2.4.1 | Ansible実行管理 |
| paramiko | 3.5.1 | SSH接続 |

### 認証・セキュリティ

| 技術 | バージョン | 用途 |
|------|----------|------|
| PyJWT | 2.10.1 | JWT生成・検証 |
| bcrypt | 4.3.0 | パスワードハッシュ |

### ユーティリティ

| 技術 | バージョン | 用途 |
|------|----------|------|
| httpx | 0.28.1 | HTTPクライアント |
| rich | 14.0.0 | ログ・出力フォーマット |
| python-multipart | 0.0.20 | ファイルアップロード |
| prometheus-fastapi-instrumentator | 7.1.0 | Prometheusメトリクス |

### コード品質

| ツール | 設定 |
|-------|------|
| Ruff | ターゲット: py39, ルール: E, F |

## フロントエンド技術スタック

### コア

| 技術 | バージョン | 用途 |
|------|----------|------|
| Vue | 3.5.14 | UIフレームワーク |
| TypeScript | ~5.7.3 | 型安全な開発 |
| Vite | ^6.2.5 | ビルドツール |
| Vuetify | ^3.8.4 | UIコンポーネントライブラリ |
| Pinia | ^3.0.2 | 状態管理 |

### ルーティング・レイアウト

| 技術 | バージョン | 用途 |
|------|----------|------|
| vue-router | ^4.5.1 | ルーティング |
| unplugin-vue-router | ^0.12.0 | ファイルベースルーティング |
| vite-plugin-vue-layouts-next | ^0.4.2 | レイアウトシステム |

### API連携

| 技術 | バージョン | 用途 |
|------|----------|------|
| openapi-fetch | ^0.13.5 | 型安全APIクライアント |
| openapi-typescript | ^7.6.1 | OpenAPI→TypeScript型生成 |

### UI・UX

| 技術 | バージョン | 用途 |
|------|----------|------|
| @mdi/font | ^7.4.47 | マテリアルデザインアイコン |
| @kyvg/vue3-notification | ^3.4.1 | 通知表示 |
| highlight.js | ^11.11.1 | コードハイライト |
| @highlightjs/vue-plugin | ^2.1.0 | highlight.js Vue統合 |

### 認証

| 技術 | バージョン | 用途 |
|------|----------|------|
| typescript-cookie | ^2.0.0 | Cookie操作 |
| jwt-decode | ^4.0.0 | JWTデコード |

### 開発ツール

| 技術 | バージョン | 用途 |
|------|----------|------|
| unplugin-auto-import | ^19.1.2 | 自動インポート |
| unplugin-vue-components | ^28.4.1 | コンポーネント自動登録 |
| unplugin-fonts | ^1.3.1 | フォント管理 |
| vue-tsc | ~2.2.8 | Vue TypeScript型チェック |
| eslint | ^9.22.0 | コード品質 |

## 環境変数

### API

| 変数名 | デフォルト | 説明 |
|--------|----------|------|
| SQLALCHEMY_DATABASE_URL | postgresql://... | DB接続文字列 |
| LOG_MODE | text | ログ形式（text/json） |
| IS_DEV | false | 開発モードフラグ |
| SECRET_KEY | - | JWT署名キー |

### フロントエンド

| 変数名 | 値 | 説明 |
|--------|---|------|
| VITE_API_URL | /api/v1 | APIベースURL |

## Docker構成

### compose.example.yml サービス

| サービス | イメージ/ビルド | ポート | 備考 |
|---------|---------------|-------|------|
| api | ./api | 7799 | FastAPIサーバー |
| worker | ./api | - | タスクワーカー（command: worker） |
| web | ./vue | 3000 | Nginx + Vue SPA |
| proxy | ./proxy | 443 | リバースプロキシ |
| db | postgres:16 | 5432 | PostgreSQL |

### 開発用（compose.dev.yml）
- API: ホットリロード対応
- dev.sh: OpenAPI型生成パイプライン
