#!/bin/bash

go build
sudo cp vctl /usr/local/bin/
vctl completion bash |sudo tee /etc/bash_completion.d/vctl