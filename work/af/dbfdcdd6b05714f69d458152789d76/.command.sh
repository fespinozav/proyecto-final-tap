#!/bin/bash -ue
set -euo pipefail

# Destino dentro del workdir (para que Nextflow lo recoja como output)
DEST="$PWD/genomas/Mycobacterium intracellulare"
mkdir -p "$DEST"

# Normalizar especie para get_accessions.py -> requiere prefijo s__
RAW_SPEC="Mycobacterium intracellulare"
if [[ "$RAW_SPEC" == s__* ]]; then
  SPEC_LABEL="$RAW_SPEC"
else
  SPEC_LABEL="s__${RAW_SPEC}"
fi

# Cambiar al root del proyecto para que los paths relativos del script funcionen
cd /Users/felipeespinoza/Documents/GitHub/proyecto-final-tap

# Ejecutar tu script tal cual, pero apuntando al DEST absoluto del workdir
bash scripts/download_by_species.sh "$SPEC_LABEL" "$DEST"

# Volver al workdir (por si acaso)
cd - >/dev/null

# Si no se descargó nada, crear marcador para no romper el flujo
ls -1 "$DEST" 2>/dev/null | grep -q . || touch "$DEST/.empty"
