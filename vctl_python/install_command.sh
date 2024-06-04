#!/bin/bash

sudo unlink /usr/local/bin/virty

sudo chmod 755 ./main.bin
sudo cp ./main.bin /usr/local/bin/virty
virty --show-completion | sudo tee /etc/bash_completion.d/virty