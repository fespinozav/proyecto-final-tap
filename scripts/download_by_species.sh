#!/usr/bin/env bash

# Uso: ./download_by_species.sh "s__Streptococcus suis" /ruta/salida

SPECIES_RAW="$1"
DEST_RAW="${2:-}"

REMOTE_USER="fespinoza"
REMOTE_HOST="faraday.utem.cl"
REMOTE_DIR="/home/amoya/Data_forTap/selected_Genomes"

if [[ -z "$SPECIES_RAW" ]]; then
  echo "❗ Uso: $0 \"Nombre especie\" [ruta/destino]"
  echo "   Ej.: $0 \"Mycobacterium intracellulare\""
  exit 1
fi

# Normaliza especie: elimina prefijo s__, colapsa espacios, quita bordes
SPECIES_CLEAN="$(printf "%s" "$SPECIES_RAW" | sed 's/^s__//I' | tr '_' ' ' | sed -E 's/[[:space:]]+/ /g; s/^ //; s/ $//')"
SPECIES_US="$(printf "%s" "$SPECIES_CLEAN" | tr '[:space:]' '_' )"

# Si no se entrega DEST, crear dentro de genomes/<Especie_con_underscores>
BASE_DIR="genomes"
if [[ -z "$DEST_RAW" ]]; then
  DEST="${BASE_DIR}/${SPECIES_US}"
else
  DEST="$DEST_RAW"
fi

mkdir -p "$DEST"

echo "🔎 Obteniendo accessions asociados a la especie \"$SPECIES_CLEAN\"..."
ACCESSIONS=$(python3 scripts/get_accessions.py "$SPECIES_CLEAN")

if [[ -z "$ACCESSIONS" ]]; then
  echo "❌ No se encontraron accessions para esa especie."
  exit 1
fi

echo "📥 Descargando archivos:"
for acc in $ACCESSIONS; do
  # Buscar archivos que empiecen con el accession
  ssh ${REMOTE_USER}@${REMOTE_HOST} "find ${REMOTE_DIR} -type f -name \"${acc}*.fna\"" | \
  while read -r remote_file; do
    echo "⬇️  $remote_file"
    scp "${REMOTE_USER}@${REMOTE_HOST}:${remote_file}" "$DEST/"
  done
done

echo "✅ Descarga finalizada en: $DEST (especie: $SPECIES_CLEAN)"