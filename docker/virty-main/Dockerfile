FROM centos:8

RUN mkdir -p /root/virty/main
RUN mkdir -p /root/.ssh
RUN chmod 600 /root/.ssh
WORKDIR /root/virty/main

# ENV http_proxy "http://IP:PORT/"
# ENV https_proxy "http://IP:PORT/"

RUN dnf update -y
RUN dnf upgrade -y
RUN dnf install -y python36 python3-libs python36-devel python3-pip
RUN dnf install -y make gcc openssh-clients openssh-server
RUN dnf install -y libvirt-client libvirt-devel
RUN dnf clean all
RUN pip3 install --upgrade pip
RUN pip3 install flask Flask-JWT uwsgi libvirt-python jsonify ansible

RUN ln -si /root/virty/main/virty.py /usr/local/bin/virty

EXPOSE 3031

CMD ["uwsgi","--ini","/root/virty/main/uwsgi.ini"]