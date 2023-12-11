#!/bin/bash

while true;
do 
    go build main.go
    sudo ./main &
    ECHO_PID=$!
    # echo $ECHO_PID

    sleep 3

    inotifywait -e modify -r ./

    sudo kill $ECHO_PID
done