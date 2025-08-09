#!/bin/bash -ue
set -euo pipefail

# Destino dentro del workdir (para que Nextflow lo recoja como output)
DEST="$PWD/genomas/Mycobacterium intracellulare"
mkdir -p "$DEST"

# Cambiar al root del proyecto para que los paths relativos del script funcionen
cd /Users/felipeespinoza/Documents/GitHub/proyecto-final-tap

# Ejecutar tu script tal cual, pero apuntando al DEST absoluto del workdir
bash scripts/download_by_species.sh "Mycobacterium intracellulare" "$DEST"

# Volver al workdir (por si acaso)
cd - >/dev/null

# Si no se descargó nada, crear marcador para no romper el flujo
ls -1 "$DEST" 2>/dev/null | grep -q . || touch "$DEST/.empty"
