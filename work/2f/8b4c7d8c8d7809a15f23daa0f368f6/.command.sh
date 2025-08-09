#!/bin/bash -euo pipefail -c
set -euo pipefail

# Opciones SSH no interactivas y con timeout
SSH_OPTS="-o BatchMode=yes -o PasswordAuthentication=no -o PubkeyAuthentication=yes               -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8               -o ServerAliveInterval=10 -o ServerAliveCountMax=2 -o LogLevel=ERROR"

# Preflight SSH (sin TTY, falla rápido si no hay auth)
if ! ssh ${SSH_OPTS} "fespinoza@faraday.utem.cl" true 2>/dev/null; then
  echo "🔒 Sin acceso SSH no-interactivo a fespinoza@faraday.utem.cl."
  echo "   Solución rápida:"
  echo "     1) eval "$(ssh-agent -s)""
  echo "     2) ssh-add ~/.ssh/id_ed25519"
  exit 1
fi

# Prepara layout esperado por el script
mkdir -p scripts
cp "download_by_species.sh" scripts/download_by_species.sh
cp "get_accessions.py"    scripts/get_accessions.py
cp "Supplememtary_Table_1.csv"  ./Supplememtary_Table_1.csv

export REMOTE_USER="fespinoza"
export REMOTE_HOST="faraday.utem.cl"
export REMOTE_DIR="/home/amoya/Data_forTap/selected_Genomes"
export SSH_OPTS="${SSH_OPTS}"
export RSYNC_RSH="ssh ${SSH_OPTS}"

chmod +x scripts/download_by_species.sh
echo "🔧 Descargando especie: "Klebsiella aerogenes" → base: genomes"
scripts/download_by_species.sh "Klebsiella aerogenes" "genomes"
