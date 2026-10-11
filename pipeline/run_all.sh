#!/bin/bash
# Usage: ./run_all.sh /path/to/mri.pdf   (outputs go in ./build)
set -e
PDF="$(cd "$(dirname "${1:-mri.pdf}")" && pwd)/$(basename "${1:-mri.pdf}")"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HERE/build" && cd "$HERE/build"
cp "$HERE/viewer_template.html" .
python3 "$HERE/1_extract_pdf.py" "$PDF"
python3 "$HERE/2_build_sagittal.py"
python3 "$HERE/3_segment_sagittal.py"
python3 "$HERE/4_build_page1.py"
python3 "$HERE/5_register.py" cor
python3 "$HERE/5_register.py" ax
python3 "$HERE/6_segment_cor_ax.py"
python3 "$HERE/7_fuse.py"
python3 "$HERE/8_build_html.py"
cp "$HERE/site_template.html" . && python3 "$HERE/9_build_site.py" site && python3 "$HERE/10_build_single.py" site single
echo "Done -> $HERE/build/knee_3d.html and $HERE/build/site/"
