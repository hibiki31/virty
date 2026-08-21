# 開発者向けドキュメント

`docs/`は、Virtyを変更する開発者とコーディングエージェント向けの内部文書である。
作業開始時はこの索引を読み、タスクに関係する文書だけを参照する。

## 文書の役割

| 文書 | 答える問い | 読む・更新するタイミング |
|---|---|---|
| [requirements.md](requirements.md) | 何を、誰のために提供するか | 機能、UI、利用者体験、対応範囲を変えるとき |
| [architecture.md](architecture.md) | なぜこの境界と処理方式なのか | componentの責務、data flow、外部連携を変えるとき |
| [development.md](development.md) | どの環境と手順で安全に変更・検証するか | build、test、migration、契約生成、release手順を変えるとき |

各文書は一つの主目的を持つ。要件に実装手順を混ぜず、開発手順に製品の将来構想を混ぜない。

## リポジトリ内文書との境界

| 場所 | 対象読者と役割 | 正本にする情報 |
|---|---|---|
| [`AGENTS.md`](../AGENTS.md) | Codex、Clineなどのコーディングエージェント | 短く強制可能な作業規律、安全規則、検証原則 |
| `docs/` | 開発者・エージェント | 要件、設計意図、開発・検証手順 |
| [`README.md`](../README.md) | 初めて訪れた利用者・開発者 | 製品概要、最短の導入、公開文書への入口 |
| `mkdocs/` | 導入・運用を行う利用者 | setup、運用how-to、利用例。内部作業規律は置かない |
| `/api/openapi.json` | API利用者・frontend | 実行中backendが生成するAPI契約 |
| code・manifest・migration | 実装者 | endpoint、型、DB列、依存version、runtime設定の詳細 |
| Git commit・tag | 保守者 | 変更履歴とrelease履歴 |

`activeContext`や`progress`のようなタスク日誌は置かない。現在の状態は`git status`、
過去の変更は`git log`と`git show`で確認し、文書には将来も有効な判断だけを残す。

## 更新ルール

- 仕様変更は`requirements.md`、構成や責務の変更は`architecture.md`、
  開発・検証方法の変更は`development.md`へ反映する。
- endpoint一覧、schema、DB列、依存packageの完全なversion表は複製せず、正本へ案内する。
- 現行機能、目標、未提供機能を明確に区別する。コードにない機能を提供済みと記載しない。
- 手順は、現在追跡されているscript、Compose、package scriptで再現できることを確認する。
- 古くなった説明は追記で打ち消さず、正しい内容へ置き換える。不要になった文書は削除する。
- 文書変更は関連する実装と同じコミットに含め、`git diff --check`とリンクを確認する。
