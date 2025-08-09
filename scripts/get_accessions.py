# get_accessions.py
import pandas as pd
import re
import sys

csv_path = "Supplememtary_Table_1.csv"

if len(sys.argv) < 2:
    print("Usage: get_accessions.py <species>", file=sys.stderr)
    sys.exit(1)

# Normalize target: strip, lowercase, remove leading 's__', convert _ to space, collapse spaces
raw = sys.argv[1].strip()
norm = raw
if norm.lower().startswith("s__"):
    norm = norm[3:]
norm = norm.replace("_", " ")
norm = re.sub(r"\s+", " ", norm).strip().lower()

# Load CSV
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"ERROR: CSV not found: {csv_path}", file=sys.stderr)
    sys.exit(2)

if "species" not in df.columns or "accession" not in df.columns:
    print("ERROR: CSV must have 'species' and 'accession' columns", file=sys.stderr)
    sys.exit(3)

# Normalize species column similarly
sp = df["species"].astype(str)
sp = sp.str.replace(r"^\s*s__","", regex=True)
sp = sp.str.replace("_", " ", regex=False)
sp = sp.str.replace(r"\s+", " ", regex=True).str.strip().str.lower()

matches = df.loc[sp == norm, "accession"].astype(str).str.strip()
matches = matches[matches.ne("")].drop_duplicates()

for acc in matches:
    print(acc)