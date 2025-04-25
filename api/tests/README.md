# Test

公開鍵の準備

```
cat ~/.ssh/id_ed25519 | sed ':a;N;$!ba;s/\n/\\n/g'
```