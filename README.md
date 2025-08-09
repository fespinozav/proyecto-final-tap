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