## 開発

開発時はWSL環境に直接pipでパッケージをインストールして開発を行う

```
sudo pip3 install -e ../pylib
sudo pip3 install -r ./requirements.txt
export PYTHONPATH="/home/akane/virty/vctl:$PYTHONPATH"
```

コマンドの設置と補完のインストール

```
./install.sh && source /etc/bash_completion.d/virty
```

テスト

```
virty auth
```

時々ライブラリを更新しよう（../pylib/README.md）

## ビルド

ビルド

```
./build.sh
```

スクリプト実行

```
./install_command.sh
```