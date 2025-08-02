# get_accessions.py
import pandas as pd
import sys

csv_path = "Supplememtary_Table_1.csv"
target_species = sys.argv[1].strip()

df = pd.read_csv(csv_path)
matches = df[df["species"] == target_species]

accessions = matches["accession"].unique()
for acc in accessions:
    print(acc)