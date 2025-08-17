#%%
import os
import numpy as np
import pandas as pd
import re
from glob import glob

# filtrado general
def filtrar_especies(df, lista_especies, guardar=True):
    df = df[df['species'].isin(lista_especies)]
    if guardar:
        df.to_csv('../outputs/1.2 Supplementary_Table_1_short_by_species.csv', index=False)
    return df

 # metadatos
def metadatos(fasta_input, df, guardar=True):
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
        meta.to_csv('../outputs/1.3 labels.tsv', index=False, sep='\t')
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
def secuencias(secuencias, guardar=True):
    fasta = secuencias.copy()
    dict_data = {'idx': [], 'nombre_seq': [], 
                'seq': [], 'cantidad_seq': [],
                'longitud_seq': []}
    for en,ii in enumerate(fasta['fichero']):
        nombres_seq, seq = lector_fasta(ii)
        ctdad = [len(seq) for seq in seq]
        dict_data['idx'].append(en)
        dict_data['nombre_seq'].append(nombres_seq)
        dict_data['seq'].append(seq)
        dict_data['cantidad_seq'].append(len(seq))
        dict_data['longitud_seq'].append(ctdad)
    fasta = pd.merge(fasta,pd.DataFrame(dict_data), left_on=fasta.index,right_on='idx').drop(columns=['idx'])
    if guardar:
        fasta.to_csv('../outputs/1.4 samples.tsv', index=False, sep='\t')
    return fasta
#%%
if __name__ == '__main__':
    # selección
    path_supplementary_table = '../Supplememtary_Table_1.csv'
    df = pd.read_csv(path_supplementary_table, low_memory=False)
    lista_especies = seleccionar_especies(path_supplementary_table)
    
    # filtrado general
    lista_especies = [lista_especies[0]] # todas las pruebas se harán con esta especie
    print('Se trabajará solo con la especie:', lista_especies[0])
    df = filtrar_especies(df, lista_especies)
    
    # metadatos
    fasta_input = '../0. Proyecto/Data_forTAP/*.fna'
    meta = metadatos(fasta_input, df)

    # secuencias
    secuencias = secuencias(meta[['fichero']])

# %%
