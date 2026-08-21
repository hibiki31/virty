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
- 秘密鍵、token、password、`api/tests/env*.json`、external labの実config、DB dumpをコミットしない。

## 定型タスク: 実機試験情報の受け入れ

- 利用者が「試験用情報を提供します」と述べた場合、または専用lab設定の提供・作成を明確に申し出た場合は、
  実機testを開始せず、`api/tests/external/README.md`の「設定受け入れタスク」を実施する。
  この申し出は設定fileを準備する許可だけであり、`./devctl infra`の実行許可ではない。
- `api/tests/external/infra-config.example.json`を正本として、変更が必要な非機密値だけを項目別に質問する。
  password、秘密鍵、token、credential付きURLは質問しない。利用者が自発的に提示した場合も使用、復唱、
  設定fileへの転記をせず、露出済みのcredentialまたはkeyとして失効・rotationを依頼する。
  組織上秘匿したいhost名、IP address、usernameも手動置換を選べるようにする。
- 回答後はrepository rootの`.secrets/infra-config.json`をexampleから作成し、非機密値だけを反映する。
  既存fileを無断で読んだり上書きしたりせず、directoryを`0700`、fileを`0600`にする。
  秘密値は用途が分かるplaceholder、`allow_destructive`は`false`のままにする。
- 最後にplaceholderを安全なlocal editorで利用者自身が置換し、専用labと設定全体を確認してから
  `allow_destructive`を`true`へ変更するよう依頼する。秘密値を返信させず、置換後のfileを表示、diff、stage、commitしない。

## 開発環境と検証

- 開発、型check、test、image buildはrepository rootの`./devctl`だけを入口とし、hostのPython、Node、pnpmや
  raw Compose commandへ置き換えない。`devctl`がworktree固有のproject名とportを割り当てる。
- 編集中は変更対象へ`./devctl quick api`、`./devctl quick web`、または`./devctl quick mcp`を実行し、
  完了前は変更範囲にかかわらず
  引数なしの`./devctl verify`を実行する。各checkは非修正modeであり、自動修正は対象fileを限定する。
- API契約変更では`./devctl generate openapi`、Webのrouter/component/auto-import生成型変更では
  `./devctl generate web-types`を使い、生成型を手編集しない。
- `./devctl infra`は専用labの明示設定を必要とする破壊的な外部結合testである。利用者の明示許可なく実行せず、
  本番・共有DB・共有nodeを指定しない。標準`quick`と`verify`は実機resourceを変更しない。
- 完了確認だけを目的に開発serverを起動しない。詳細なcommand、timeout、test分類は`docs/development.md`を正本とする。
- 文書だけの変更でも`git diff --check`と内部リンクの存在確認を行う。

## 完了とGit

1. `git --no-pager diff`と`git status --short`で、意図した変更だけであることを確認する。
2. 意図したfileだけをstageし、`git diff --cached --check`と`git --no-pager diff --cached`で
   untrackedだった新規fileを含むcommit内容を確認する。
3. 影響範囲の検証を実行し、未実施項目と理由を明記する。
4. 変更した要件、設計、開発手順を同じ変更内で更新する。Git履歴を別の進捗文書へ複製しない。
5. 利用者がコミット保留を指示していない限り、理解可能な単位で必ずコミットする。
6. 既定ブランチへマージする直前に最新の既定ブランチを作業ブランチへ取り込み、
   競合では双方の意図を保持して解消し、影響範囲を再検証する。
7. 想定外の事象が発生していない限り、作業ブランチを`master`へ適切にマージして作業を完了する。
