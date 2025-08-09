import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from Bio import SeqIO
import re
from pathlib import Path
import argparse
from IPython.display import display


 # === CLI args: species name (accepts forms like "s__Genus_species", "Genus species", or "Genus_species") ===
parser = argparse.ArgumentParser(description="Parse metadata for a given species folder under genomes/")
parser.add_argument("--species", dest="species", required=False, help="Species name. Accepts 's__Genus_species', 'Genus species', or 'Genus_species'.")
parser.add_argument("species_pos", nargs='?', default=None, help="Positional species name (optional)")
args = parser.parse_args()

# Choose CLI source (positional has lower priority than --species)
raw_species = args.species if args.species else args.species_pos
if not raw_species:
    raise SystemExit("[ERROR] Debe proporcionar la especie via '--species " +
                     "\"Genus species\"' o como argumento posicional. Ej.:\n" +
                     "    python scripts/parse_metadata.py --species 'Mycobacterium intracellulare'")

# Normalize: strip s__ prefix, accept '_' or space, collapse whitespace
def normalize_species(s: str) -> str:
    s = s.strip()
    if s.lower().startswith('s__'):
        s = s[3:]
    s = s.replace('_', ' ')
    s = re.sub(r"\s+", " ", s)
    return s.strip()

species_clean = normalize_species(raw_species)
# Build common variants for matching folder names
species_space = species_clean  # e.g., 'Mycobacterium intracellulare'
species_underscore = species_clean.replace(' ', '_')  # e.g., 'Mycobacterium_intracellulare'

# Resolve folder under genomes/ preferring underscore variant, then space, case-insensitive
genomes_dir = Path(os.getcwd()) / 'genomes'
if not genomes_dir.exists():
    raise SystemExit(f"[ERROR] No existe el directorio base de genomas: {genomes_dir}")

def find_species_dir(base: Path, candidates: list[str]) -> Path | None:
    cand_lower = [c.lower() for c in candidates]
    for d in base.iterdir():
        if d.is_dir():
            name_l = d.name.lower()
            if name_l in cand_lower:
                return d
    return None

species_dir = find_species_dir(genomes_dir, [species_underscore, species_space])
if species_dir is None:
    # Try also accepting a folder with prefixed 's__' (some datasets use it)
    species_dir = find_species_dir(genomes_dir, [f"s__{species_underscore}", f"s__{species_space}"])

if species_dir is None:
    raise SystemExit(
        "[ERROR] No se encontró carpeta de especie bajo 'genomes/'. "
        f"Buscado por: '{species_underscore}' o '{species_space}' (con o sin 's__').\n"
        f"Carpetas disponibles en genomes/: {[p.name for p in genomes_dir.iterdir() if p.is_dir()]}")

# Use resolved directory name as the species label for downstream paths
species = species_dir.name
features = pd.read_csv('Supplememtary_Table_1.csv', dtype=str, low_memory=False)
features.columns = features.columns.str.strip()
folder_path = os.path.join(os.getcwd(), 'genomes', species)

# Filtrar solo archivos que terminen en '.fna' y NO en '.fna.gz'
fna_files = [f for f in Path(folder_path).glob("*.fna") if not f.name.endswith(".fna.gz")]

# Lista para guardar resultados
datos = []
for file in fna_files:
    try:
        record = next(SeqIO.parse(file, "fasta"))
        full_desc = record.description
        seq_id = record.id
        filename = file.name

        # Regex para capturar el nombre del organismo (Género + especie)
        match = re.match(r"^[^\s]+\s+([A-Z][a-z]+ [a-z]+)(.*)", full_desc)
        if match:
            organism = match.group(1).strip()
            strain_description = match.group(2).strip().strip(",")
        else:
            organism = "Unknown"
            strain_description = ""

        # Guardar
        datos.append({
            "filename": filename,
            "sequence_id": seq_id,
            "organism_name": organism,
            "strain_description": strain_description,
            "full_description": full_desc
        })

    except Exception as e:
        print(f"Error leyendo {file.name}: {e}")

# Crear DataFrame
df = pd.DataFrame(datos)

# Guardar como TSV
df.to_csv(f"outputs/samples_{species_underscore}.tsv", sep="\t", index=False)
print("Archivo 'samples_{species_underscore}.tsv' creado con éxito, encuéntralo en la carpeta outputs.")

labels_data = []

species_list = list(features['species'].unique())

# Función de búsqueda
def buscar_especie_en_fna(fna_path):
    record = next(SeqIO.parse(fna_path, "fasta"))
    header = record.description.lower()
    
    matches = []
    for species in species_list:
        especie = species.replace("s__", "").lower()
        if especie in header:
            matches.append(species)

    if matches:
        # Filtra en la tabla de metadatos (features), no en el DataFrame de muestras (df)
        df_matches = features[features['species'].isin(matches)]
        #print(f"✅ Coincidencias encontradas en el header:\n{matches}")
    else:
        df_matches = None
        #print("❌ No se encontraron especies reconocidas en el header.")

    return header, matches, df_matches

for file in fna_files:
    # Ejecuta búsqueda
    header, coincidencias, df_matches = buscar_especie_en_fna(file)
    
    if df_matches is not None:
        df_matches = df_matches.copy()
        # Para sacar todos los campos
        #df_matches['filename'] = file.name
        #labels_data.append(df_matches)
        
        # Select only the required columns plus filename
        required_cols = [
            "accession",
            "checkm_marker_lineage",
            "ssu_silva_blast_subject_id",
            "ssu_silva_taxonomy",
            "species"
        ]
        reduced_df = df_matches[required_cols].copy()
        reduced_df.insert(0, "filename", file.name)
        labels_data.append(reduced_df)

if labels_data:
    labels_df = pd.concat(labels_data, ignore_index=True)
    labels_df.to_csv(f"outputs/labels_{species_underscore}.tsv", sep="\t", index=False)
    print(f"Archivo 'labels_{species_underscore}.tsv' creado con éxito con {len(labels_df)} filas, encuéntralo en la carpeta outputs.")