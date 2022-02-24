### Ver 2.1.0
- 2022-02-24 Add oVSを利用したVLANネットワークに対応 0326bc2 (@hibiki131) 
- 2022-02-23 Update README.md f05af13 (@GitHub) 
- 2022-02-23 Update README.md 8d6ad70 (@GitHub)

### Ver 2.0.0
- 2022-02-22 Fix known_hostsのバグ 3436a82 (@hibiki131) 
- 2022-02-23 Add SSH鍵の登録 19216d4 (@hibiki131) 
- 2022-02-23 Fix docker build e87adaa (@hibiki31) 
- 2022-02-22 Add admin mode dc5cd66 (@hibiki131) 
- 2022-02-22 Fix ユーザ変更周りを修正 36bf365 (@hibiki131) 
- 2022-02-22 Fix タスク状況のポーリング処理追加 7ecddac (@hibiki131) 
- 2022-02-21 Fix タスク状況取得 0504531 (@hibiki131) 
- 2022-02-21 Add websoccketの仮対応とバックグラウンド処理の変更 42d8c84 (@hibiki131) 
- 2022-02-20 Add タスクに依存関係を追加 a4dfe99 (@hibiki131) 
- 2022-02-20 Fix taskの外部キー a9aa700 (@hibiki131) 
- 2022-02-20 Add scopeの雛形作成 6fafe5f (@hibiki31) 
- 2022-02-19 Add docker-compose 189d144 (@hibiki131) 
- 2022-02-18 Add alembic 977833f (@hibiki131) 

### Ver 1.6.1
- 2022-02-15 Fix パッケージの更新 1c16836 (@hibiki131) 
- 2022-02-15 Bump postcss from 7.0.35 to 7.0.39 in /web 04b0fe9 (@GitHub) 
- 2022-02-15 Bump node-sass from 5.0.0 to 7.0.0 in /web d6df9f1 (@GitHub) 
- 2022-02-15 Bump ansible from 2.9.6 to 4.2.0 in /main ccc2a13 (@GitHub) 
- 2022-02-15 Bump shelljs from 0.8.4 to 0.8.5 in /web 870cf38 (@GitHub) 
- 2022-02-15 Bump path-parse from 1.0.6 to 1.0.7 in /web 5869eac (@GitHub) 
- 2022-02-15 Bump tar from 6.1.0 to 6.1.11 in /web 3fb33d4 (@GitHub) 
- 2022-02-15 Bump ws from 6.2.1 to 6.2.2 in /web a434d7e (@GitHub) 
- 2022-02-15 Bump follow-redirects from 1.12.1 to 1.14.8 in /web 3eae7ef (@GitHub) 
- 2022-02-15 Bump url-parse from 1.4.7 to 1.5.6 in /web 20fd09a (@GitHub) 
- 2022-02-15 Bump color-string from 1.5.4 to 1.9.0 in /web eb2ce51 (@GitHub) 
- 2021-06-10 Bump fastapi from 0.61.1 to 0.65.2 in /main 5a8653f (@GitHub) 
- 2021-05-29 Bump dns-packet from 1.3.1 to 1.3.4 in /web da3d04c (@GitHub) 
- 2021-05-26 Bump browserslist from 4.16.1 to 4.16.6 in /web e01255a (@GitHub) 
- 2021-05-11 Bump lodash from 4.17.19 to 4.17.21 in /web 41cc736 (@GitHub) 
- 2021-05-11 Bump hosted-git-info from 2.8.8 to 2.8.9 in /web 133e923 (@GitHub) 
- 2021-04-30 Bump ssri from 6.0.1 to 6.0.2 in /web ff9ac90 (@GitHub) 
- 2021-03-26 Add cloud-initに仮対応 2ed40eb (@hibiki31) 
- 2021-03-25 Add ストレージのメタデータ変更可能 c6fa8aa (@hibiki31) 
- 2021-03-24 Add ストレージにメタデータを付与#9 ストレージモデルがメタデータを持ち、ロールを設定可能に これをもとにisoのリストが表示される bb27941 (@hibiki131) 
- 2021-03-24 Add cloud-init用イメージ作成機能 3fc946c (@hibiki131) 
- 2021-03-24 Fix VM削除が即時ではない#15 593a6f5 (@hibiki131) 
- 2021-03-24 Change Dockerイメージをpythonに 1bbb9c2 (@hibiki131) 
- 2021-03-24 Change Vue開発環境の変更 e232d65 (@hibiki131) 
- 2021-03-24 Change ストレージのメタデータを別テーブルに移行 3883d85 (@hibiki31) 
- 2021-03-16 Add ansible qemu-img 6f68ed2 (@hibiki31) 
- 2021-03-11 Bump elliptic from 6.5.3 to 6.5.4 in /web 1af67c3 (@GitHub) 
- 2021-01-31 Add VMのOVS対応 db47596 (@hibiki31) 
- 2021-01-31 Add OpenVSwitchネットワークの追加 f693c89 (@hibiki31) 
- 2021-01-24 Add Open vSwitchの設定方法 2a78fc3 (@hibiki31) 
- 2021-01-10 Change VM一覧のロード表示 5dc39b8 (@hibiki31) 
- 2021-01-10 Delete 旧モジュールの削除 2efb636 (@hibiki31) 
- 2021-01-10 Add Linux bridgeのネットワークを作成可能 709686c (@hibiki31) 
- 2021-01-10 Fix 旧モジュール依存の処理を書き直した 8fec0b2 (@hibiki31) 
- 2021-01-10 ネットワークAPI 73c5672 (@hibiki31) 
- 2021-01-09 Delete 旧モジュール群のインポート 6d058e6 (@hibiki31) 

