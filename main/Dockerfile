FROM centos:8

RUN mkdir -p /opt/virty/app
RUN mkdir -p /opt/virty/data
WORKDIR /opt/virty/app

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
RUN dnf install -y libpq-devel

RUN dnf clean all

RUN python3.6 -m pip install --upgrade pip
RUN pip3 install --upgrade pip
RUN pip3 install Flask==1.1.1
RUN pip3 install Flask_Login==0.5.0
RUN pip3 install uwsgi==2.0.18
RUN pip3 install libvirt-python==6.1.0
RUN pip3 install jsonify==0.5
RUN pip3 install ansible==2.9.6
RUN pip3 install bcrypt==3.1.7
RUN pip3 install pings==0.0.1 
RUN pip3 install flask-cors
RUN pip3 install flask_jwt_extended
RUN pip3 install pyhumps
RUN pip3 install fastapi
RUN pip3 install sqlalchemy
RUN pip3 install uvicorn
RUN pip3 install psycopg2
RUN pip3 install databases
RUN pip3 install asyncpg
RUN pip3 install aiosqlite

COPY . /opt/virty/app

RUN ln -si /opt/virty/main/virty.py /usr/local/bin/virty

EXPOSE 3031

CMD ["uwsgi","--ini","/opt/virty/main/uwsgi.ini"]