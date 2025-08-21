#%%
import argparse
import ast
from glob import glob
import os
import numpy as np
import pandas as pd
import re
from numpy.lib.stride_tricks import sliding_window_view
from typing import Counter
from concurrent.futures import as_completed, ProcessPoolExecutor
from multiprocessing import Pool
import time


def code_kmer(ref, long_kmer=1, base_n=4):
    seq_array = base_to_int[np.frombuffer(ref.encode(), dtype=np.uint8)]
    kmers = sliding_window_view(seq_array, long_kmer)
    if long_kmer == 1:
        return kmers.flatten().astype(np.int64)
    else:
        powers = base_n ** np.arange(long_kmer - 1, -1, -1, dtype=np.int64)
        encoded_kmers = (kmers * powers).sum(axis=1).astype(np.int64)
        return encoded_kmers
      
def decode_kmer(kmer, long_kmer, base_n=4):
    bases = []
    for _ in range(long_kmer):
        bases.append(int_to_base[kmer % base_n])
        kmer //= base_n
    return ''.join(bases[::-1])

def seq2kmer(seq, long_kmer, base_n=4):
    return dict(Counter(code_kmer(seq, long_kmer=long_kmer, base_n=base_n)))

def kmer_worker(row, long_kmer, base_n):
    return seq2kmer(row, long_kmer=long_kmer, base_n=base_n)

