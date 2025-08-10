#!/usr/bin/env bash
set -euo pipefail

species="${1:-}"
if [[ -z "$species" ]]; then
  echo "[ERROR] Falta especie. Uso: scripts/parse_metadata.sh \"Genus species\"" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# OUTDIR: preferir el que viene del proceso (env) o por defecto al PWD
OUTDIR="${OUTDIR:-$PWD}"

echo "[SH] species=$species"
echo "[SH] PROJ_DIR=$PROJ_DIR"
echo "[SH] OUTDIR=$OUTDIR"
mkdir -p "$OUTDIR"

# Ejecutar el Python desde la raíz del proyecto, pero escribiendo SIEMPRE en OUTDIR
(
  cd "$PROJ_DIR"
  OUTDIR="$OUTDIR" python3 "$PROJ_DIR/scripts/parse_metadata.py" \
    --species "$species" \
    --outdir "$OUTDIR"
)

echo "[SH] Archivos generados en OUTDIR:"
ls -l "$OUTDIR" || true