FROM centos:8

RUN dnf update -y && dnf upgrade -y && dnf clean packages
RUN dnf install -y python38 python38-libs python38-devel python38-pip make gcc wget openssh-clients openssh-server
RUN dnf install -y libvirt-client libvirt-devel libpq-devel

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

RUN mkdir -p /opt/virty/app
COPY . /opt/virty/app
WORKDIR /opt/virty/app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]