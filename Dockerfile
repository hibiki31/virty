FROM centos:6.8

ENV container docker

ADD ./docker/conf/nginx.repo /etc/yum.repos.d/

RUN yum localinstall -y http://rpms.famillecollet.com/enterprise/remi-release-6.rpm
RUN yum install -y https://centos6.iuscommunity.org/ius-release.rpm
RUN yum install -y nginx-1.10.1
RUN yum install -y make gcc openssh-clients
RUN yum install -y libxml2-devel
RUN yum install -y python35u python35u-libs python35u-devel python35u-pip
RUN yum install -y libvirt-client libvirt-devel libvirt libvirt-bin libvirt-python libxml2-python python-websockify

RUN  yum install -y libguestfs libvirt libvirt-client python-virtinst qemu-kvm virt-manager virt-top virt-viewer virt-who virt-install bridge-utils 

RUN yum clean all

RUN ln -s /usr/bin/python3.5 /usr/bin/python3
RUN unlink /usr/bin/python
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3.5 /usr/bin/pip

RUN pip install --upgrade pip
RUN pip install uwsgi flask

COPY ./docker/conf/nginx.conf /etc/nginx/nginx.conf
ADD ./docker/conf/default.conf /etc/nginx/conf.d/default.conf
RUN usermod -u 1000 nginx

EXPOSE 80

ADD ./docker/script/start.sh /tmp/start.sh

CMD /bin/bash /tmp/start.sh