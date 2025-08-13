process RUN_BLAST {
    label 'blast' 
    publishDir ( params.blast ?: "${projectDir}/outputs/" ), mode: 'copy', overwrite: true
    input:
        path sample
        path database
        
    output:
        // stdout
        path "*.xml", emit: results_xml
        
  
    script:
    """

    bash "${projectDir}/scripts/DistExtract/run_blast.sh" ${sample} ${params.blast} ${database}
    """
}

process MAKE_DB {
    label 'blast' 
    publishDir ( params.outdir ?: "${projectDir}/outputs" ), mode: 'copy', overwrite: true
    input:
        path samples
        path genomes
    output:
        path "ref_db.fsa*", emit: database
        
    script:
    """
    echo ${samples}
    bash "${projectDir}/scripts/DistExtract/make_db.sh" "${samples}" "${genomes}"

    """
}