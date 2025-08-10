# Proyecto Final TAP

## Descripción

Este proyecto corresponde al trabajo final para la asignatura **Técnicas de la Programación Avanzada (TAP)**. Su objetivo es **facilitar la descarga y el procesamiento de archivos genómicos filtrados por especie**, además del **análisis de metadatos** asociados.

Incluye dos formas de uso:

- **Modo scripts**: `scripts/download_by_species.sh` y `scripts/parse_metadata.py`.
- **Modo pipeline** con **Nextflow (DSL2)**: proceso `PARSE_METADATA` que orquesta `parse_metadata.sh` → `parse_metadata.py` y publica **TSVs**.

---

## Requisitos

- **Nextflow** ≥ 24.10.1
- **Bash** (macOS / Linux)
- **Python 3.8+** con:
  - `pandas`
  - `biopython`
- Acceso a la carpeta `genomes/` con subcarpetas por especie (p.ej. `Mycobacterium_intracellulare/`).

> En macOS sin contenedor verás `WARN: Task runtime metrics are not reported…` (es esperado).

Instalación rápida de dependencias Python (opcional):

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas biopython
```

---

## Estructura del proyecto (resumen)

```
.
├── genomes/                       # Datos locales por especie
├── modules/local/parse_metadata.nf# Proceso Nextflow PARSE_METADATA
├── scripts/                       # Wrappers y utilidades
│   ├── download_by_species.sh
│   ├── parse_metadata.py
│   └── parse_metadata.sh
├── nextflow.config                # Config del pipeline
├── outputs/                       # Publicación por defecto (ver params.outdir)
├── reports/                       # Reportes si activas -with-*
└── README.md
```

---

## Flujo con Nextflow

El pipeline expone un **único proceso**:

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

- **Lenin Ruiz:** Enterobacter roggenkampii, Aeromonas veronii, Aeromonas caviae, Limosilactobacillus fermentum
- **Juan Cantos:** Lacticaseibacillus rhamnosus, Burkholderia glumae, Rickettsia rickettsii, Staphylococcus pseudintermedius
- **Felipe Espinoza:** Mycobacterium intracellulare, Klebsiella aerogenes, Burkholderia multivorans, Clostridium_F botulinum
- **Osvaldo Delgado:** Bifidobacterium longum, Escherichia fergusonii, Bacillus_A cereus, Xylella fastidiosa

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

### Changelog (2025-08-09)
- Integración **Nextflow (DSL2)** del proceso `PARSE_METADATA`.
- Escritorio robusto de salidas: `OUTDIR="$PWD"` → TSV siempre en el workdir del task.
- Publicación con `publishDir (params.outdir)` y soporte de `--outdir`.
- Limpieza con `scripts/clean.sh`.
- Rutas de reportes en `reports/` cuando se usan `-with-*`.