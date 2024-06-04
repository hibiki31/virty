#/bin/bash

set -eu

alembic downgrade base
alembic upgrade head