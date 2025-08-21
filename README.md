# Proyecto Final TAP

## Descripción

Este proyecto corresponde al trabajo final para la asignatura **Técnicas de la Programación Avanzada (TAP)**. Su objetivo es **facilitar la descarga y el procesamiento de archivos genómicos filtrados por especie**, además del **análisis de metadatos** asociados.

Incluye dos formas de uso:

- **Modo scripts**: `scripts/download_by_species.sh` y `scripts/parse_metadata.py`.
- **Modo pipeline** con **Nextflow (DSL2)**: implementa un flujo de trabajo integral basado en BLAST mediante procesos secuenciales: `PARSE_METADATA` → `MAKE_DB` → `RUN_BLAST` → `EXTRACT_HSPS` → `CALC_DISTANCES` → `RUN_HEATMAPS` → `RUN_CORRELACION`. Este enfoque genera matrices de distancia filogenéticas adecuadas para el análisis evolutivo y la clasificación taxonómica detallada por medio de mapas de calor que nos permite comparar la diferencia entre las secuencias comparadas, y también la diferencia entre las 10 fórmulas de distancia usadas.

## Resultados

Los resultados generados por la ejecución del pipeline se almacenan en la carpeta `figures/`. Dentro de esta se incluyen los resultados que permiten realizar el análisis de distancias y correlaciones entre las secuencias procesadas. Asimismo, se generan visualizaciones como mapas de calor y matrices comparativas, acompañadas de conclusiones derivadas de los cálculos estadísticos y filogenéticos en el archivo 'RESULTADOS Y CONCLUSIONES.md', lo que facilita la interpretación de la diversidad y similitud entre especies.

---

## Requisitos

- **Nextflow** ≥ 24.10.1
- **Bash** (macOS / Linux)
- **Conda 24.11.3**
- **Python 3.8+** con:
  - `numpy`
  - `pandas`
  - `biopython`
  - `blast`
  - `matplotlib`
  - `seaborn`
  - `scikit-bio`
- Acceso a la carpeta `genomes/` con subcarpetas por especie (p.ej. `Mycobacterium_intracellulare/`).

> En macOS sin contenedor verás `WARN: Task runtime metrics are not reported…` (es esperado).

