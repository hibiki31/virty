FROM python:3.8-buster

RUN apt update -y
RUN apt install -y \
    make gcc wget openssh-client openssh-server genisoimage rsync \
    libvirt-clients libvirt-dev

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

RUN mkdir -p /opt/virty/app
COPY . /opt/virty/app
WORKDIR /opt/virty/app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]