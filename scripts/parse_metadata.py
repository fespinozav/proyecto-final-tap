import pandas as pd
import argparse
import os

def parse_metadata(input_csv, output_dir, selected_classes=None):
    # Leer archivo CSV
    df = pd.read_csv(input_csv)

    # Filtrar columnas relevantes
    required_cols = ['filename', 'class', 'species', 'taxonomy']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Falta columna requerida: {col}")

    # Filtrar clases si es necesario
    if selected_classes:
        df = df[df['class'].isin(selected_classes)]

    # Filtrar entradas con archivos faltantes
    df = df[df['filename'].apply(lambda x: os.path.exists(x))]

    # Guardar samples.tsv
    samples_path = os.path.join(output_dir, "samples.tsv")
    df[['filename']].to_csv(samples_path, sep='\t', header=False, index=False)

    # Guardar labels.tsv
    labels_path = os.path.join(output_dir, "labels.tsv")
    df[['filename', 'class', 'species']].to_csv(labels_path, sep='\t', index=False)

    print(f"Archivos generados:\n- {samples_path}\n- {labels_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parser de metadata para el pipeline GBDP")
    parser.add_argument("--input_csv", required=True, help="Archivo CSV con metadatos")
    parser.add_argument("--output_dir", required=True, help="Directorio de salida")
    parser.add_argument("--classes", nargs="+", help="Clases taxonómicas a considerar (opcional)")

    args = parser.parse_args()

    parse_metadata(args.input_csv, args.output_dir, args.classes)