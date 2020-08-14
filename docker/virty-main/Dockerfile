FROM centos:8

RUN mkdir -p /root/virty/main
RUN mkdir -p /root/.ssh
RUN chmod 600 /root/.ssh

WORKDIR /root/virty/main

RUN dnf update -y
RUN dnf upgrade -y
RUN dnf clean packages
RUN dnf install -y python36
RUN dnf install -y python3-libs
RUN dnf install -y python36-devel
RUN dnf install -y python3-pip
RUN dnf install -y make 
RUN dnf install -y gcc
RUN dnf install -y wget
RUN dnf install -y openssh-clients 
RUN dnf install -y openssh-server
RUN dnf install -y libvirt-client
RUN dnf install -y libvirt-devel 

RUN dnf clean all

COPY ./requirements.txt /tmp/

RUN python3.6 -m pip install --upgrade pip
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
RUN pip3 install flask-cors
RUN pip3 install flask_jwt_extended
RUN pip3 install pyhumps

RUN ln -si /root/virty/main/virty.py /usr/local/bin/virty

ENV VIRTY_SECRET="secret-key"
ENV VIRTY_PATH="/root/virty/main"
ENV PYTHONPATH="/root/virty/main"

# ENV http_proxy "http://IP:PORT/"
# ENV https_proxy "http://IP:PORT/"

EXPOSE 3031

CMD ["uwsgi","--ini","/root/virty/main/uwsgi.ini"]