### Ver 1.6.0
- 2021-01-09 Add 既存VMイメージからVMを作成可能 e81701e (@hibiki31) 
- 2021-01-09 Update highlight.js to a non-vulnerable version 64f2d4d (@hibiki31) 
- 2021-01-09 Update axios from 0.19.2 to 0.21.1 be82686 (@hibiki31) 
- 2021-01-09 Update README 5a25af3 (@hibiki31) 
- 2020-12-02 Add Ansibleのテストコード b2e9e1d (@hibiki31) 

### Ver 1.5.0
- 2020-11-23 Fix 表記ミスを修正 #8 (WEB) f2f4fb0 (@hibiki31) 
- 2020-11-23 Fix GlustorFSなどを利用した際のパースエラーを修正 93fb216 (@hibiki31) 
- 2020-11-22 Change update script 9d1bbfd (@hibiki31) 
- 2020-11-22 Add エラー内容をクリップボードへコピー (WEB) 6807db7 (@hibiki31) 
- 2020-11-20 Change ネットワーク名のユニーク制限を削除 dd92548 (@hibiki31) 
- 2020-11-20 Change プール名のユニーク制限を削除 5d66701 (@hibiki31) 
- 2020-11-20 Add ストレージの追加と削除 c8ec2e5 (@hibiki31) 

### Ver 1.4.0
- 2020-11-19 Change ロングポーリングで状態の取得 (WEB) 4276a56 (@hibiki31) 
- 2020-11-19 Add タスク状況のロングポーリング (API) 26ded34 (@hibiki31) 
- 2020-11-19 Add CDROMの変更 (API) 5904cf4 (@hibiki31) 
- 2020-11-19 Add VMの作成・削除・電源 (API) 9dd6e40 (@hibiki31) 
- 2020-11-18 Update version b3003fa (@hibiki31) 

### Ver 1.3.0
- 2020-11-18 Fix lint (WEB) e121771 (@hibiki31) 
- 2020-11-18 Add 各リソースの一覧ページ (WEB) 067d463 (@hibiki31) 
- 2020-11-18 Change レスポンスのスキーマ定義 (API) b5ea0f0 (@hibiki31) 
- 2020-11-18 Update VScode設定 383670f (@hibiki31) 
- 2020-11-18 Fix ログアウト時にリダイレクトされない (WEB) 9581e6e (@hibiki31) 
- 2020-11-18 Add ネットワーク関連のAPI e75b43f (@hibiki31) 
- 2020-11-17 Add グループ関連のAPI d4f37bf (@hibiki31) 
- 2020-11-16 Add VM詳細の取得API 6d753ee (@hibiki31) 
- 2020-11-16 Update README.md d98d8b0 (@hibiki31) 
- 2020-11-15 Fix LANG 9de316a (@hibiki31) 
- 2020-11-15 Change 開発環境の判定と、本番環境でのトークン自動生成 c5cc164 (@hibiki31) 
- 2020-11-15 Update version 240ceb7 (@hibiki31) 
- 2020-11-15 Add APIで実装されてる機能をUIに実装 4422999 (@hibiki31) 

### Ver 1.2.0
- 2020-11-15 Add APIで実装されてる機能をUIに実装 4422999 (@hibiki31) 

### Ver 1.1.0
- 2020-11-15 Change ワーカのエラー処理 04a2efb (@hibiki31) 
- 2020-11-15 Move xmlとplaybookのパスを変更 55135ad (@hibiki31) 
- 2020-11-15 Remove 不要なモジュールの整理 9a3c0c8 (@hibiki31) 
- 2020-11-15 Change タスク処理をワーカへ委任 1356e69 (@hibiki31) 
- 2020-11-13 Add タスク処理用のデコレータを作成 070d804 (@hibiki31) 

### Ver 1.0.0
- バックエンドをFastAPIに変更
- フロントエンドをVue+Vuetifyに変更

### Ver 0.4.0
- Dockerize Vue App
- Added front written in vue

### Ver 0.3.7
- Moving to an API and front composition

### Ver 0.3.6
- Design and template organization

### Ver 0.3.5
- View is now modularized

### Ver 0.3.4
- Change docker image name
- Modularization of flask
- Implemented a little API

### Ver 0.3.3
- Fix bug, ssh command permisson

### Ver 0.3.2
- Fix bug, when enlarging an image
- Get script path from env

### Ver 0.3.1
- fix bug when define by archive mode

### Ver 0.3.0
- select from three types when creating a virtual machine
- replace define function

### Ver 0.2.4
- Task status can be checked by long polling

### Ver 0.2.3
- Separation of set values
- Package optimization

### Ver 0.2.2
- Fix user and group function
- Process logs are taken individually

### Ver 0.2.1
- Fix path error
- Fix javascript active effect
- Unifying web design

### Ver 0.2.0
- Added user and group function
- URL structure changed

### Ver 0.1.0
- Beta version released