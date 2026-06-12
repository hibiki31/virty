# Progress - タスク詳細アーカイブ

## 2025-07-18: release-5.2.0ブランチ開発

### 未使用importの削除
- 各コンポーネントから`useReloadListener`の未使用importを削除
- コミット: 6f24649a

### ユーザー公開鍵管理機能追加
- ユーザーモデルに公開鍵フィールド追加
- スキーマ・ルーター更新
- Alembicマイグレーション追加: `20250718_131034_04543573864a_added_users_publickey.py`

### ネットワーク isolated モード修正
- ブリッジ名バリデーション修正
- ポートグループレンダリング修正

### Prometheusメトリクス/エクスポーター機能 (#7)
- `exporter/router.py` 追加
- Metricクラス、ExpoterEditor実装
- メトリクスエンドポイント追加

## 2025-06-22〜2025-06-27: v5.1.2 開発

### ISOイメージwget/ダウンロード機能 (#49)
- imagesモジュールにダウンロード機能追加
- ログ強化

### JSONログサポート
- `LOG_MODE`環境変数導入
- `mixin/log.py` でJSON/テキスト切り替え

### MkDocsドキュメント整備
- 日本語対応
- OVS VLAN, Tailscale, FRRouting等のドキュメント追加

## 2025-05-14〜2025-05-17: v5.0.0〜v5.1.0 大規模リファクタリング

### Vue Composition API移行・Vuetify3対応
- Options API → Composition API (`<script setup>`)
- Vuetify3へのアップグレード
- ファイルベースルーティング導入（unplugin-vue-router）
- レイアウトシステム導入（vite-plugin-vue-layouts-next）

### OpenAPI型生成パイプライン構築
- `dev.sh` でAPI起動→openapi.json取得→型生成の自動化
- `openapi-fetch` + `openapi-typescript` 導入

### 認証システム刷新
- JWT認証（cookie保存）
- bcryptパスワードハッシュ
- ロールベースアクセス制御

## 初期化時点の備考
- 現在のブランチ: `release-5.2.0`
- APIバージョン: 5.1.2
- フロントエンドバージョン: 5.1.2
- 最終コミット日: 2025-07-18
