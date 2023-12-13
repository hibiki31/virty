#!/bin/bash

SEND_HOST="
"

for line in $SEND_HOST
do  
    echo "++++++++++++  "$line"  +++++++++++++++"
    ssh $line 'sudo systemctl disable --now virty-agent.service'
    scp ./main $line:
    ssh $line 'sudo mkdir -pv /opt/virty'
    ssh $line 'sudo mv ./main /opt/virty/agent'

    scp ./virty-agent.service $line:
    ssh $line 'sudo mv ./virty-agent.service /lib/systemd/system/'
    ssh $line 'sudo systemctl daemon-reload'
    ssh $line 'sudo systemctl enable --now virty-agent.service'
    ssh $line 'sudo systemctl restart virty-agent.service'
done 