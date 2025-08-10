#!/usr/bin/env bash
set -euo pipefail

# --- Opciones ---
DRY_RUN=false
KEEP_OUTPUTS=false
KEEP_RESULTS=false
KEEP_REPORTS=false
YES=false

for arg in "$@"; do
  case "$arg" in
    -n|--dry-run) DRY_RUN=true ;;
    --keep-outputs) KEEP_OUTPUTS=true ;;
    --keep-results) KEEP_RESULTS=true ;;
    --keep-reports) KEEP_REPORTS=true ;;
    -y|--yes) YES=true ;;
    -h|--help)
      cat <<EOF
Uso: $(basename "$0") [opciones]

Opciones:
  -n, --dry-run      Muestra qué se borraría, sin borrar.
      --keep-outputs No borra ./outputs
      --keep-results No borra ./results
      --keep-reports No borra ./reports
  -y, --yes          No pedir confirmación
  -h, --help         Ayuda

Borra: work/, .nextflow*, reportes/artefactos HTML/SVG/trace en la raíz,
y TSV sueltos (samples_*.tsv, labels_*.tsv).
EOF
      exit 0
      ;;
    *)
      echo "[WARN] Opción desconocida: $arg" ;;
  esac
done

# --- Helpers ---
do_rm() {
  local target="$1"
  if $DRY_RUN; then
    echo "[dry-run] rm -rf $target"
  else
    rm -rf $target 2>/dev/null || true
  fi
}

do_find_delete() {
  if $DRY_RUN; then
    echo "[dry-run] find . -maxdepth 1 -type f \\( $1 \\) -print"
  else
    # Mostrar antes de borrar
    eval "find . -maxdepth 1 -type f \( $1 \) -print" || true
    eval "find . -maxdepth 1 -type f \( $1 \) -delete" || true
  fi
}

confirm() {
  $YES && return 0
  printf "¿Seguro que quieres limpiar? [y/N] "
  IFS= read -r resp || true
  resp_lc=$(printf '%s' "${resp:-}" | tr '[:upper:]' '[:lower:]')
  [ "$resp_lc" = "y" ] || [ "$resp_lc" = "yes" ]
}

# --- Mostrar plan ---
echo "== Plan de limpieza =="
echo "- nextflow cache/work: work/ .nextflow .nextflow.*"
$KEEP_OUTPUTS || echo "- outputs/"
$KEEP_RESULTS || echo "- results/"
$KEEP_REPORTS || echo "- reports/"
echo "- artefactos raíz: report-*.html, timeline-*.html, nf-*.html, nf-*.svg, flow.svg, dag.svg, trace.txt"
echo "- TSV sueltos en raíz: samples_*.tsv, labels_*.tsv"
$DRY_RUN && echo "(modo dry-run: no se borra nada)"
echo

confirm || { echo "Cancelado."; exit 0; }

# --- Ejecutar limpieza ---

# 1) Limpieza Nextflow (cache/work)
if command -v nextflow >/dev/null 2>&1 && ! $DRY_RUN; then
  nextflow clean -f || true
fi
do_rm work
do_rm .nextflow
do_rm .nextflow.*

# 2) Carpeta(s) de publicación
$KEEP_OUTPUTS || do_rm outputs
$KEEP_RESULTS || do_rm results
$KEEP_REPORTS || do_rm reports

# 3) Artefactos raíz
PATTERNS="-name 'report-*.html' -o -name 'timeline-*.html' -o -name 'nf-*.html' -o -name 'nf-*.svg' -o -name 'flow.svg' -o -name 'dag.svg' -o -name 'trace.txt' -o -name 'samples_*.tsv' -o -name 'labels_*.tsv'"
do_find_delete "$PATTERNS"

echo "✅ Limpieza completada."