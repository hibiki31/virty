# Virty Web development

Webの開発環境、lint、型check、Vitest、生成型、production buildは
[`docs/development.md`](../docs/development.md)を正本とする。

hostへNode.jsやpnpmを導入せず、repository rootから次を使う。

```bash
./devctl quick web
./devctl verify web
```

OpenAPIまたはVite pluginの生成型を更新するときだけ、`./devctl generate openapi`または
`./devctl generate web-types`を明示的に実行する。
