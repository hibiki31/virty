
## install

開発（editable）モードでのインストール（自動更新）

```
pip install -e .
pip uninstall virty
```

## openapi-python-client

```
openapi-python-client generate --url https://virty-pr.hinagiku.me/api/openapi.json
```

## openapi-generator-cli

```bash
docker run --rm \
  -v ${PWD}:/local openapitools/openapi-generator-cli generate \
  -i https://virty-pr.hinagiku.me/api/openapi.json \
  -g python-pydantic-v1 \
  --package-name virty_client \
  -o /local/openapi/python

sudo chown -R ${USER}:${USER} ${PWD}/openapi
pip install -e ${PWD}/openapi/python/
pip install ${PWD}/openapi/python/
pip uninstall virty-client -y

python3 -X importtime test.py
```