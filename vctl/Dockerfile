# 古ければ互換性が高くなる
FROM ubuntu:18.04

RUN sed -i.bak -e "s%http://archive.ubuntu.com/ubuntu/%http://ftp.riken.go.jp/Linux/ubuntu/%g" /etc/apt/sources.list
RUN mkdir -p /opt/app && mkdir -p /opt/data
WORKDIR /opt/app

RUN apt-get update -y && apt-get install -y \
    python3 python3-pip patchelf ccache
RUN python3 -m pip install --upgrade pip


COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt