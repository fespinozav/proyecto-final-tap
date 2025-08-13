
sample_file=$1
database_file=$3
outdir=$2
db=`echo $database_file | cut -d " " -f 1`
base=`basename -s .fna $sample_file`

#Make a blast for a single FASTA file
#Ouput.xml results to xml directory
name=`basename -s .fna $sample_file`
    echo "$outdir/$name.xml"
    if [ -f "$outdir/$name.xml"  ];then
        echo "File exists";
        touch temp.xml
    else
        echo "File doesn´t exist";
        blastn -db $db -query $sample_file -out $base.xml -outfmt 5

fi
