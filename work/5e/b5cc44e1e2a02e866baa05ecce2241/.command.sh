#!/bin/bash -euo pipefail -c
set -euo pipefail

# Preflight SSH: falla rápido si no hay auth no-interactiva
if ! ssh -o BatchMode=yes -o ConnectTimeout=8 "fespinoza@faraday.utem.cl" true 2>/dev/null; then
  echo "🔒 Sin acceso SSH no-interactivo a fespinoza@faraday.utem.cl."
  echo "   Ejecuta: eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519"
  exit 1
fi

export REMOTE_USER="fespinoza"
export REMOTE_HOST="faraday.utem.cl"
export REMOTE_DIR="/home/amoya/Data_forTap/selected_Genomes"

chmod +x scripts/download_by_species.sh
echo "🔧 Descargando especie: \"Klebsiella aerogenes\" → base: genomes"
scripts/download_by_species.sh "Klebsiella aerogenes" "genomes"
