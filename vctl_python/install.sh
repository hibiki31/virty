#!/bin/bash

sudo ln -f main.py /usr/local/bin/virty
virty --show-completion | sudo tee /etc/bash_completion.d/virty
source /etc/bash_completion.d/virty