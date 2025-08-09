#!/bin/bash -euo pipefail -c
set -euo pipefail

export REMOTE_USER="fespinoza"
export REMOTE_HOST="faraday.utem.cl"
export REMOTE_DIR="/home/amoya/Data_forTap/selected_Genomes"

chmod +x scripts/download_by_species.sh
echo "🔧 Descargando especie: \"Klebsiella aerogenes\" → base: genomes"
scripts/download_by_species.sh "Klebsiella aerogenes" "genomes"
