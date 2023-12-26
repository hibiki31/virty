FROM ubuntu:20.04

RUN sed -i.bak -e "s%http://archive.ubuntu.com/ubuntu/%http://ftp.riken.go.jp/Linux/ubuntu/%g" /etc/apt/sources.list

RUN apt-get update -y && apt-get install -y \
    python3 python3-pip patchelf ccache

COPY ./requirements.txt /tmp/
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

RUN mkdir -p /opt/app && mkdir -p /opt/data

# COPY . /opt/app
WORKDIR /opt/app
