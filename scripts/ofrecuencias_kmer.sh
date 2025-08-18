# ejemplo de uso:
# con kmer 1:
python ofrecuencias_kmer.py --tsv "../outputs/1.4 samples.tsv" --long_kmer 3 --salida "../outputs/1.5 frecuency.tsv"
# con kmer 3, 4 y 5 y hasta un máximo de 2 CPUs:
# python ofrecuencias_kmer.py --tsv "../outputs/1.4 samples.tsv" --long_kmer 3 4 5 --salida "../outputs/1.5 frecuency.tsv" --max_cpu 2