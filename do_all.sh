#!/bin/bash

set -Eeuo pipefail

script_path=$(readlink -f "$0")
script_dir=$(dirname "${script_path}")
root_dir="${script_dir}"
cd "${script_dir}"

function die() {
    echo
    echo "$@" >&2
    exit 1
}

"${script_dir}/validate.sh" || die "Validation failed, aborting..."

echo
echo "All steps completed successfully."
