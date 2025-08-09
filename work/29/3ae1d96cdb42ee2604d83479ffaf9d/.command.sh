#!/bin/bash -ue
set -euo pipefail

# Crear layout esperado
mkdir -p "genomas/Mycobacterium intracellulare"

# Usar  scripts
bash scripts/download_by_species.sh "Mycobacterium intracellulare" "genomas/Mycobacterium intracellulare"

# Si no se descargó nada, crea un marcador para no romper el flujo
ls -1 "genomas/Mycobacterium intracellulare" 2>/dev/null | grep -q . || touch "genomas/Mycobacterium intracellulare/.empty"
