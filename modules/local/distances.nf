process EXTRACT_HSPS {
    label 'blast' 
    publishDir ( params.hsps ?: "${projectDir}/outputs/" ), mode: 'copy', overwrite: true
    input:
        path sample
        
    output:
        // stdout
        path "*.npy", emit: npy_results
        
  
    script:
    """
    mkdir -p ${params.hsps}
    python3 "${projectDir}/scripts/DistExtract/parse_hsps.py" ${sample} ${params.hsps}
    """
}


process CALC_DISTANCES {
    label 'blast' 
    publishDir ( params.distance ?: "${projectDir}/outputs/" ), mode: 'copy', overwrite: true
    input:
        path npy_results

        
    output:
        // stdout
        path "*.npy", emit: distances_npy
        
  
    script:
    """

    python3 "${projectDir}/scripts/DistExtract/calc_distances.py" ${params.hsps} ${params.dis_formula}
    """
}
