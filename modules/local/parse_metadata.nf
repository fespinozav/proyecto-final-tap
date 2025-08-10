process PARSE_METADATA {
  label 'small'
  tag { sp }
  publishDir ( params.outdir ?: "${projectDir}/outputs" ), mode: 'copy', overwrite: true
  input:
  val sp


  output:
  path 'samples*.tsv', emit: samples, optional: true
  path 'labels*.tsv',  emit: labels, optional: true

script:
  """
set -euo pipefail

cd "\$(dirname "\$0")"

echo "[NF] species: ${sp}"
echo "[NF] PWD: \$(pwd)"
echo "[NF] projectDir: ${projectDir}"

OUTDIR="\$(pwd)" "${projectDir}/scripts/parse_metadata.sh" "${sp}"

ls -lh
  """
}