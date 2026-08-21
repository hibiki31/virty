# Virty 開発エージェントガイド

## 適用範囲と正本

- 本書はリポジトリ全体に適用する。同じdirectoryでは`AGENTS.override.md`を`AGENTS.md`より優先し、
  競合する場合は作業対象により近いdirectoryの指示を優先する。
- VirtyはVue 3・TypeScript・VuetifyのWeb UI、FastAPI・PostgreSQLのAPI、
  SSH・Ansible・libvirtで管理ノードを操作するLinux向け仮想化管理基盤である。
- 実装詳細の正本はコード、`compose.example.yml`、Dockerfile、依存manifest、
  OpenAPI、Alembic migrationとする。`docs/`は要件、設計意図、開発手順を扱う。
- 文書の読み分けと更新先は、最初に`docs/README.md`で確認する。

## 作業開始

1. `docs/README.md`を読み、タスクに必要な文書だけを参照する。
2. `git status --short --branch`でブランチと既存変更を確認し、利用者の変更を保持する。
3. Codex worktreeでは、編集前に既定ブランチ（現在は`master`）から
   `codex/task-name`の形式で作業ブランチを作る。detached HEADや既定ブランチでは編集しない。
4. 関係するコードと必要なGit履歴を確認する。古い文書だけから現行仕様を推測しない。
5. 要件や設計判断を変える場合は、実装前に該当する`docs/`へ方針を反映する。

## 実装規律

- 利用者の変更を上書きせず、依頼範囲に必要な最小の変更を行う。
- DBモデル変更にはAlembic migrationを追加し、upgradeとdowngradeをレビューする。
- API契約変更では、バックエンドschema、OpenAPI、`vue/src/api/openapi.d.ts`、
  利用側の型と実装を同じ変更で同期する。生成型を手編集しない。
- 非同期処理を追加した場合は、ルーターが作るtask keyと`api/*/tasks.py`のhandler、
  `api/worker.py`の登録が一致することを確認する。
- 新規・変更するPythonの関数と公開インターフェースには型ヒントを付ける。
- 新規・変更するコメント、運用者向けログ、Gitコミットメッセージは原則として日本語にする。
  外部仕様の固定文言や既存コードを、理由なく一括変換しない。
- バージョンはリリース対象の変更でのみ更新し、更新時は`api/settings.py`と
  `vue/package.json`の値を同時に確認する。
- 大きなHTML、OpenAPI、生成ファイルは全文を展開せず、`rg`、parser、対象範囲の抽出で調査する。
- 秘密鍵、token、password、`api/tests/env*.json`、DB dumpをコミットしない。

## 開発環境と検証

- 利用可能なコンテナ環境を優先する。Docker Composeを使う場合は
  `-p virty-task-name`の形式でproject名を分離し、他のworktreeのcontainer、network、volumeを共有しない。
- API開発用Composeは`api/.devcontainer/compose.yml`である。
  `compose.example.yml`は配布imageを使う実行例で、ソースbuild用Composeではない。
- ルートの`dev.sh`は旧デプロイ更新スクリプトであり、OpenAPI生成や開発テストには使わない。
- API変更では、API開発containerの`/workspaces/api`で先に`ruff check .`を実行し、必要な場合だけ変更対象へ
  `--fix`を適用する。完了前にもう一度`ruff check .`を実行する。
  関連pytestは隔離した統合テスト環境でだけ実行する。単なる確認のために`main.py`を直接起動しない。
- Web変更では`cd vue && pnpm run type-check && pnpm run build`を実行し、必要に応じてlintする。
  完了確認のためだけに開発serverを起動しない。
- API/worker/image/network/storageを扱うpytestは、DB内容の削除や管理ノード上のresource作成・削除を行う。
  本番・共有環境では実行しない。前提条件と安全な手順は`docs/development.md`を参照する。
- 文書だけの変更でも`git diff --check`と内部リンクの存在確認を行う。
- 影響範囲別の詳しい検証手順は`docs/development.md`を正本とする。

## 完了とGit

1. `git --no-pager diff`と`git status --short`で、意図した変更だけであることを確認する。
2. 意図したfileだけをstageし、`git diff --cached --check`と`git --no-pager diff --cached`で
   untrackedだった新規fileを含むcommit内容を確認する。
3. 影響範囲の検証を実行し、未実施項目と理由を明記する。
4. 変更した要件、設計、開発手順を同じ変更内で更新する。Git履歴を別の進捗文書へ複製しない。
5. 利用者がコミット保留を指示していない限り、理解可能な単位で必ずコミットする。
6. 既定ブランチへマージする直前に最新の既定ブランチを作業ブランチへ取り込み、
   競合では双方の意図を保持して解消し、影響範囲を再検証する。
