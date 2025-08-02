#!/usr/bin/env bash

# Uso: ./download_by_species.sh "s__Streptococcus suis" /ruta/salida

SPECIES="$1"
DEST="$2"
REMOTE_USER="fespinoza"
REMOTE_HOST="faraday.utem.cl"
REMOTE_DIR="/home/amoya/Data_forTap/selected_Genomes"

if [[ -z "$SPECIES" || -z "$DEST" ]]; then
  echo "❗ Uso: $0 \"s__Nombre especie\" /ruta/destino"
  exit 1
fi

mkdir -p "$DEST"

echo "🔎 Obteniendo accessions asociados a la especie \"$SPECIES\"..."
ACCESSIONS=$(python3 scripts/get_accessions.py "$SPECIES")

if [[ -z "$ACCESSIONS" ]]; then
  echo "❌ No se encontraron accessions para esa especie."
  exit 1
fi

echo "📥 Descargando archivos:"
for acc in $ACCESSIONS; do
  # Buscar archivos que empiecen con el accession
  ssh ${REMOTE_USER}@${REMOTE_HOST} "find ${REMOTE_DIR} -type f -name \"${acc}*.fna*\"" | \
  while read -r remote_file; do
    echo "⬇️  $remote_file"
    scp "${REMOTE_USER}@${REMOTE_HOST}:${remote_file}" "$DEST/"
  done
done

echo "✅ Descarga finalizada en: $DEST"