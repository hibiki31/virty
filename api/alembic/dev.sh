#!/bin/bash

alembic downgrade base && \
rm -rf alembic/versions/* && \
alembic revision --autogenerate && \
alembic upgrade head