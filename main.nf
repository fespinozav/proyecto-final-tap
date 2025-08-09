nextflow.enable.dsl=2

// ---------------- Params ----------------
def speciesParam     = params.get('species')          // --species "Klebsiella aerogenes"
def speciesFileParam = params.get('species_file')     // --species_file ruta.txt
params.genomes_dir   = 'genomes'
params.outdir        = 'outputs/metadata'

// ---------------- Canales ----------------
def species_ch = speciesFileParam ?
    Channel
      .fromPath(speciesFileParam)
      .splitText()
      .map{ it?.trim() }
      .filter{ it }
      .unique()
  :
    Channel.of(speciesParam)

def parse_script_ch = Channel.fromPath('scripts/parse_metadata.py')

// ---------------- Proceso ----------------
process PARSE_METADATA {
  tag { sp }
  publishDir params.outdir, mode: 'copy', overwrite: true

  input:
  val  sp
  path parse_py

  output:
  path 'samples.tsv', optional: true
  path 'labels.tsv',  optional: true
  path 'metadata*.tsv', optional: true

  """
  set -euo pipefail
  set -x

  echo "[NF] start PARSE sp='${sp}'"
  echo "[NF] pwd=\$(pwd)"
  echo "[NF] python=\$(command -v python3 || true)"; python3 -V || true
  echo "[NF] ls staged:"; ls -lah || true

  # Comprobación de staging del script
  if [[ ! -s "${parse_py}" ]]; then
    echo "[NF][ERR] parse_py no stageado: ${parse_py}"; exit 2
  fi

  # Ejecuta con salida en vivo y timeout de seguridad (ajusta 5m si necesitas)
  mkdir -p .nf_logs
  set +e
  timeout 5m stdbuf -oL -eL python3 "${parse_py}" --species "${sp}" \
    2> >(tee -a .nf_logs/parse.err >&2) | tee -a .nf_logs/parse.out
  rc=\${PIPESTATUS[0]}
  set -e
  echo "[NF] python rc=\$rc"
  ls -lah || true
  exit "\$rc"
  """
}

// ---------------- Workflow ----------------
workflow {
  main:
    PARSE_METADATA( species_ch, parse_script_ch )
}