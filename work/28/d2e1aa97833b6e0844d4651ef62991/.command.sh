#!/bin/bash -ue
set -euo pipefail

python scripts/parse_metadata.py     --species "$species"     --genomes_dir "${genomes_dir}"     --output_dir .

mv samples.tsv "${species// /_}.samples.tsv"
mv labels.tsv  "${species// /_}.labels.tsv" || touch "${species// /_}.labels.tsv"
