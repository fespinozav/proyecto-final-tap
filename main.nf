nextflow.enable.dsl=2
// Evita warnings si el parámetro no viene definido
if( !params.containsKey('species_file') ) params.species_file = null

// ---------------- Params ----------------

def speciesParam      = params.get('species')
def speciesFileParam  = params.get('species_file')
params.dest_base     = 'genomes'    // base donde se crean carpetas de especie

// SSH / cluster
params.remote_user   = 'fespinoza'
params.remote_host   = 'faraday.utem.cl'
params.remote_dir    = '/home/amoya/Data_forTap/selected_Genomes'

// ---------------- Prompt interactivo ----------------
String asked_species = null
if( !speciesParam && !speciesFileParam ){
    def console = System.console()
    if( console ){
        asked_species = console.readLine('🧬 Especie (p.ej. "Mycobacterium intracellulare"): ')?.trim()
    }
    else {
        print '🧬 Especie (p.ej. "Mycobacterium intracellulare"): '
        asked_species = new java.io.BufferedReader(new java.io.InputStreamReader(System.in)).readLine()?.trim()
    }
    if( !asked_species ){
        exit 1, 'Debe especificar una especie con --species, --species_file, o responder al prompt.'
    }
}
def target_species = speciesParam ?: asked_species

// ---------------- Canales ----------------
def species_ch = speciesFileParam ?
    Channel
        .fromPath(speciesFileParam)
        .splitText()
        .map{ it?.trim() }
        .filter{ it }
        .unique()
  :
    Channel.of(target_species)

// Canales para archivos locales requeridos por el proceso
def dl_script_ch = Channel.fromPath('scripts/download_by_species.sh')
def acc_py_ch    = Channel.fromPath('scripts/get_accessions.py')
def supp_csv_ch  = Channel.fromPath('Supplememtary_Table_1.csv')

// ---------------- Proceso: Descarga de archivos por especie ----------------
process DOWNLOAD_BY_SPECIES {
    tag { sp }
    publishDir "${params.dest_base}", mode: 'copy', overwrite: true

    input:
    val sp
    path dl_script
    path acc_py
    path supp_csv

    """
    set -euo pipefail
    set -x   # <<< traza visible en .command.err

    echo "[NF] PRE_STAGE start"

    # Opciones SSH NO interactivas y con timeout (para evitar bloqueos sin TTY)
    SSH_OPTS="-o BatchMode=yes -o PasswordAuthentication=no -o PubkeyAuthentication=yes \
              -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes \
              -o ConnectTimeout=8 -o ServerAliveInterval=10 -o ServerAliveCountMax=2 -o LogLevel=ERROR"

    # --- STAGING VALIDATION ---
    if [[ ! -s "${dl_script}" ]]; then echo "[NF] missing dl_script" ; exit 2 ; fi
    if [[ ! -s "${acc_py}"    ]]; then echo "[NF] missing acc_py"    ; exit 2 ; fi
    if [[ ! -s "${supp_csv}"  ]]; then echo "[NF] missing supp_csv"  ; exit 2 ; fi

    mkdir -p scripts bin
    cp "${dl_script}" scripts/download_by_species.sh
    cp "${acc_py}"    scripts/get_accessions.py
    cp "${supp_csv}"  ./Supplememtary_Table_1.csv
    chmod +x scripts/download_by_species.sh

    # Wrapper ssh no-interactivo en PATH
    cat > bin/ssh <<'EOS'
    #!/usr/bin/env bash
    exec /usr/bin/ssh -o BatchMode=yes -o PasswordAuthentication=no -o PubkeyAuthentication=yes \
                      -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes \
                      -o ConnectTimeout=8 -o ServerAliveInterval=10 -o ServerAliveCountMax=2 -o LogLevel=ERROR "\$@"
    EOS
    chmod +x bin/ssh
    export PATH="\$PWD/bin:\$PATH"
    export RSYNC_RSH="ssh"

    echo "[NF] PRE_STAGE end"

    # --- PREFLIGHT con timeout duro y logs PRE/POST ---
    echo "[NF] PREFLIGHT start"
    if ! timeout 12s ssh \${SSH_OPTS} "${params.remote_user}@${params.remote_host}" true ; then
      echo "[NF] PREFLIGHT fail: sin acceso SSH no-interactivo a ${params.remote_user}@${params.remote_host}"
      echo "[NF] tips: eval \"\$(ssh-agent -s)\" && ssh-add ~/.ssh/id_ed25519 && ssh -o BatchMode=yes ${params.remote_user}@${params.remote_host} true"
      exit 1
    fi
    echo "[NF] PREFLIGHT ok"

    # --- MONITOR DE PROGRESO ---
    mkdir -p "${params.dest_base}"
    (
      while true; do
        cnt=\$(find "${params.dest_base}" -type f -name '*.fna' 2>/dev/null | wc -l || true)
        echo "[NF] PROGRESS .fna: \$cnt"
        sleep 5
      done
    ) &
    mon_pid=\$!

    echo "[NF] RUN start: ${sp}"
    set +e
    # timeout global de 30m (ajústalo si necesitas más)
    timeout 30m stdbuf -oL -eL scripts/download_by_species.sh --debug "${sp}" "${params.dest_base}" | tee -a .nf.out
    rc=\${PIPESTATUS[0]}
    set -e
    echo "[NF] RUN end rc=$rc"

    kill -TERM "\$mon_pid" 2>/dev/null || true
    wait "\$mon_pid" 2>/dev/null || true

    exit "$rc"
    """
}

// ---------------- Workflow ----------------
workflow {
  main:
    DOWNLOAD_BY_SPECIES(species_ch, dl_script_ch, acc_py_ch, supp_csv_ch)
}
