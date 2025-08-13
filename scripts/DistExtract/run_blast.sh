
dir="/home/jseba/Documents/UTEM/semester_3/tap/proyecto_final/proyectoTAP"
outdir="blast_results"

sample_file=$1
database_file=$3
outdir=$2
db=`echo $database_file | cut -d " " -f 1`
base=`basename -s .fna $sample_file`


# echo $sample_file $database_file/ref_db.fsa

#Make a blast for all the FASTA files in a directory
#Ouput.xml results to xml directory

# for file in $(ls $dir/*.fna);do
#     name=`basename -s .fna $file`
#     echo "$name"


name=`basename -s .fna $sample_file`
    echo "$outdir/$name.xml"
    if [ -f "$outdir/$name.xml"  ];then
        echo "File exists";
        touch temp.xml
    else
        echo "File doesn´t exist";
        blastn -db $db -query $sample_file -out $base.xml -outfmt 5

fi

# done