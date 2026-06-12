# System Patterns - アーキテクチャ・設計パターン

## 全体構成

```
virty/
├── api/          # FastAPI バックエンド (Python)
├── vue/          # Vue3 フロントエンド (TypeScript)
├── proxy/        # Nginxリバースプロキシ
├── docs/         # MkDocsドキュメント
├── memory-bank/  # プロジェクト記憶
├── compose.example.yml  # Docker Compose設定
└── dev.sh        # 開発用スクリプト（OpenAPI型生成）
```

## バックエンド (API) アーキテクチャ

### ディレクトリ構造（ドメイン分割）

```
api/
├── main.py          # FastAPIアプリ・ルーター登録・起動
├── models.py        # 全モデルインポート集約
├── worker.py        # 非同期タスクワーカー
├── settings.py      # 設定・環境変数
├── mixin/           # 共通基盤
│   ├── database.py  # DB接続・セッション管理
│   ├── router.py    # APIRouter設定
│   ├── schemas.py   # 共通スキーマ（ページネーション等）
│   ├── exception.py # カスタム例外・ハンドラ
│   ├── log.py       # ログ設定（JSON/テキスト切替）
│   └── timestamp.py # タイムスタンプMixin
├── auth/            # 認証（JWT・bcrypt）
├── user/            # ユーザー管理
├── node/            # ノード（libvirtホスト）管理
├── domain/          # 仮想マシン(ドメイン)管理
├── network/         # 仮想ネットワーク管理
├── storage/         # ストレージプール管理
├── images/          # ディスクイメージ管理
├── flavor/          # フレーバー（VM仕様テンプレート）
├── project/         # プロジェクト管理
├── task/            # タスクキュー管理
├── exporter/        # Prometheusメトリクス
├── module/          # ユーティリティモジュール
│   ├── virtlib.py   # libvirt操作ラッパー
│   ├── ansiblelib.py# Ansible操作ラッパー
│   ├── paramikolib.py# SSH操作
│   ├── cloudinitlib.py# cloud-init設定生成
│   ├── ovslib.py    # Open vSwitch操作
│   └── xmllib/      # libvirt XML生成
└── ansible/         # Ansibleモジュール
```

### 各ドメインモジュールの構成パターン

各ドメインは以下のファイルで構成される：

| ファイル | 役割 |
|---------|------|
| `models.py` | SQLAlchemyモデル定義 |
| `schemas.py` | Pydanticスキーマ（リクエスト/レスポンス） |
| `router.py` | 同期APIエンドポイント |
| `router_task.py` | タスク作成APIエンドポイント |
| `tasks.py` | タスク実行ロジック（@TaskBase.registryデコレータ） |

### 非同期タスクキューシステム

1. APIエンドポイント（`router_task.py`）がDBに`TaskModel`レコードを作成（status: "init"）
2. ワーカー（`worker.py`）が100msポーリングで"init"/"wait"タスクを取得・実行
3. タスク完了後、statusを"finish"/"error"に更新
4. `dependence_uuid`による依存チェーン対応（"wait"→親タスク完了後に"init"に遷移）

```python
# タスク登録パターン
@TaskBase.registry(method="post", resource="domain", object="domain")
def post_domain(self):
    # 実行ロジック
    pass

# タスク作成パターン（router_task.py）
task = TaskManager(db)
task.select(method="post", resource="domain", object="domain")
task.commit(user=user, req=req, body=body)
```

### データベースパターン

- SQLAlchemy ORM + Alembicマイグレーション
- `get_db()` ジェネレータによるセッション管理（FastAPI Depends）
- `TimestampMixin` で `created_at` / `updated_at` 自動管理

### 認証パターン

- JWT認証（cookieベース: `access_token`）
- `get_current_user` 依存関数でユーザー取得
- bcryptパスワードハッシュ

## フロントエンド (Vue) アーキテクチャ

### ディレクトリ構造

```
vue/src/
├── main.ts          # アプリエントリポイント
├── App.vue          # ルートコンポーネント（v-app + notifications）
├── pages/           # ファイルベースルーティング
│   ├── index.vue    # ダッシュボード
│   ├── login.vue    # ログイン
│   ├── domains/     # VM管理ページ群
│   ├── nodes/       # ノード管理ページ群
│   ├── networks/    # ネットワーク管理ページ群
│   ├── storages/    # ストレージ管理ページ群
│   ├── images/      # イメージ管理ページ群
│   ├── projects/    # プロジェクト管理ページ群
│   ├── flavors/     # フレーバー管理ページ群
│   ├── users/       # ユーザー管理ページ群
│   └── tasks/       # タスク管理ページ群
├── layouts/         # レイアウト
│   ├── default.vue  # メインレイアウト（サイドバー + ヘッダー）
│   └── login.vue    # ログインレイアウト
├── components/      # 共通コンポーネント
│   ├── MainAppbar.vue    # ヘッダーバー
│   ├── MainSidebar.vue   # サイドバー
│   ├── PaginationBar.vue # ページネーション
│   ├── TaskTable.vue     # タスクテーブル
│   ├── ExpoterEditor.vue # エクスポーター設定
│   ├── MetricChart.vue   # メトリクスチャート
│   └── ...
├── stores/          # Pinia ストア
│   ├── auth.ts      # 認証ストア
│   ├── sidebar.ts   # サイドバー状態
│   └── tasks.ts     # タスクストア
├── composables/     # コンポーザブル
│   ├── api.ts       # APIクライアント（openapi-fetch）
│   └── reload.ts    # リロード制御
├── plugins/         # Vueプラグイン
│   ├── vuetify.ts   # Vuetify設定
│   ├── router.ts    # ルーター設定
│   └── pinia.ts     # Pinia設定
└── api/             # 自動生成API型定義
    └── openapi.d.ts # OpenAPIから生成された型
```

### 主要パターン

- **ファイルベースルーティング**: `unplugin-vue-router` によりpagesディレクトリ構造がそのままルートに
- **レイアウトシステム**: `vite-plugin-vue-layouts-next` でdefault/loginレイアウト切替
- **型安全APIクライアント**: `openapi-fetch` + 自動生成型による完全型安全なAPI呼び出し
- **Auto Import**: Vue/Pinia/ストア/コンポーザブルの自動インポート
- **Vuetify3**: マテリアルデザインUIコンポーネント

## デプロイ

### Docker Compose構成

| サービス | 説明 | ポート |
|---------|------|-------|
| api | FastAPI + uvicorn | 7799 |
| worker | タスクワーカー | - |
| web | Vue3 (nginx) | 3000 |
| proxy | リバースプロキシ (nginx) | 443 |
| db | PostgreSQL 16 | 5432 |

### 開発スクリプト（dev.sh）

```bash
# APIコンテナ起動 → openapi.json取得 → TypeScript型生成
docker compose -f compose.dev.yml up -d --build api
curl http://localhost:7799/openapi.json -o api/openapi.json
cd vue && pnpm exec openapi-typescript ../api/openapi.json -o ./src/api/openapi.d.ts
```
