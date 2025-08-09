nextflow.enable.dsl=2

// ------------------
// Parámetros
// ------------------
params.genomes_dir  = params.genomes_dir ?: 'genomas'
params.species_list = params.species_list ?: ''   // Lista separada por comas
params.outdir       = params.outdir ?: 'results'

// ------------------
// Sólo módulo de DESCARGA
// ------------------
include { DOWNLOAD_SPECIES } from './modules/local/download_species.nf'

// ------------------
// Workflow principal (sólo descarga)
// ------------------
workflow {
  ch_species = params.species_list
      ? Channel.from( params.species_list.split(',').collect { it.trim() }.findAll { it } )
      : Channel.of('Mycobacterium intracellulare')

  // Paso único: descarga por especie
  DOWNLOAD_SPECIES( ch_species )
}