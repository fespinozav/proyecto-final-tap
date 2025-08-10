#!/usr/bin/env bash
set -euo pipefail

species="${1:-}"
[[ -z "$species" ]] && { echo "Falta especie"; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTDIR="${OUTDIR:-.}"   # Nextflow la setea a $PWD del workdir; si corres a mano, será "."

echo "[NF] species=$species"
echo "[NF] PROJ_DIR=$PROJ_DIR"
echo "[NF] OUTDIR=$OUTDIR"

# 1) Ejecuta el Python desde la raíz del repo (ahí existen genomes/ y el CSV)
(
  cd "$PROJ_DIR"
  python3 "$PROJ_DIR/scripts/parse_metadata.py" --species "$species"
)

# 2) Copia los outputs generados en $PROJ_DIR/outputs al OUTDIR (workdir)
mkdir -p "$OUTDIR"
shopt -s nullglob
for f in "$PROJ_DIR"/outputs/samples_*.tsv "$PROJ_DIR"/outputs/labels_*.tsv; do
  cp -f "$f" "$OUTDIR"/
done

echo "[NF] Copiados al OUTDIR:"
ls -l "$OUTDIR" || true