#!/usr/bin/env bash

set -Eeuo pipefail

root="${1:?workspace rootを指定してください}"
canonical_root="$(realpath -e -- "${root}")"
digest="$(printf '%s' "${canonical_root}" | sha256sum)"
digest="${digest%% *}"
printf 'virty-%s\n' "${digest:0:12}"
