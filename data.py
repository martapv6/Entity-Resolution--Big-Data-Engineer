import pandas as pd
import json

df=pd.read_parquet(r"D:\cv\task_ver\veridion_entity_resolution_challenge.snappy.parquet")

output = {}

for col in df.columns:
    vals=df[col].dropna() #nu tin cont de null
    duplicates=vals[vals.duplicated(keep=False)]
    if not duplicates.empty:
        output[col]=duplicates.value_counts().to_dict()

with open(r"D:\cv\task_ver\date.json", "w", encoding="utf-8") as f:
    json.dump(output, f,indent=4,ensure_ascii=False)

