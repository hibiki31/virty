#!/bin/bash

# Passの時もログを表示
# pytest -v --capture=no

# 遅いテストを確認
# pytest -v --duration=N

# 前回Faileしたテストから実施
# pytest -v --ff

# pytest -v --cov=module ;  printf '\a'
pytest -v -x ;  printf '\a'