import pandas as pd

df=pd.read_parquet(r"D:\cv\task_ver\veridion_entity_resolution_challenge.snappy.parquet")

#cele 3 liste cu coloane dupa importanta
#sunt alese arbitrar
primary_cols = [
    "company_name",
    "company_legal_names",
    "company_commercial_names",
    "website_domain",
    "website_url",
    "primary_email",
    "emails",
    "primary_phone",
    "phone_numbers",
    "linkedin_url",
    "main_latitude",
    "main_longitude",
    "main_postcode",

]

secondary_cols = [
    "main_country_code",
    "main_country",
    "main_region",
    "main_city_district",
    "main_city",
    "main_street",
    "main_street_number",
    "main_address_raw_text",
    "locations",
    "num_locations",
    "tiktok_url",
    "youtube_url",
    "year_founded",
    "facebook_url",
    "twitter_url",
    "instagram_url",

]


context_cols = [
    "company_type",
    "lnk_year_founded",
    "short_description",
    "long_description",
    "business_tags",
    "business_model",
    "product_type",
    "naics_vertical",
    "naics_2022_primary_code",
    "naics_2022_primary_label",
    "naics_2022_secondary_codes",
    "naics_2022_secondary_labels",
    "main_business_category",
    "main_industry",
    "main_sector",
    "revenue",
    "revenue_type",
    "employee_count",
    "employee_count_type",
    "alexa_rank",
    "sics_codified_industry",
    "sics_codified_industry_code",
    "sics_codified_subsector",
    "sics_codified_subsector_code",
    "sics_codified_sector",
    "sics_codified_sector_code",
    "sic_codes",
    "sic_labels",
    "isic_v4_codes",
    "isic_v4_labels",
    "nace_rev2_codes",
    "nace_rev2_labels",
    "website_tld",
    "website_language_code",
    "created_at",
    "last_updated_at",
    "website_number_of_pages",
    "generated_description",
    "generated_business_tags",
    "status",
    "domains",
    "all_domains",
    "inbound_links_count",
]



#o a 2 a verificare pentru ca le am hardcodat mai sus
primary_cols=[c for c in primary_cols   if c in df.columns]
secondary_cols=[c for c in secondary_cols if c in df.columns]
context_cols=[c for c in context_cols   if c in df.columns]

all_cols=primary_cols+secondary_cols+context_cols

#functie pentru scor unicitate pe o coloana
#daca val de pe coloana respectiva este nula socrul etse 0,
#altfel cu cat este mai rara scorul este mai bun si daca apare o singura data scorul este 1/1=1
def column_uniqueness_score(series):
    freq=series.value_counts(dropna=True)
    s=series.map(lambda x: 0 if pd.isna(x) else 1.0/float(freq.get(x, 1)))
    min_v=s.min()
    max_v=s.max()
    if pd.isna(min_v) or pd.isna(max_v) or max_v==min_v:
        return s.fillna(0.0)
    return (s-min_v)/(max_v-min_v)

#calculeaza scor pe fiecare coloana
for col in all_cols:
    df[col+"_score"]=column_uniqueness_score(df[col])

#scoruri medii pe categorii 
def mean_or_zero(cols):
    if len(cols)==0:
        return 0.0
    return df[[c+"_score" for c in cols]].mean(axis=1)

primary_score=mean_or_zero(primary_cols)
secondary_score=mean_or_zero(secondary_cols)
context_score=mean_or_zero(context_cols)

#scor final ponderat 
df["unicity_score"]=(
    0.5*primary_score+
    0.3*secondary_score+
    0.2*context_score
)

out_path=r"D:\cv\task_ver\unicity_scores.parquet"  
df.to_parquet(out_path, engine="pyarrow", compression="snappy", index=False)

