FROM python:3.10-buster

RUN apt update -y && apt install -y \
    make gcc wget openssh-client openssh-server \
    genisoimage rsync \
    libvirt-clients libvirt-dev

COPY ./requirements.txt /tmp/
RUN /usr/local/bin/python -m pip install --upgrade pip && pip3 install -r /tmp/requirements.txt

RUN mkdir -p /opt/app && mkdir -p /opt/data
COPY . /opt/app
WORKDIR /opt/app

EXPOSE 8000

CMD bash -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"