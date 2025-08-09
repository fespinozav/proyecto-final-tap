#!/bin/bash -euo pipefail -c
set -euo pipefail

# Opciones SSH NO interactivas y con timeout (para evitar bloqueos sin TTY)
SSH_OPTS="-o BatchMode=yes -o PasswordAuthentication=no -o PubkeyAuthentication=yes \
          -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes \
          -o ConnectTimeout=8 -o ServerAliveInterval=10 -o ServerAliveCountMax=2 -o LogLevel=ERROR"

# Preflight SSH (falla rápido con mensaje claro si no hay auth no-interactiva)
if ! ssh ${SSH_OPTS} "fespinoza@faraday.utem.cl" true 2>/dev/null; then
  echo "🔒 Sin acceso SSH no-interactivo a fespinoza@faraday.utem.cl."
  echo "   Carga tu llave antes de correr Nextflow:"
  echo "     eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519"
  exit 1
fi

# Verifica que los artefactos stageados EXISTEN (para evitar 'No such file or directory')
if [[ ! -s "download_by_species.sh" ]]; then
  echo "❌ Falta scripts/download_by_species.sh (no fue stageado al workdir)"; exit 2
fi
if [[ ! -s "get_accessions.py" ]]; then
  echo "❌ Falta scripts/get_accessions.py (no fue stageado al workdir)"; exit 2
fi
if [[ ! -s "Supplememtary_Table_1.csv" ]]; then
  echo "❌ Falta Supplememtary_Table_1.csv (no fue stageado al workdir)"; exit 2
fi

# Prepara el layout esperado por tu script (carpeta scripts/ y CSV en CWD)
mkdir -p scripts
cp "download_by_species.sh" scripts/download_by_species.sh
cp "get_accessions.py"    scripts/get_accessions.py
cp "Supplememtary_Table_1.csv"  ./Supplememtary_Table_1.csv
chmod +x scripts/download_by_species.sh

# Exporta variables de entorno para que ssh/rsync sean no-interactivos dentro del script
export REMOTE_USER="fespinoza"
export REMOTE_HOST="faraday.utem.cl"
export REMOTE_DIR="/home/amoya/Data_forTap/selected_Genomes"
export SSH_OPTS="${SSH_OPTS}"
export RSYNC_RSH="ssh ${SSH_OPTS}"

echo "🔧 Descargando especie: "Klebsiella aerogenes" → base: genomes"
scripts/download_by_species.sh "Klebsiella aerogenes" "genomes"
