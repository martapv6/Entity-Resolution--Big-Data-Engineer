import pandas as pd

df=pd.read_parquet(r"D:\cv\task_ver\veridion_entity_resolution_challenge.snappy.parquet")
#print(df.head())

print(df.shape)

for col in df:
    print(col)


for col in df:
    unique_count=df[col].nunique(dropna=True)
    #print(f"{col}: {unique_count} valori unice")



for col in df.columns:
    unique_count = df[col].nunique(dropna=True)
    total_count = len(df[col])
    if unique_count < total_count:   # exista duplicate
      # print(f"Coloana {col} are duplicate (valori unice: {unique_count}/{total_count})")
       ok=1



#toate valorile duplicat dar care nu sunt null
for col in df.columns:
    vals=df[col].dropna()  # eliminam valorile nule
    duplicates=vals[vals.duplicated(keep=False)]
    if not duplicates.empty:
       # print(f"\nColoana {col} are duplicate:")
       # print(duplicates.value_counts())
       ok=1
