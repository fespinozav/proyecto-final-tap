#!/bin/bash -euo pipefail -c
set -euo pipefail

echo "[NF] start $(date)"
echo "[NF] PWD: $(pwd)"
echo "[NF] species: Mycobacterium intracellulare"
echo "[NF] projectDir: /Users/felipeespinoza/Documents/GitHub/proyecto-final-tap"

# nos aseguramos que el wrapper sea ejecutable
chmod +x "/Users/felipeespinoza/Documents/GitHub/proyecto-final-tap/scripts/parse_metadata.sh"

echo "[NF] genomes exists? -> /Users/felipeespinoza/Documents/GitHub/proyecto-final-tap/genomes"
ls -ld "/Users/felipeespinoza/Documents/GitHub/proyecto-final-tap/genomes" || true

# Ejecuta el wrapper y **escribe en el workdir**
OUTDIR="$PWD" "/Users/felipeespinoza/Documents/GitHub/proyecto-final-tap/scripts/parse_metadata.sh" "Mycobacterium intracellulare"

echo "[NF] generated in CWD:"
ls -lh || true
