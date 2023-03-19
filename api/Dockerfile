FROM ubuntu:22.04 AS build

RUN apt update -y && apt install -y \
    make gcc wget openssh-client openssh-server \
    genisoimage rsync \
    libvirt-clients libvirt-dev \
    python3 python3-pip

COPY ./requirements.txt /tmp/
RUN python3 -m pip install --upgrade pip
RUN pip3 install --user -r /tmp/requirements.txt

FROM ubuntu:22.04 AS runner

RUN apt-get update -y --no-install-recommends \
    && apt-get install -y \
        wget openssh-client openssh-server \
        genisoimage rsync \
        libvirt-clients libvirt-dev \
        python3 python3-pip \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /root/.local /root/.local

RUN mkdir -p /opt/app && mkdir -p /opt/data
COPY . /opt/app
WORKDIR /opt/app

ENV PATH $PATH:/root/.local/bin/

EXPOSE 8000

CMD bash -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"