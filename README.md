# proyecto-final-tap
Proyecto final para Tecnicas de la programación avanzada


## Para descargar archivos por especie

#### Especies de cada estudiante:

Lenin Ruiz:
- Enterobacter roggenkampii
- Aeromonas veronii 
- Aeromonas caviae 
- Limosilactobacillus fermentum

Juan Cantos 

- Lacticaseibacillus rhamnosus
- Burkholderia glumae
- Rickettsia rickettsii
- Staphylococcus pseudintermedius

Felipe Espinoza

- Mycobacterium intracellulare
- Klebsiella aerogenes
- Burkholderia multivorans
- Clostridium_F botulinum

Osvaldo Delgado

- Bifidobacterium longum             
- Escherichia fergusonii             
- Bacillus_A cereus                  
- Xylella fastidiosa



# HOW to RUN
Para descarga los documentos a tu local filtrados por especie.

```bash
// Pasando el usuario como 3er argumento:
scripts/download_by_species.sh "s__Streptococcus suis" otro_usuario

// O con variable de entorno:
REMOTE_USER=otro_usuario scripts/download_by_species.sh "Streptococcus suis" genomas/Streptococcus_suis

```

Para poder ejecutar el script de parse_metadata.py de manera independiente y hacer pruebas.
En el terminal ejecutar:

````bash
# con espacios
python scripts/parse_metadata.py --species "Mycobacterium intracellulare"

# con underscore
python scripts/parse_metadata.py "Mycobacterium_intracellulare"

# con prefijo s__
python scripts/parse_metadata.py --species "s__Mycobacterium intracellulare"

// Ejemplo:
python scripts/parse_metadata.py --species "Klebsiella aerogenes"
// Se imprime
Archivo 'samples_{species_underscore}.tsv' creado con éxito, encuéntralo en la carpeta outputs.
Archivo 'labels_Klebsiella_aerogenes.tsv' creado con éxito con 2450 filas, encuéntralo en la carpeta outputs.

```