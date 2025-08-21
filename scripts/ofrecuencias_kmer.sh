# ejemplo de uso:
# Cuando prueba = 1, se ejecuta el script con un archivo TSV de secuencias.
# con kmer 1:
# python ofrecuencias_kmer.py --tsv "../outputs/1.4 samples.tsv" --long_kmer 3 --salida "../outputs/1.5 frecuency.tsv"
# Por defecto prueba = 2, se ejecuta el script con un directorio de archivos FASTA.
python ofrecuencias_kmer.py --entrada "../genomes/Streptococcus suis/*.fna" --long_kmer 3 4 5 --salida "../outputs/1.5 frecuency.tsv" --max_cpu 4