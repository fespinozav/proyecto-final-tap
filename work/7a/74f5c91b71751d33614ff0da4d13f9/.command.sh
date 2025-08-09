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

# Fuerza modo no-interactivo para cualquier 'ssh' interno del script creando un wrapper en PATH
mkdir -p bin
cat > bin/ssh <<'EOS'
#!/usr/bin/env bash
exec ssh -o BatchMode=yes -o PasswordAuthentication=no -o PubkeyAuthentication=yes              -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes              -o ConnectTimeout=8 -o ServerAliveInterval=10 -o ServerAliveCountMax=2 -o LogLevel=ERROR "$@"
EOS
chmod +x bin/ssh
export PATH="/Users/felipeespinoza/Documents/GitHub/proyecto-final-tap/bin:/opt/homebrew/opt/openjdk@17/bin:/Users/felipeespinoza/.pyenv/shims:/Users/felipeespinoza/.pyenv/bin:/opt/homebrew/opt/tcl-tk/bin:/Library/Frameworks/Python.framework/Versions/3.10/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/Library/Frameworks/Python.framework/Versions/3.11/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/opt/X11/bin:/usr/local/share/dotnet:~/.dotnet/tools:/opt/homebrew/opt/openjdk@17/bin:/Users/felipeespinoza/.pyenv/bin:/opt/homebrew/opt/tcl-tk/bin:/opt/miniconda3/bin:/opt/miniconda3/condabin:/Library/Frameworks/Python.framework/Versions/3.10/bin:/Users/felipeespinoza/.vscode/extensions/ms-python.debugpy-2025.10.0-darwin-arm64/bundled/scripts/noConfigScripts:/Users/felipeespinoza/Library/Application Support/Code/User/globalStorage/github.copilot-chat/debugCommand"
export RSYNC_RSH="ssh"

# Exporta variables de entorno para que ssh/rsync sean no-interactivos dentro del script
export REMOTE_USER="fespinoza"
export REMOTE_HOST="faraday.utem.cl"
export REMOTE_DIR="/home/amoya/Data_forTap/selected_Genomes"

echo "🔧 Descargando especie: "Klebsiella aerogenes" → base: genomes"
scripts/download_by_species.sh --debug "Klebsiella aerogenes" "genomes"
