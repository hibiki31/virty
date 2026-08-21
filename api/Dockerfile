FROM python:3.12-bullseye@sha256:7cc929040c5e8cf6036c5099d62a83708427c131fb7a7c965b5ba51e995eea1c AS runtime-base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PROMETHEUS_MULTIPROC_DIR=/opt/data/metrics \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p /opt/data/metrics \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        genisoimage \
        libvirt-clients \
        libvirt-dev \
        make \
        openssh-client \
        openssh-server \
        rsync \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.lock /tmp/
RUN python -m pip install --no-cache-dir --no-deps -r /tmp/requirements.lock \
    && python -m pip check


FROM runtime-base AS development

COPY requirements-dev.txt requirements-dev.lock /tmp/
RUN python -m pip install --no-cache-dir --no-deps -r /tmp/requirements-dev.lock \
    && python -m pip check \
    && groupadd --gid 1000 virty \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash virty \
    && mkdir -p /cache /generated /home/virty/.ssh /tmp/virty-home/.ssh /workspace/api/data \
    && chown -R virty:virty /cache /home/virty /opt/data /workspace/api \
    && chown virty:virty /generated \
    && chmod 0777 /home/virty/.ssh /tmp/virty-home /tmp/virty-home/.ssh \
        /workspace/api/data

ENV HOME=/home/virty
WORKDIR /workspace/api
USER virty
CMD ["sleep", "infinity"]


FROM development AS check

COPY --chown=virty:virty . /workspace/api
CMD ["bash", "-lc", "ruff check . && mypy && pytest"]


FROM runtime-base AS production

WORKDIR /opt/app
COPY . .

EXPOSE 8000

CMD ["bash", "-lc", "mkdir -p /opt/data/metrics && alembic upgrade head && exec uvicorn main:app --host 0.0.0.0 --port 8000"]
