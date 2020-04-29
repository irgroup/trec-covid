import pandas as pd
from config.config import META

col_names = ["cord_uid", "doi", "pmcid", "pubmed_id", "sha"]
dtypes = {"cord_uid": str, "doi": str, "pmcid": str, "pubmed_id": str}

df = pd.read_csv(META, usecols=col_names, dtype=dtypes)

col_write = ["cord_uid", "doi", "pmcid", "pubmed_id"]
df.to_csv('ids.csv', index=False, columns=col_write)