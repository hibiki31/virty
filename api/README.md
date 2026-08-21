# Virty API development

APIの開発環境、型check、test、migration、OpenAPI生成は
[`docs/development.md`](../docs/development.md)を正本とする。

hostへPythonやpytestを導入せず、repository rootから次を使う。

```bash
./devctl quick api
./devctl verify api
```

SSH、Ansible、実libvirt nodeを使う`external` testは標準検証に含まれない。専用lab以外では実行しない。
