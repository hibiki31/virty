
## install

開発（editable）モードでのインストール（自動更新）

```
pip install -e .
pip uninstall virty
```

```bash
docker run --rm \
  -v ${PWD}:/local openapitools/openapi-generator-cli generate \
  -i https://virty-pr.hinagiku.me/api/openapi.json \
  -g python \
  --package-name virty_client \
  -o /local/openapi/python

sudo chown -R ${USER}:${USER} ${PWD}/openapi
pip install -e ${PWD}/openapi/python/
pip install ${PWD}/openapi/python/
```