nextflow.enable.dsl=2

// ---------------- Módulos ----------------
include { PARSE_METADATA } from './modules/local/parse_metadata.nf'

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
    PARSE_METADATA( ch_species )
}