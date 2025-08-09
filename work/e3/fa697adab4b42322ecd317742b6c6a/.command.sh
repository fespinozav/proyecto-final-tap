#!/bin/bash -ue
set -euo pipefail
SPEC="Mycobacterium intracellulare"

python scripts/parse_metadata.py     --species "$SPEC"     --genomes_dir "genomas"     --output_dir .

safe_name="${SPEC// /_}"
mv samples.tsv "${safe_name}.samples.tsv"
mv labels.tsv  "${safe_name}.labels.tsv" || touch "${safe_name}.labels.tsv"
echo "Metadata for $SPEC parsed successfully."
echo "Output files: ${safe_name}.samples.tsv, ${safe_name}.labels.tsv
