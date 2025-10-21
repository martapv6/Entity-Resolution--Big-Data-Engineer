import re
try:
    import numpy as np
except Exception:
    import sys
    import subprocess
    import importlib
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    np = importlib.import_module("numpy")
from rapidfuzz import fuzz, process
import pandas as pd

df=pd.read_parquet(r"D:\cv\task_ver\veridion_entity_resolution_challenge.snappy.parquet")
#normalizez numele
def normalize_name(name):
    if pd.isna(name):
        return None
    name=name.lower()
    name=re.sub(r'[^a-z0-9]+', ' ', name)  #pastrez litere si cifre
    name=re.sub(r'\b(inc|ltd|limited|llc|l\.?l\.?c|corp|corporation|co|company|gmbh|srl|s\.?r\.?l|sa|s\.?a)\b','',name)
    name=re.sub(r'\s+',' ', name).strip()
    return name or None

df["name_norm"]=df["company_name"].map(normalize_name) if "company_name" in df.columns else None

#blocking key: (tara si + prima litera din name_norm)
country=df["main_country_code"].fillna("").astype(str) if "main_country_code" in df.columns else ""
first_char=df["name_norm"].fillna("").str[:1]
df["block_key"]=(country + "|"+first_char).astype(str)

#tin cont si de website_domain cand exista
#tot ce are același domeniu => acelasi grup
if "website_domain" in df.columns:
    dom=df["website_domain"].astype("string")
    has_dom=dom.notna() & dom.ne("")
else:
    has_dom=pd.Series(False, index=df.index)

#pornim cu group ids pe domeniu sau NaN daca nu are
df["fuzzy_group_id"] = np.nan
df.loc[has_dom, "fuzzy_group_id"] = dom[has_dom].factorize()[0]

#fuzzy doar pe rândurile fara domeniu ca sa nu stric grupurile bune
mask=~has_dom & df["name_norm"].notna() & df["name_norm"].ne("")
todo=df[mask].copy()

#parametri reglabil/aici hardcodati
THRESHOLD=92           
MAX_BLOCK_SIZE=2000     #securitate pentru blocuri uriase

#union-find pentru clusterizare
class DSU:
    def __init__(self, n):
        self.p=list(range(n))
        self.r=[0]*n
    def find(self,x):
        while self.p[x]!=x:
            self.p[x]=self.p[self.p[x]]
            x=self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb: return
        if self.r[ra] < self.r[rb]:
            self.p[ra] = rb
        elif self.r[ra] > self.r[rb]:
            self.p[rb] = ra
        else:
            self.p[rb] = ra
            self.r[ra] += 1

#parcurg blocurile si leg perechile similare
from collections import defaultdict
group_counter=0

#pastrez mapping index->id
assigned_ids = {}

for bk,block in todo.groupby("block_key"):
    idx=block.index.to_list()
    names=block["name_norm"].to_list()
    m=len(idx)
    if m==0:
        continue
    if m>MAX_BLOCK_SIZE:
        labels=pd.factorize(block["name_norm"])[0]
        for lab,sub in block.groupby(labels):
            block_gid=group_counter
            group_counter+=1
            for i in sub.index:
                assigned_ids[i]=block_gid
        continue

    dsu=DSU(m)
    #folosesc cdist pentru scoruri pairwise pe token_set_ratio
    #(rapidfuzz.process.cdist returneaza o matrice de scoruri)
    scores=process.cdist(
        names, names,
        scorer=fuzz.token_set_ratio,
        score_cutoff=THRESHOLD,
        workers=-1
    )
    #leg muchii unde scor >= THRESHOLD
    #scores este list-of-lists de (j,score) pentru fiecare i (sparse)
    # calculează scorurile pairwise
    scores = process.cdist(
        names, names,
        scorer=fuzz.token_set_ratio,
        score_cutoff=THRESHOLD,
        workers=-1
    )

    if m <= 1:
        pass 

    elif isinstance(scores, list):
        for i, row in enumerate(scores):
            if isinstance(row, (float, int, np.floating)):
                continue
            for j, sc in row:
                if j <= i:
                    continue
                dsu.union(i, j)

    else:
        for i in range(m):
            for j in range(i + 1, m):
                sc = float(scores[i, j])
                if sc >= THRESHOLD:
                    dsu.union(i, j)


    #atribui id per componenta
    roots = [dsu.find(i) for i in range(m)]
    root_to_gid={}
    for i_root in roots:
        if i_root not in root_to_gid:
            root_to_gid[i_root]=group_counter
            group_counter+=1
    for local_i,global_idx in enumerate(idx):
        assigned_ids[global_idx]=root_to_gid[roots[local_i]]

#rezultate in coloana fuzzy_group_id 
for i,gid in assigned_ids.items():
    if pd.isna(df.at[i, "fuzzy_group_id"]):
        df.at[i,"fuzzy_group_id"] = gid

#modific NaN 
nan_left = df["fuzzy_group_id"].isna()
if nan_left.any():
    start = (pd.Series(df["fuzzy_group_id"]).dropna().max() or -1) + 1
    df.loc[nan_left,"fuzzy_group_id"]=np.arange(start, start + nan_left.sum())

df["fuzzy_group_id"]=df["fuzzy_group_id"].astype(int)

#aleg reprezentantul per grup pe baza unicity_score 
if "unicity_score" in df.columns:
    fuzzy_unique=(
        df.sort_values("unicity_score",ascending=False)
          .groupby("fuzzy_group_id",as_index=False)
          .head(1)
          .reset_index(drop=True)
    )
else:
    fuzzy_unique=(
        df.groupby("fuzzy_group_id", as_index=False)
          .head(1)
          .reset_index(drop=True)
    )

df.to_parquet(r"D:\cv\task_ver\veridion_with_fuzzy_groups.parquet", engine="pyarrow", compression="snappy", index=False)
fuzzy_unique.to_parquet(r"D:\cv\task_ver\veridion_fuzzy_unique.parquet", engine="pyarrow", compression="snappy", index=False)