Instalación de ambiente conda con todas las dependencias:
- Ingresar a la carpeta del repositorio
- Asegurarse de que conda este instalado y corriendo (si se usa el sistema operativo Windows, asegurarse de tener [instalado el subsitema WSL](https://learn.microsoft.com/es-mx/windows/wsl/install), e [instalar miniconda dentro de WSL](https://www.anaconda.com/docs/getting-started/miniconda/install#linux-terminal-installer))
- Instalar y activar el ambiente conda ejecutando los siguientes comandos:
```bash
conda env create -f environment.yml
conda activate TAP
```

Si trabajas con MacOS

```bash
conda env create -f environment.yaml
conda activate tap-mac
```

---

## Estructura del proyecto (resumen)

```
.
├── genomes/                       # Datos locales por especie
├── modules/local/                 # Proceso Nextflow
├── scripts/                       # Wrappers y utilidades
├── nextflow.config                # Config del pipeline
├── outputs/                       # Publicación por defecto (ver params.outdir)
├── reports/                       # Reportes si activas -with-*
└── README.md
```

---

## Flujo con Nextflow

El pipeline expone los siguientes procesos:

### `PARSE_METADATA`
- **Input**: canal de especies (`--species` única o `--species_list` archivo).
- **Ejecución**:
  1. `parse_metadata.sh` posiciona entorno y llama
  2. `parse_metadata.py` que:
     - normaliza el nombre de la especie
     - localiza FASTA (`*.fna` / `*.fna.gz`) bajo `genomes/<Especie>/`
     - parsea headers y cruza con `Supplememtary_Table_1.csv`
     - genera:
       - `samples_<Especie>.tsv`
       - `labels_<Especie>.tsv` (vacío si no hay matches, para robustez)
- **Outputs**:
  - `emit: samples` → `samples_*.tsv`
  - `emit: labels`  → `labels_*.tsv`
  - **publishDir**: `params.outdir` (por defecto `${projectDir}/outputs` salvo que lo cambies en `nextflow.config`).

### `MAKE_DB`
- **Input**:
       - canal de archivos `samples_<Especie>.tsv`
       - canal de archivos en carpeta genomes `<Especies>/*.fna`
- **Ejecución**:
    1. `make_db.sh` 
       - Lee entradas en archivos samples_<Especies>.tsv
       - localiza FASTA (`*.fna`) bajo `genomes/<Especie>/`
       - concatena los FASTA en un solo archivo ref_db.fsa
       - utiliza el comando `makeblastdb` de la librearía `blast` y genera:
         - `ref_db.fsa*`
- **Outputs**:
    - `emit: `database` → `ref_db.fsa*`
    - **publishDir**: `params.outdir` (por defecto `${projectDir}/results` salvo que lo cambies en `nextflow.config`).

### `RUN_BLAST`
- **Input**:
       - canal de archivos en carpeta genomes `<Especies>/*.fna`, solo las especificadas en canal de especies
       - canal de archivos database `ref_db.fsa*`
- **Ejecución**:
    1. `run_blast.sh` 
       - recibe un archivo FASTA para realizar alineamiento
       - utiliza comando `blastn` de librería `blast` para alineamientos
       - genera:
	 - archivo .xml con formato blast con resultados
       - En caso de ya existir un archivo con el mismo nombre (para evitar ejecutar el alineamiento nuevamente), se genera un archivo vacío `temp.xml`.
- **Outputs**:
    - `emit: `results_xml` → `*.xml`
    - **publishDir**: `params.blast` (por defecto `${params.outdir/blast_results` salvo que lo cambies en `nextflow.config`).

### `EXTRACT_HSPS`
- **Input**:
       - canal de archivos resultados blast `*.xml`
- **Ejecución**:
    1. `parse_hsps.py` 
       - recibe un archivo de resultados de blast .xml
       - utiliza `Blast.parse` de la librería `biopython` para lectura de los archivos
       - extrae información necesario para cálculos posteriores en arreglos `numpy`
       - genera:
	 - `labels.npy` archivo con los identificadores de cada secuencia para cada alineamiento
	 - `hsps.npy` archivos con información de alineamientos
       - En caso de ya existir un archivo con el mismo nombre (para evitar ejecutar el la extracción nuevamente), se genera un archivo vacío `temp.npy`.
- **Outputs**:
    - `emit: 
       - `npy_results` → `*.npy`
    - **publishDir**: `params.hsps` (por defecto `${params.outdir}/hsps/` salvo que lo cambies en `nextflow.config`).

### `CALC_DISTANCES`
- **Input**:
       - canal de archivos resultados de extracción de hsps `*.npy`
- **Ejecución**:
    1. `calc_distances.py` 
       - recibe un archivos de numpy `labels.npy` y `hsps.npy` y cadena con números del 0 a 9
       - Los números especifican que fórmulas de distancias a utilizar e.g. "0,2,6" -> Calcular distancias 
       - Las fómulas de distancias se especifican con el parámetro `dis_formula` en `nextflow.config`
       - Extra información de `hsps.npy` para realizar los cálculos y la información de `labels.npy` para buscar alinemiento inverso, es decir, seq1-v-seq2, el inverso es seq2-v-seq1. 
       - genera:
         - archivo unique_labels.npy.  
         - archivo distances_matrix.npy de forma (N,N,d), donde N corresponde al número de labels, y d esta dado por el número de fórmulas de distancias especificados.
- **Outputs**:
    - `emit: 
       - `distance_npy` → `*.npy`
    - **publishDir**: `params.distances` (por defecto `${params.outdir}/distances/` salvo que lo cambies en `nextflow.config`).

### `RUN_HEATMAPS`
- **Input**:
       - canal de archivos `*.npy` DESDE `CALC_DISTANCES`.
- **Ejecución**:
    1. `heatmaps.py` 
       - Recibe la matriz de distancias y las etiquetas (`distances_matrix.npy` y `unique_labels.npy`)
       - Genera un mapa de calor (heatmap) en formato .png para cada una de las fórmulas de distancia calculadas.        
- **Outputs**:
    - `emit` → `*.png` 
    - **publishDir**: `params.heatmaps` (por defecto `${params.outdir}/heatmaps/`).

### `RUN CORRELACION`
- **Input**:
      - canal de archivos `*.npy` desde `CALC_DISTANCES`.
- **Ejecución**:
    1. `correlacion_Ds.py`
      - Recibe la matriz de distancias.
      - Realiza un Test de Mantel para comparar estadísticamente todas las matrices de distancia entre sí.
      - Genera un único mapa de calor de correlaciones que resume los resultados.
- **Outputs**:
    - `emit:` → `*.png`
    - **publishDir**: `params.correlation`(por defecto `${params.outdir}/correlation/`).

---

**Parámetros clave**

| Parámetro          | Tipo     | Requerido | Descripción                                               |
|--------------------|----------|-----------|-----------------------------------------------------------|
| `--species`        | string   | Sí*       | Nombre de especie. Ej.: `"Mycobacterium intracellulare"` |
| `--species_list`   | archivo  | Sí*       | Archivo con una especie por línea                         |
| `--outdir`         | carpeta  | No        | Carpeta donde publicar TSVs (`publishDir`)                |

\* Usa **uno u otro** (`--species` **o** `--species_list`).

---

## Uso

### 1) Modo scripts (standalone)

**Descargar por especie**
```bash
# Con variable REMOTE_USER
REMOTE_USER=otro_usuario scripts/download_by_species.sh "s__Streptococcus suis" genomes/Streptococcus_suis

# Con usuario como argumento
scripts/download_by_species.sh "s__Streptococcus suis" otro_usuario
```

**Procesar metadatos**
```bash
# Con espacios
python scripts/parse_metadata.py --species "Mycobacterium intracellulare"
# Con guión bajo
python scripts/parse_metadata.py "Mycobacterium_intracellulare"
# Con prefijo s__
python scripts/parse_metadata.py --species "s__Mycobacterium intracellulare"
```

Genera:
- `samples_<Especie>.tsv`
- `labels_<Especie>.tsv`

Por defecto los deja en `outputs/` (o en la ruta que pases con `--outdir`).

---

### 2) Modo Nextflow (pipeline)

**Ejecutar una sola especie**
```bash
# Publica en outputs/
nextflow run . --species "Mycobacterium intracellulare" --outdir outputs

# O publica en results/
nextflow run . --species "Mycobacterium intracellulare" --outdir results
```

**Varias especies desde archivo**
```bash
cat > species.txt <<EOF
Mycobacterium intracellulare
Klebsiella aerogenes
EOF

nextflow run . --species_list species.txt --outdir outputs
```

**Reportes (opcionales) en carpeta `reports/`**
```bash
mkdir -p reports
nextflow run . --species "Klebsiella aerogenes" \
  -with-report   reports/nf-report.html \
  -with-timeline reports/nf-timeline.html \
  -with-dag      reports/nf-dag.svg \
  -with-trace    reports/nf-trace.txt
```

**Log de Nextflow en `reports/` (opcional)**
```bash
mkdir -p reports
export NXF_LOG_FILE=reports/nextflow.log
nextflow run . --species "Mycobacterium intracellulare"
```

---

## Limpieza

Incluimos un script de limpieza:

```bash
# Vista previa (no borra)
bash scripts/clean.sh --dry-run

# Limpieza completa
bash scripts/clean.sh -y

# Conservar algunas carpetas
bash scripts/clean.sh -y --keep-outputs --keep-reports
```

Lo que borra:
- cache y work de Nextflow: `work/`, `.nextflow*`
- artefactos sueltos: `report-*.html`, `timeline-*.html`, `nf-*.html`, `nf-*.svg`, `flow.svg`, `dag.svg`, `trace.txt`
- TSV sueltos en la raíz: `samples_*.tsv`, `labels_*.tsv`
- carpetas de publicación (`outputs/`, `results/`, `reports/`) salvo que las conserves

---

## Troubleshooting (FAQ)

- **`Permission denied` al ejecutar `.command.sh`**  
  Quita overrides de shell en `nextflow.config`. No uses:
  ```groovy
  process.shell = ['/bin/bash','-euo','pipefail','-c']
  ```
  Deja el default de Nextflow o usa:
  ```groovy
  process.shell = ['/bin/bash','-lc']
  ```

- **Los TSV aparecen en la raíz y no en `--outdir`**  
  Asegúrate de que `scripts/parse_metadata.sh` **no** haga `cd` global fuera del workdir y que el proceso pase:
  ```bash
  OUTDIR="$PWD" scripts/parse_metadata.sh "<Especie>"
  ```
  (En este repo ya está resuelto.)

- **No veo reportes en `reports/`**  
  Debes activarlos con `-with-*` o fijar `enabled = true` en `nextflow.config` y especificar `file = "${params.reports}/..."`.

---

## Estándares recomendados del repo (GitHub)

- **`.gitignore`** (sugerencia):
  ```
  work/
  outputs/
  results/
  reports/
  .nextflow*
  report-*.html
  timeline-*.html
  nf-*.html
  nf-*.svg
  flow.svg
  dag.svg
  trace.txt
  samples_*.tsv
  labels_*.tsv
  .venv/
  __pycache__/
  ```
- **LICENSE**: agrega una licencia (MIT o la que prefieras).
- **CITATION.cff** (opcional): cómo citar este repositorio.
- **CONTRIBUTING.md** (opcional): guía para contribuciones.
- **Issues/PR templates** (opcional): `.github/ISSUE_TEMPLATE/` y `.github/PULL_REQUEST_TEMPLATE.md`.
- **Releases** con tags (`v0.1.0`, `v0.2.0`, …).

---

## Especies por estudiante

- **Lenin Ruiz:** s__Enterobacter hoffmannii, s__Aeromonas veronii, s__Aeromonas caviae, s__Limosilactobacillus fermentum
- **Juan Cantos:** s__Lacticaseibacillus rhamnosus, s__Burkholderia glumae, s__Rickettsia rickettsii, s__Staphylococcus pseudintermedius
- **Felipe Espinoza:** s__Mycobacterium intracellulare, s__Enterobacter hormaechei_B, s__Burkholderia multivorans, s__Clostridium_F botulinum
- **Osvaldo Delgado:** s__Bifidobacterium longum, s__Escherichia coli, s__Bacillus_A cereus, s__Xylella fastidiosa

---

## Ejemplos rápidos (scripts)

```bash
python scripts/parse_metadata.py --species "Klebsiella aerogenes"
# -> genera samples_*.tsv y labels_*.tsv en outputs/ (o --outdir)

python scripts/parse_metadata.py "Mycobacterium_intracellulare"
python scripts/parse_metadata.py --species "s__Mycobacterium intracellulare"
```

---

## Prueba en limpio Nextflow

```bash
nextflow clean -f || true
rm -rf work .nextflow
nextflow run . --species "Klebsiella aerogenes" --outdir outputs
```

---

### Changelog
- **(2025-08-20)**
  - Integración de los procesos `RUN_HEATMAPS` y `RUN_CORRELACION`.
  - Ajustes en los scripts de Python para aceptar argumentos desde la línea de comandos.
  - Actualización de la gestión de dependencias de Python dentro del ambiente conda.

- **(2025-08-09)**
  - Integración **Nextflow (DSL2)** de los procesos `MAKE_DB`, `RUN_BLAST`,`EXTRACT_HSPS` y `CALC_DISTANCES`.
  - Carpeta de archivos para nuevos procesos en scripts/DistExtract.
  - Modificación de archivo main.df para implementación de pipeline.
  - Parámetros agregados en archivo `nextflow.config` para nuevos procesos.
