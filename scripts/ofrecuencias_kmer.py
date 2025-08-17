#%%
import ast
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from typing import Counter

def code_kmer(ref, long_kmer=1, base_n=4):
  # convertir a arreglo de enteros
  seq_array = base_to_int[np.frombuffer(ref.encode(), dtype=np.uint8)]  # shape(len(seq),)

  # extraer todos los k-mers como vistas con stride
  kmers = sliding_window_view(seq_array, long_kmer)  # shape (n-long_kmer+1, k)

  # codificar cada k-mer como número en base-n
  if long_kmer == 1:
    return kmers.flatten().astype(np.int64)
  else:
    powers = base_n ** np.arange(long_kmer - 1, -1, -1, dtype=np.int64)
    encoded_kmers = (kmers * powers).sum(axis=1).astype(np.int64)
    return encoded_kmers

# opcional: decodificar k-mers, manteniendo el long_kmer y base_n de la codificación [útil para la interpretación]
def decode_kmer(kmer, long_kmer, base_n=4):
  bases = []
  for _ in range(long_kmer):
    bases.append(int_to_base[kmer % base_n])
    kmer //= base_n
  return ''.join(bases[::-1])  # Invertir para coincidir con el orden original

# contar frecuencias de k-mers en una secuencia
def seq2kmer(seq, long_kmer, base_n=4):    
  # contar frecuencias de k-mers
  return dict(Counter(code_kmer(seq['seq'], long_kmer=long_kmer, base_n=base_n)))

#%%
%%time
if __name__ == "__main__":
  # para parsear
  long_kmer = 3  # Longitud de k-mers

  # configuración inicial
  base_to_int = np.zeros(128, dtype=np.uint8)
  base_to_int[ord('A')] = 0
  base_to_int[ord('C')] = 1
  base_to_int[ord('G')] = 2
  base_to_int[ord('T')] = 3
  int_to_base = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
  base_n = 4 # 4 letras en el alfabeto de ADN
  
  # cargar los datos
  fasta = pd.read_csv('../data/output/1.4 samples.tsv', sep='\t',
                      converters={'nombre_seq': ast.literal_eval,
                                  'seq': ast.literal_eval,
                                  'longitud_seq': ast.literal_eval,})
  # exploder las listas en filas
  cols = ['nombre_seq', 'seq']
  df = pd.DataFrame(fasta[cols], columns=cols).explode(cols).reset_index(drop=True)

  # crear una lista para almacenar los k-mers y sus frecuencias
  list_kmer = []
  for en, seq in df.iterrows():
    # contar frecuencias de k-mers
    list_kmer.append(seq2kmer(seq, long_kmer=long_kmer, base_n=base_n))

  # matriz de frecuencias de k-mers
  df_kmer = pd.DataFrame(list_kmer, index=df['nombre_seq'][:len(list_kmer)]).fillna(0).astype(int)
  df_kmer.columns = [decode_kmer(ii, 3) for ii in df_kmer.columns]
  df_kmer
# %%
