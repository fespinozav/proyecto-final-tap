process PARSE_METADATA {
  tag { sp }
  publishDir "${projectDir}/outputs", mode: 'copy', overwrite: true

  input:
  val sp


  output:
  path 'samples*.tsv', optional: false
  path 'labels*.tsv',  optional: false

script:
"""
set -euo pipefail

echo "[NF] start \$(date)"
echo "[NF] PWD: \$(pwd)"
echo "[NF] species: ${sp}"
echo "[NF] projectDir: ${projectDir}"

# nos aseguramos que el wrapper sea ejecutable
chmod +x "${projectDir}/scripts/parse_metadata.sh"

echo "[NF] genomes exists? -> ${projectDir}/genomes"
ls -ld "${projectDir}/genomes" || true

# Ejecuta el wrapper y **escribe en el workdir**
OUTDIR="\$PWD" "${projectDir}/scripts/parse_metadata.sh" "${sp}"

echo "[NF] generated in CWD:"
ls -lh || true
"""
}