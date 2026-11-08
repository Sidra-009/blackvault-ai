import re, pandas as pd

BRANDS = (r"nayapay|sadapay|easypaisa|jazzcash|bisp|hbl|ubl|meezan|allied|"
          r"alfalah|ptcl|jazz|zong|ufone|telenor|tcs|leopards|fbr|nadra")

def mask(t):
    t = str(t).lower()
    t = re.sub(r"\d[\d,\.]*", "<n>", t)
    t = re.sub(BRANDS, "<org>", t)
    t = re.sub(r"[^a-z<>\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

df = pd.read_excel("data/raw/phishing_dataset_1000.xlsx")
df = df.rename(columns={"Raw_text": "text", "Labels": "label",
                        "Source_Type": "source_type", "Normalized_text": "text_norm"})
df["label"] = df["label"].astype(int)
df["k_raw"] = df["text"].map(mask)
df["k_norm"] = df["text_norm"].map(mask)

# rows that share EITHER key belong to the same template (union-find)
parent = list(range(len(df)))
def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[rb] = ra
for col in ["k_raw", "k_norm"]:
    first = {}
    for i, k in enumerate(df[col]):
        if k in first:
            union(first[k], i)
        else:
            first[k] = i
df["template_id"] = [find(i) for i in range(len(df))]

df[["text", "label", "source_type", "template_id", "text_norm", "k_raw", "k_norm"]].to_csv(
    "data/processed/roman_urdu_zenodo.csv", index=False)
print("Rows:", len(df), df["label"].value_counts().to_dict())
print("Unique templates:", df["template_id"].nunique())
print("Templates with mixed labels:", int((df.groupby("template_id")["label"].nunique() > 1).sum()))
