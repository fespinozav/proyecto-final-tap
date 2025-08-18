# ejemplos de uso:
# 16 especies
# python oparse_metadata.py --tabla ../Supplememtary_Table_1.csv --especies "s__Enterobacter hoffmannii, s__Aeromonas veronii, s__Aeromonas caviae, s__Limosilactobacillus fermentum, s__Lacticaseibacillus rhamnosus, s__Burkholderia glumae, s__Rickettsia rickettsii, s__Staphylococcus pseudintermedius, s__Mycobacterium intracellulare, s__Enterobacter hormaechei_B, s__Burkholderia multivorans, s__Clostridium_F botulinum, s__Bifidobacterium longum, s__Escherichia coli, s__Bacillus_A cereus, s__Xylella fastidiosa" --ruta_fasta "/data/T-cnicas-Avanzadas-de-Programaci-n/0. Proyecto/Data_forTAP/*.fna" --salidas "../outputs"

# 1 especie
python oparse_metadata.py --tabla ../Supplememtary_Table_1.csv --especies "s__Bifidobacterium longum" --ruta_fasta "/data/T-cnicas-Avanzadas-de-Programaci-n/0. Proyecto/Data_forTAP/*.fna" --salidas "../outputs"
