FROM python:3.11-bullseye

WORKDIR /opt/app
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
    libvirt-dev

COPY ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY . .

EXPOSE 8000

CMD bash -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"