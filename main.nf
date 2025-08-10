nextflow.enable.dsl=2

// ---------------- Params ----------------
def speciesParam = params.get('species', null)
if( !speciesParam ){
  error 'Debes pasar --species "Genus species"'
}

// ---------------- Canales ----------------
def species_ch = Channel.of(speciesParam)

// ---------------- Módulos ----------------
include { PARSE_METADATA } from './modules/local/parse_metadata.nf'

// ---------------- Workflow ----------------
workflow {
  main:
    PARSE_METADATA( species_ch )
}