

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
