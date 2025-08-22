process KMER {
    label 'kmer'  
    publishDir ( params.kmer_results ?: "${projectDir}/outputs/" ), mode: 'copy', overwrite: true
    input:
        path dir
        
    output:
        path "*.tsv", emit: kmer_matrix
        

        
    script:
    """
    python3 "${projectDir}/scripts/ofrecuencias_kmer.py" --entrada "${params.genomes}/${dir}" --glob "*.fna" --salida "${dir}_frecuencia.tsv" --long_kmer ${params.kmer} --max_cpu 2
    """
}
