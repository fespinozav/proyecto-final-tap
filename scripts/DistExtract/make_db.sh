#Make database for blast

samples_file=$1
genomes_dir=$2



for file in $samples_file;do
    dir_base=`echo $file | cut -f 2,3 -d "_" | cut -f 1 -d "."`
    {
        read   
    while IFS=, read name;do
        id=`echo $name | cut -f 1 -d " "`
        cat $genomes_dir/$dir_base/$id >> ref_db.fsa
        
    done 
    } < $file
done


makeblastdb -in ref_db.fsa -dbtype nucl -parse_seqids
