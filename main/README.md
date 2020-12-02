## CODE
### Que
0 sucsess
1 error
2 skip
3 running
4 init

### Domain
1 ON
5 OFF
7 node is maintenance mode
10 deleted domain
20 lost node



### Node
10 Up
20 Maintenance
30 Down
40 Error
50 Lost

## 概念メモ



## Git運用メモ
ローカルDevelopでこまめにコミット、スカッシュして正式なメッセージをつける。

```
Fix バグ修正
Add 機能追加
Change バグではないコードの修正
Update 動作に関係ない修正やドキュメントの修正、masterマージ前の変更履歴など
Remove 不要なコードの削除
Revert 変更取り消し
Move ファイルの移動
```

マージするときは以下の規則で行う。

```
Merge branch 'develop' v1.0.0
```

changes.mdは以下のコマンドで該当コミットを記録する？意味あるか？

```
git log --date=short --no-merges --pretty=format:"%cd %s %h (@%cn) "
```