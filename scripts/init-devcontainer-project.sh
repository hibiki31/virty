#!/usr/bin/env bash

set -Eeuo pipefail

workspace="${1:?local workspace folderを指定してください}"
repo_root="$(git -C "${workspace}" rev-parse --show-toplevel)"
project="$("${repo_root}/scripts/project-name.sh" "${repo_root}")-dev"
# Dev Containers/Composeは最初のCompose fileがあるproject directoryの.envを読む。
env_file="${repo_root}/.env"
temp_file="$(mktemp "${env_file}.XXXXXX")"
trap 'rm -f -- "${temp_file}"' EXIT

if [[ -f "${env_file}" ]]; then
  awk '!/^(COMPOSE_PROJECT_NAME|VIRTY_HOST_UID|VIRTY_HOST_GID)=/' \
    "${env_file}" >"${temp_file}"
fi

{
  printf 'COMPOSE_PROJECT_NAME=%s\n' "${project}"
  printf 'VIRTY_HOST_UID=%s\n' "$(id -u)"
  printf 'VIRTY_HOST_GID=%s\n' "$(id -g)"
} >>"${temp_file}"

chmod 0600 "${temp_file}"
mv -- "${temp_file}" "${env_file}"
trap - EXIT
