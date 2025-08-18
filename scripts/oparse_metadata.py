import argparse
import os
import pandas as pd
import re
import time
from glob import glob

# filtrado general
def filtrar_especies(df, lista_especies, guardar=True, output_dir='../outputs'):
    os.makedirs(output_dir, exist_ok=True)
    df = df[df['species'].isin(lista_especies)]
    if guardar:
        df.to_csv(f'{output_dir}/1.2 Supplementary_Table_1_short_by_species.csv', index=False)
    return df

 # metadatos
def metadatos(fasta_input, df, guardar=True, output_dir='../outputs'):
    fasta = {'índice_in_suplementary_table':[], 'fichero':[]}
    for ii in glob(fasta_input):
        for en,jj in enumerate(df['accession']):
            if ii.split('/')[-1].startswith(jj):
                fasta['índice_in_suplementary_table'].append(en)
                fasta['fichero'].append(ii)
    fasta = pd.DataFrame(fasta).sort_values('índice_in_suplementary_table')
    # Dominio, filo, clase, orden, familia, género y especie.
    meta = pd.DataFrame(df.iloc[fasta['índice_in_suplementary_table']]['gtdb_taxonomy'].str.split(';').tolist(), columns=['dominio', 'filo', 'clase', 'orden', 'familia', 'genero', 'especie'])
    meta.insert(0, 'accession', df.iloc[fasta['índice_in_suplementary_table']]['accession'].values)
    meta.insert(0, 'fichero', fasta['fichero'].values)
    meta.insert(0, 'índice_in_suplementary_table', fasta['índice_in_suplementary_table'].values)
    if guardar:
        meta.to_csv(f'{output_dir}/1.3 labels.tsv', index=False, sep='\t')
    return meta

# lector de secuencias
def lector_fasta(file):
    with open(file, 'r') as f:
        lectura = f.read()
    lectura = lectura.replace('\n', '')
    pattern_name = '(>.*?)[A-Z]{10}'
    pattern_seq = '>.*?([A-Z]{10,})'
    nombres = re.findall(pattern_name, lectura)
    secuencias = re.findall(pattern_seq, lectura)
    return nombres, secuencias

# secuencias
def secuencias(secuencias, guardar=True, output_dir='../outputs'):
    os.makedirs(output_dir, exist_ok=True)
    fasta = secuencias.copy()
    dict_data = {'idx': [], 'nombre_seq': [], 
                'seq': [], 'cantidad_seq': [],
                'longitud_seq': []}
    print('Progreso:', end=' ', flush=True)
    for en,ii in enumerate(fasta['fichero']):
        nombres_seq, seq = lector_fasta(ii)
        ctdad = [len(seq) for seq in seq]
        dict_data['idx'].append(en)
        dict_data['nombre_seq'].append(nombres_seq)
        dict_data['seq'].append(seq)
        dict_data['cantidad_seq'].append(len(seq))
        dict_data['longitud_seq'].append(ctdad)
        if en%5 == 0:
            print(en, end=' ', flush=True)
    print()
    fasta = pd.merge(fasta,pd.DataFrame(dict_data), left_on=fasta.index,right_on='idx').drop(columns=['idx'])
    if guardar:
        fasta.to_csv(f'{output_dir}/1.4 samples.tsv', index=False, sep='\t')
    return fasta

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Procesa metadatos y secuencias FASTA para el proyecto TAP.",
        add_help=False
    )
    parser.add_argument(
    '-h', '--help',
    action='help',
    default=argparse.SUPPRESS,
    help='Muestra este mensaje de ayuda y sale'
)
    parser.add_argument(
        '--tabla', type=str, required=True,
        help='Ruta al archivo Supplementary_Table_1.csv'
    )
    parser.add_argument(
        '--especies', type=str, required=True,
        help='Lista de especies separadas por coma (ejemplo: "s__Escherichia coli,s__Bacillus_A cereus")'
    )
    parser.add_argument(
        '--ruta_fasta', type=str, required=True,
        help='Ruta de los archivos fasta, incluyendo comodín y extensión (ejemplo: "/ruta/*.fna")'
    )    
    parser.add_argument(
        '--salidas', type=str, default='../outputs',
        help='Ruta del directorio donde se guardarán los archivos de salida'
    )
    args = parser.parse_args()

    tiempo_inicio = time.time()

    # Cargar tabla
    if not os.path.exists(args.tabla):
        raise FileNotFoundError(f"El archivo {args.tabla} no existe.")
    df = pd.read_csv(args.tabla, low_memory=False)
    print('Tabla cargada con éxito.')
    print('-'*60)
    lista_especies = [esp.strip() for esp in args.especies.split(',')]

    # Filtrar especies
    df = filtrar_especies(df, lista_especies)
    print(f'Especies filtradas: {lista_especies}')
    print(f'Registros después del filtrado: {len(df)}')
    print(f'Archivo guardado en: "{args.salidas}/1.2 Supplementary_Table_1_short_by_species.csv"')
    print('-'*60)

    # Metadatos
    if len(glob(args.ruta_fasta)) == 0:
        raise FileNotFoundError(f"No se encontraron archivos fasta en la ruta {args.ruta_fasta}.")
    meta = metadatos(args.ruta_fasta, df)
    print(f'Metadatos procesados y guardados en: "{args.salidas}/1.3 labels.tsv"')
    print(f'Número de secuencias encontradas: {len(meta)}')
    print('-'*60)
    
    # Secuencias
    print('Extrayendo secuencias FASTA...')
    secuencias = secuencias(meta[['fichero']])
    print(f'Secuencias extraídas, procesadas y guardados en: "{args.salidas}/1.4 samples.tsv"')            
    print(f'Número de secuencias extraídas: {len(secuencias)}')
    print('-'*60)
    print('Proceso completado con éxito.')

    tiempo_fin = time.time()
    print(f"Tiempo total de ejecución: {tiempo_fin - tiempo_inicio:.2f} segundos")
    
# ejemplo de uso:
# python oparse_metadata.py --help
# python oparse_metadata.py --tabla ../Supplememtary_Table_1.csv --especies "s__Enterobacter hoffmannii, s__Aeromonas veronii, s__Aeromonas caviae, s__Limosilactobacillus fermentum, s__Lacticaseibacillus rhamnosus, s__Burkholderia glumae, s__Rickettsia rickettsii, s__Staphylococcus pseudintermedius, s__Mycobacterium intracellulare, s__Enterobacter hormaechei_B, s__Burkholderia multivorans, s__Clostridium_F botulinum, s__Bifidobacterium longum, s__Escherichia coli, s__Bacillus_A cereus, s__Xylella fastidiosa" --ruta_fasta "/data/T-cnicas-Avanzadas-de-Programaci-n/0. Proyecto/Data_forTAP/*.fna" --salidas "../outputs"
