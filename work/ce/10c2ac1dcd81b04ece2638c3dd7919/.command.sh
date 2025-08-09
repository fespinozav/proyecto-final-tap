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
cp "${dl_script}" scripts/download_by_species.sh
cp "${acc_py}"    scripts/get_accessions.py
cp "${supp_csv}"  ./Supplememtary_Table_1.csv
chmod +x scripts/download_by_species.sh

# Fuerza modo no-interactivo para cualquier 'ssh' interno del script creando un wrapper en PATH
mkdir -p bin
cat > bin/ssh <<'EOS'
#!/usr/bin/env bash
exec ssh -o BatchMode=yes -o PasswordAuthentication=no -o PubkeyAuthentication=yes              -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes              -o ConnectTimeout=8 -o ServerAliveInterval=10 -o ServerAliveCountMax=2 -o LogLevel=ERROR "$@"
EOS
chmod +x bin/ssh
export PATH="$PWD/bin:$PATH"
export RSYNC_RSH="ssh"

# Exporta variables de entorno para que ssh/rsync sean no-interactivos dentro del script
export REMOTE_USER="fespinoza"
export REMOTE_HOST="faraday.utem.cl"
export REMOTE_DIR="/home/amoya/Data_forTap/selected_Genomes"

echo "🔧 Descargando especie: "Klebsiella aerogenes" → base: genomes"
# Lanza la descarga en segundo plano
scripts/download_by_species.sh --debug "Klebsiella aerogenes" "genomes" &
pid=$!

# Monitoreo de cantidad de archivos cada 10 segundos
(
  while kill -0 "$pid" 2>/dev/null; do
    count=$(find "genomes" -type f | wc -l)
    echo "📦 Archivos descargados hasta ahora: $count"
    sleep 10
  done
) &

wait $pid
