FROM ubuntu:latest

ENV TZ=Asia/Tokyo

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    openjdk-17-jdk \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV HOME=/home/${UNAME}
ENV VOLTA_HOME=${HOME}/.volta
ENV PATH=${VOLTA_HOME}/bin:$PATH

RUN curl -sSL https://get.volta.sh | bash

RUN volta install node
RUN volta install yarn