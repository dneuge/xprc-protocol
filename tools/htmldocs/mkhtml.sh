#!/bin/bash

set -Eeuo pipefail

script_path=$(readlink -f "$0")
script_dir=$(dirname "${script_path}")
cd "${script_dir}"

function die() {
	echo $@ >&2
	exit 1
}

if [[ ! -e .venv/pyvenv.cfg ]]; then
	echo 'Virtual environment does not exist yet, initializing...'
	mkdir -p "${script_dir}/.venv"
	(cd "${script_dir}/.venv" && python3 -m venv .) || die 'failed to create virtual environment'
fi

. "${script_dir}/.venv/bin/activate" || die 'failed to activate virtual environment'

# update dependencies if necessary
requirements_md5="$(md5sum "${script_dir}/requirements.txt")"
requirements_md5_file="${script_dir}/.venv/.last_installed_reqs"
if [[ ! -e "${requirements_md5_file}" ]] || [[ "$(cat "${requirements_md5_file}")" != "${requirements_md5}" ]]; then
	echo 'Requirements changed, updating...'
	pip install -r "${script_dir}/requirements.txt" || die 'failed to install dependencies'
	echo

	echo "${requirements_md5}" >"${requirements_md5_file}"
fi

python3 "${script_dir}/mkhtml.py" $@
