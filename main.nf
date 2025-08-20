nextflow.enable.dsl=2

// ---------------- Módulos ----------------
include { PARSE_METADATA } from './modules/local/parse_metadata.nf'
include { RUN_BLAST } from './modules/local/blast.nf'
include { MAKE_DB } from './modules/local/blast.nf'
include { EXTRACT_HSPS } from './modules/local/distances.nf'
include { CALC_DISTANCES } from './modules/local/distances.nf'
include { RUN_HEATMAPS } from './modules/local/distances.nf'
include { RUN_CORRELACION } from './modules/local/distances.nf'


// ---------------- Defaults para params (evita WARN) ----------------
if( !params.containsKey('species') )      params.species = null
if( !params.containsKey('species_list') ) params.species_list = null

// ---------------- Entradas ----------------
// Soporta: --species "Genus species"  o  --species_list <archivo>

def speciesArg = params.species
def speciesListFile = params.species_list

def ch_species

if (speciesListFile) {
  ch_species = Channel
    .fromPath(speciesListFile, checkIfExists: true)
    .splitText()
    .map { it.trim() }
    .filter { it }
}
else if (speciesArg) {
  ch_species = Channel.of(speciesArg)
}
else {
  error "Debe proporcionar --species 'Genus species' o --species_list <archivo>"
}

// ---------------- Workflow ----------------
workflow {
  main:
    samples_out = PARSE_METADATA( ch_species )
    database=MAKE_DB(samples_out.samples.collect(),params.genomes)
    file_channel = ch_species.map { species ->
    def dir_name = species.replace(' ', '_')
    files("${params.genomes}/${dir_name}/*.fna")
    }.flatten()
    blast_results=RUN_BLAST(file_channel,database)
    // blast_results = Channel.fromPath("${params.blast}/*.xml") //To run on the files, not on the output of channel
    npy_results=EXTRACT_HSPS(blast_results)
    distances_out=CALC_DISTANCES(npy_results.collect())
    RUN_HEATMAPS(distances_out)
    RUN_CORRELACION(distances_out)
}