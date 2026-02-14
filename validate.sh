#!/bin/bash

set -Eeuo pipefail

script_path=$(readlink -f "$0")
script_dir=$(dirname "${script_path}")
root_dir="${script_dir}"
cd "${script_dir}"

src_dir="${script_dir}/src"

document_xsd_path='document.xsd'
document_xml_file='document.xml'

command_xsd_path="${src_dir}/command.xsd"
command_root_dir="${src_dir}/commands/"

function die() {
    echo "$@" >&2
    exit 1
}

_failed=()
function failed() {
    echo "$1 failed to validate" >&2
    _failed+=("$1")
}

echo "=== Validating document structure ==="
xmllint --noout --schema "${src_dir}/${document_xsd_path}" "${src_dir}/${document_xml_file}" || failed "document structure ${document_xml_file}"

echo
echo "=== Validating command descriptions ==="
IFS=$'\n'
for command_file_path in $(find "${command_root_dir}" -type f -iname '*.xml'); do
    command_file="$(realpath --relative-to="${command_root_dir}" "${command_file_path}")"
    echo "== Validating ${command_file} =="
    xmllint --noout --schema "${command_xsd_path}" "${command_file_path}" || failed "command description ${command_file}"
    echo
done

echo
if [[ ${#_failed[@]} -eq 0 ]]; then
    echo "No validation errors found."
else
    echo "Validation errors found in:" >&2
    for msg in ${_failed[@]}; do
        echo " - $msg" >&2
    done
    exit 1
fi
