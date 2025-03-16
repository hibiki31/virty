FROM ubuntu:24.04

ENV PATH $PATH:/root/.local/bin/:/opt/venv/bin/

RUN apt-get update -y
RUN apt-get install -y \
    make \
    gcc \
    openssh-client \
    openssh-server \
    genisoimage \
    rsync \
    libvirt-clients \
    libvirt-dev \
    python3 \
    python3-dev \
    python3-venv

COPY ./requirements.txt /tmp/
RUN python3 -m venv /opt/venv
RUN pip3 install -r /tmp/requirements.txt

COPY . /opt/app
WORKDIR /opt/app

EXPOSE 8000

CMD bash -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"