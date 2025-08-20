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
        path "*.npy"
        
    script:
    """
    python3 "${projectDir}/scripts/DistExtract/calc_distances.py" "${npy_results}" ${params.dis_formula}

    """
}

process RUN_HEATMAPS {
    label 'analysis'
    publishDir ( params.heatmaps ?: "${projectDir}/outputs/heatmaps" ), mode: 'copy', overwrite: true
    input:
        path distances_output

    output:
        path "*.png"

    script:
    """
    python3 "${projectDir}/scripts/DistExtract/heatmaps.py" "${distances_output[0]}" "${distances_output[1]}" .
    """
}

process RUN_CORRELACION {
    label 'analysis'
    publishDir ( params.correlation ?: "${projectDir}/outputs/correlation" ), mode: 'copy', overwrite: true
    input:
        path distances_output

    output:
        path "*.png"

    script:
    """
    pip install scikit-bio
    python3 "${projectDir}/scripts/DistExtract/correlacion_Ds.py" "${distances_output[0]}" .
    """
}