def calcular_kmer(df, long_kmer, base_n, salida):
    print(f'Calculando frecuencias de k-mers de longitud {long_kmer}')
    print('Cantidad de secuencias:', len(df))
    print('Progreso: ')
    list_kmer = []
    for en, row in enumerate(df.itertuples(index=False)):
        result = seq2kmer(row.seq, long_kmer=long_kmer, base_n=base_n)
        list_kmer.append(result)
        if en % 5 == 0:
            print(f'{en}:{long_kmer}', end=' ', flush=True)
    print()
    df_kmer = pd.DataFrame(list_kmer, index=df['nombre_seq'][:len(list_kmer)]).fillna(0).astype(int)
    df_kmer.columns = [decode_kmer(ii, long_kmer) for ii in df_kmer.columns]
    df_kmer.to_csv(salida, sep='\t')
    print(f'Frecuencias de k-mers guardadas en: "{salida}"')
    print('-'*60)

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
if __name__ == "__main__":
    prueba = 2
    if prueba == 1:
        parser = argparse.ArgumentParser(
            description="Calcula frecuencias de k-mers a partir de un archivo TSV de secuencias.",
            add_help=False
        )
        parser.add_argument(
            '-h', '--help',
            action='help',
            default=argparse.SUPPRESS,
            help='Muestra este mensaje de ayuda y sale'
        )
        parser.add_argument(
            '--tsv', type=str, required=True,
            help='Ruta al archivo TSV de entrada (ejemplo: "../outputs/1.4 samples.tsv")'
        )
        parser.add_argument(
            '--long_kmer', type=int, nargs='+', required=True,
            help='Lista de longitudes de k-mer (ejemplo: 3 4 5)'
        )
        parser.add_argument(
            '--salida', type=str, default='../outputs/1.5 frecuency.tsv',
            help='Ruta base del archivo TSV de salida (se agregará _kN.tsv para cada k)'
        )
        parser.add_argument(
            '--max_cpu', type=int, default=None,
            help='Máximo número de CPUs a usar (por defecto: todos los disponibles)'
        )
        args = parser.parse_args()

        base_n = 4
        base_to_int = np.zeros(128, dtype=np.uint8)
        base_to_int[ord('A')] = 0
        base_to_int[ord('C')] = 1
        base_to_int[ord('G')] = 2
        base_to_int[ord('T')] = 3
        int_to_base = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
        if not os.path.exists(args.tsv):
            raise FileNotFoundError(f"El archivo {args.tsv} no existe.")
        
        # Cargar el archivo TSV
        print('Cargando archivo TSV...')
        fasta = pd.read_csv(args.tsv, sep='\t',
                            converters={'nombre_seq': ast.literal_eval,
                                        'seq': ast.literal_eval,
                                        'longitud_seq': ast.literal_eval,})
        cols = ['nombre_seq', 'seq']
        df = pd.DataFrame(fasta[cols], columns=cols).explode(cols).reset_index(drop=True)

        tiempo_inicio = time.time()
        max_workers = args.max_cpu if args.max_cpu is not None else len(args.long_kmer)
        futures = []
        with ProcessPoolExecutor(max_workers=max_workers) as pool:
            for k in args.long_kmer:
                salida_k = args.salida.replace('.tsv', f'_k{k}.tsv')
                futures.append(pool.submit(calcular_kmer, df, k, base_n, salida_k))
            for future in as_completed(futures):
                future.result()
        tiempo_fin = time.time()
        print('Todos los cálculos de k-mer han terminado.')
        print(f"Tiempo total de ejecución: {tiempo_fin - tiempo_inicio:.2f} segundos")

    # ejemplo de uso:
    # python ofrecuencias_kmer.py --tsv "../outputs/1.4 samples.tsv" --long_kmer 3 4 5 --salida "../outputs/1.5 frecuency.tsv" --max_cpu 4
    
    if prueba == 2:
        parser = argparse.ArgumentParser(
            description="Calcula frecuencias de k-mers a partir de un una ruta/*.extensión",
            add_help=False
        )
        parser.add_argument(
            '-h', '--help',
            action='help',
            default=argparse.SUPPRESS,
            help='Muestra este mensaje de ayuda y sale'
        )
        parser.add_argument(
            '--entrada', type=str, required=True,
            help='Ruta con comodín a los archivos fasta (ejemplo: "../genomes/*.fna")'
            )
        parser.add_argument(
            '--long_kmer', type=int, nargs='+', required=True,
            help='Lista de longitudes de k-mer (ejemplo: 3 4 5)'
        )
        parser.add_argument(
            '--salida', type=str, default='../outputs/1.5 frecuency.tsv',
            help='Ruta base del archivo TSV de salida (se agregará _kN.tsv para cada k)'
        )
        parser.add_argument(
            '--max_cpu', type=int, default=None,
            help='Máximo número de CPUs a usar (por defecto: todos los disponibles)'
        )
        args = parser.parse_args()
        #%%
        base_n = 4
        base_to_int = np.zeros(128, dtype=np.uint8)
        base_to_int[ord('A')] = 0
        base_to_int[ord('C')] = 1
        base_to_int[ord('G')] = 2
        base_to_int[ord('T')] = 3
        int_to_base = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
        entrada = args.entrada
        path, comodin = os.path.split(entrada)
        if not os.path.exists(path):
            raise FileNotFoundError(f"El directorio {path} no existe.")
        
        ficheros = [ff for ii in os.walk(path) for jj in ii[1] for ff in glob(ii[0] + '/' + jj + '/' + comodin)] + glob(path + '/' + comodin)
        registros = {ii:jj for fi in ficheros for ii,jj in zip(*lector_fasta(fi)) if ii and jj}
        
        df = pd.DataFrame(list(registros.items()), columns=['nombre_seq', 'seq'])
        
        tiempo_inicio = time.time()
        max_workers = args.max_cpu if args.max_cpu is not None else len(args.long_kmer)
        futures = []
        with ProcessPoolExecutor(max_workers=max_workers) as pool:
            for k in args.long_kmer:
                salida_k = args.salida.replace('.tsv', f'_k{k}.tsv')
                futures.append(pool.submit(calcular_kmer, df, k, base_n, salida_k))
            for future in as_completed(futures):
                future.result()
        tiempo_fin = time.time()
        print('Todos los cálculos de k-mer han terminado.')
        print(f"Tiempo total de ejecución: {tiempo_fin - tiempo_inicio:.2f} segundos")

    # ejemplo de uso
    # python -i ofrecuencias_kmer.py --entrada "../genomes/Streptococcus suis/*.fna" --long_kmer 3 4 5 --salida "../outputs/1.5 frecuency.tsv" --max_cpu 4
