import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from Bio import SeqIO
import re
from pathlib import Path
import argparse
from IPython.display import display


species = 'Mycobacterium intracellulare'
features = pd.read_csv('Supplememtary_Table_1.csv', dtype=str, low_memory=False)
features.columns = features.columns.str.strip()
folder_path = os.path.join(os.getcwd(), 'genomas', species)

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
df.to_csv("samples.tsv", sep="\t", index=False)
print("Archivo 'samples.tsv' creado con éxito.")

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
    labels_df.to_csv("labels.tsv", sep="\t", index=False)
    print(f"Archivo 'labels.tsv' creado con éxito con {len(labels_df)} filas.")