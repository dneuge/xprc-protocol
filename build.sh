#!/bin/bash

set -Eeuo pipefail

script_path=$(readlink -f "$0")
script_dir=$(dirname "${script_path}")
root_dir="${script_dir}"
cd "${script_dir}"

src_dir="${script_dir}/src"
target_dir="${script_dir}/target"

document_xml="${src_dir}/document.xml"

html_target_dir="${target_dir}/html"
html_target="${html_target_dir}/index.html"
html_tool_dir="${script_dir}/tools/htmldocs"
html_template_dir="${html_tool_dir}/template"
html_template_less="${html_template_dir}/main.less"
html_template_css="${html_template_dir}/main.css"
html_template="${html_template_dir}/template.html"
mkhtml="${html_tool_dir}/mkhtml.sh"

function die() {
    echo "$@" >&2
    exit 1
}


echo "=== Preparing target directory ==="
if [[ -d "${target_dir}" ]]; then
    rm -Rf "${target_dir}" || die "Failed to delete target directory ${target_dir}"
fi
mkdir "${target_dir}" || die "Failed to create target directory ${target_dir}"

echo
echo "=== Preparing HTML template ==="
lessc "${html_template_less}" "${html_template_css}" || die "Failed to compile CSS via LESS"

echo
echo "=== Building HTML documentation ==="
mkdir "${target_dir}/html" || die "Failed to create target directory ${target_dir}"
"${mkhtml}" --src "${document_xml}" --out "${html_target}" --template "${html_template}" $@ || die "Failed to build HTML documentation"

echo
echo "Done."
