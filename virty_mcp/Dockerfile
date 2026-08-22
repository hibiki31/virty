# syntax=docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e

FROM python:3.12-slim-bookworm@sha256:d50fb7611f86d04a3b0471b46d7557818d88983fc3136726336b2a4c657aa30b AS development

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/workspace/virty/virty_mcp/src:/workspace/virty

COPY virty_mcp/requirements.lock /tmp/requirements.lock
RUN python -m pip install --no-cache-dir --no-deps -r /tmp/requirements.lock \
    && python -m pip check

WORKDIR /workspace/virty
COPY api ./api
COPY virty_mcp ./virty_mcp
WORKDIR /workspace/virty/virty_mcp

CMD ["bash", "-lc", "ruff check . && pytest"]


FROM development AS check

RUN --network=none ruff check . && pytest
CMD ["true"]
