# Proyecto Final TAP

## Descripción

Este proyecto corresponde al trabajo final para la asignatura Técnicas de la Programación Avanzada. Su objetivo principal es facilitar la descarga y procesamiento de archivos genómicos filtrados por especie, así como el análisis de metadatos asociados.

## Instalación

Asegúrate de tener los scripts necesarios en la carpeta `scripts/` y los permisos adecuados para ejecutar los archivos `.sh` y `.py`.

## Uso

### Descargar archivos por especie

El script `download_by_species.sh` permite descargar documentos filtrados por especie. Puedes ejecutar el script de dos formas:

- Pasando el usuario remoto como tercer argumento:

```bash
scripts/download_by_species.sh "s__Streptococcus suis" otro_usuario
```

- Usando la variable de entorno `REMOTE_USER`:

```bash
REMOTE_USER=otro_usuario scripts/download_by_species.sh "Streptococcus suis" genomas/Streptococcus_suis
```

### Ejecutar el script `parse_metadata.py`

El script `parse_metadata.py` permite procesar metadatos para una especie específica. Puedes ejecutarlo con diferentes formatos para la especie:

- Con espacios:

```bash
python scripts/parse_metadata.py --species "Mycobacterium intracellulare"
```

- Con guiones bajos:

```bash
python scripts/parse_metadata.py "Mycobacterium_intracellulare"
```

- Con prefijo `s__`:

```bash
python scripts/parse_metadata.py --species "s__Mycobacterium intracellulare"
```

## Especies por estudiante

A continuación, se listan las especies asignadas a cada estudiante para la descarga y análisis:

- **Lenin Ruiz:**
  - Enterobacter roggenkampii
  - Aeromonas veronii 
  - Aeromonas caviae 
  - Limosilactobacillus fermentum

- **Juan Cantos:**
  - Lacticaseibacillus rhamnosus
  - Burkholderia glumae
  - Rickettsia rickettsii
  - Staphylococcus pseudintermedius

- **Felipe Espinoza:**
  - Mycobacterium intracellulare
  - Klebsiella aerogenes
  - Burkholderia multivorans
  - Clostridium_F botulinum

- **Osvaldo Delgado:**
  - Bifidobacterium longum             
  - Escherichia fergusonii             
  - Bacillus_A cereus                  
  - Xylella fastidiosa

## Ejemplos de ejecución

Ejemplo de ejecución para `parse_metadata.py`:

```bash
python scripts/parse_metadata.py --species "Klebsiella aerogenes"
```

Al ejecutarlo, se imprimirá un mensaje indicando la creación de archivos con éxito:

- Archivo `samples_{species_underscore}.tsv` creado con éxito, encuéntralo en la carpeta `outputs`.
- Archivo `labels_Klebsiella_aerogenes.tsv` creado con éxito con 2450 filas, encuéntralo en la carpeta `outputs`.