from Bio import Blast
# from Bio.Blast import NCBIXML
import numpy as np
import os
import sys


# print(f"Query,Target,iXY,hXY,lamXY,minXY")

def extractH(blast_records):
    """
    Function to parse information from blast xml file.
    Input: Blast record from Biopython
    Output: Numpy array with 
        # X = Query name
        # Y = Target name
        # iXY := sum of identical base pairs over all HSPs
        # hXY = total length of all HSPs
        # lamXY = sum of both genomes’ lengths
        # minXY = twice the length of the smallest genome
    """
    temp=[]
    for blast_record in blast_records:
        
        for hit in blast_record:
            # hit=blast_record[0]
            iXY=0
            hXY=0
            for alignment in hit:
                iXY+=alignment.annotations["identity"]
                hXY+=alignment.length
            
            lamXY=alignment.query.__len__() + alignment.target.__len__()
            minXY = min(alignment.query.__len__(),alignment.target.__len__())*2
            query_name=blast_record.query.description.split(".")[0] # Temporary naming parsing solution
            target_name=alignment.target.name

            temp.append([f"{query_name}-v-{target_name}",iXY,hXY,lamXY,minXY])
            # print(f"{query_name}")
            # print(f"{query_name},{target_name},{iXY},{hXY},{lamXY},{minXY}")
        # fin_array.append(temp)
    return np.array(temp)
        # break




def multi_results_arr(dir):
    """
    Return a numpy array of all the blast records
    Input: Paht to directory with all the blast xml results.
    """
    temp=[]
    for result in os.listdir(dir):
        if result.endswith(".xml") and result != "temp.xml":
            # print(result)
            # result_stream = open(os.path.join(dir,result), "rb")
            # blast_record = Blast.read(result_stream)
            blast_record = Blast.parse(os.path.join(dir,result))
            # print(extractH(blast_record))
            temp.extend(extractH(blast_record))
    return np.array(temp)

def single_results_arr(result):
    """
    Return a numpy array of all the blast records
    Input: Paht to directory with all the blast xml results.
    """
    return np.array(extractH(Blast.parse(result)))



# # Various files
dir=sys.argv[1]
outdir=os.listdir(sys.argv[2])
if dir.endswith(".xml") and f"hsps_{dir.replace(".xml",".npy")}" not in outdir and dir != "temp.xml":
    #Single file
    if os.path.isfile(os.path.join(sys.argv[2],f"hsps_{dir.replace(".xml",".npy")}")):
        print("file exists peko")
    arr=single_results_arr(dir)
    np.save(f"labels_{dir.replace(".xml",".npy")}",arr[:,:1])
    np.save(f"hsps_{dir.replace(".xml",".npy")}",arr[:,1:])
elif os.path.isdir(os.path.dirname(dir)):
    arr=multi_results_arr(dir)
    np.save("labels.npy",arr[:,:1])
    np.save("hsps.npy",arr[:,1:])
else:
    with open("temp.npy", "a") as f:
        f.write("")


# blast_records=Blast.parse("/home/jseba/Documents/UTEM/semester_3/tap/proyecto_final/proyectoTAP/nextflow/scripts/2.DistExtract/blast_results/GCF_900116695.1_ASM90011669v1_genomic.xml")
# print(extractH(blast_records))




# TEST
# -----------------------------------------
# def extractH_test(blast_records):
#     """
#     Function to parse information from blast xml file.
#     Input: Blast record from Biopython
#     Output: Numpy array with 
#         # X = Query name
#         # Y = Target name
#         # iXY := sum of identical base pairs over all HSPs
#         # hXY = total length of all HSPs
#         # lamXY = sum of both genomes’ lengths
#         # minXY = twice the length of the smallest genome
#     """
#     temp=[]
#     for blast_record in blast_records:
        
#         for hit in blast_record:
#             # hit=blast_record[0]
#             iXY=0
#             hXY=0
#             for alignment in hit:
#                 iXY+=alignment.annotations["identity"]
#                 hXY+=alignment.length
            
#             lamXY=alignment.query.__len__() + alignment.target.__len__()
#             minXY = min(alignment.query.__len__(),alignment.target.__len__())*2
#             query_name=blast_record.query.description
#             target_name=alignment.target.name

#             temp.append([f"{query_name}-v-{target_name}",iXY,hXY,lamXY,minXY])
#             # print(f"{query_name}")
#         # fin_array.append(temp)
#     return np.array(temp)
#         # break


# temp=[]
# for result in os.listdir(dir):
#     if result.endswith(".xml"):
#         # print(result)
#         # result_stream = open(os.path.join(dir,result), "rb")
#         # blast_record = Blast.read(result_stream)
#         blast_record = Blast.parse(os.path.join(dir,result))
#         # print(extractH(blast_record))
#         temp.extend(extractH_test(blast_record))

# print(temp)


# for blast_record in blast_records:
#     for hit in blast_record:
#         for alignment in hit:
#             # if "ow" in alignment.target.name:
#                 query=blast_record.query.description.split(".")[0] # Temporary naming parsing solution
#                 target=alignment.target.name
#                 print(query)



# peko=arr[0]
# print(peko)
# print(type(peko))








