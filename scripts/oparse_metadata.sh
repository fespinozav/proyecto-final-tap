# ejemplos de uso:
# 16 especies
# python oparse_metadata.py --tabla ../Supplememtary_Table_1.csv --especies "s__Enterobacter hoffmannii, s__Aeromonas veronii, s__Aeromonas caviae, s__Limosilactobacillus fermentum, s__Lacticaseibacillus rhamnosus, s__Burkholderia glumae, s__Rickettsia rickettsii, s__Staphylococcus pseudintermedius, s__Mycobacterium intracellulare, s__Enterobacter hormaechei_B, s__Burkholderia multivorans, s__Clostridium_F botulinum, s__Bifidobacterium longum, s__Escherichia coli, s__Bacillus_A cereus, s__Xylella fastidiosa" --ruta_fasta "../genomes/folder with 3 species/*.fna" --salidas "../outputs"

# 3 especies
python oparse_metadata.py --tabla ../Supplememtary_Table_1.csv --especies "s__Klebsiella aerogenes, s__Mycobacterium_intracellulare, s__Streptococcus suis" --ruta_fasta "../genomes/folder with 3 species/*.fna" --salidas "../outputs"