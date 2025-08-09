#!/bin/bash -ue
set -euo pipefail

# Crear layout esperado
mkdir -p "genomas/${species}"

# Usar  scripts
bash scripts/download_by_species.sh "$species" "genomas/${species}"

# Si no se descargó nada, crea un marcador para no romper el flujo
ls -1 "genomas/${species}" 2>/dev/null | grep -q . || touch "genomas/${species}/.empty"
