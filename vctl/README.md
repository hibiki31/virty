

## Openapi generator cli

```
docker run --rm \
  -v ${PWD}:/local openapitools/openapi-generator-cli generate \
  -i https://virty-pr.hinagiku.me/api/openapi.json \
  -g go \
  --package-name openapi \
  -o /local/virty-go \
  --git-repo-id virty-go --git-user-id hibiki31

sudo chown -R akane:akane openapi/
```



```
./install.sh && source /etc/bash_completion.d/virty
```

```
export PYTHONPATH="/home/akane/virty/vctl:$PYTHONPATH"
```

```
sudo chmod 755 ./main.bin
sudo cp ./main.bin /usr/local/bin/virty
virty --install-completion bash
```
echo "source <(vctl completion bash)" >> ~/.zshrc
