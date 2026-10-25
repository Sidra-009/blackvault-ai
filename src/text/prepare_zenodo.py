import re, pandas as pd

df = pd.read_excel("data/raw/phishing_dataset_1000.xlsx")
df = df.rename(columns={"Raw_text": "text", "Labels": "label",
                        "Source_Type": "source_type", "Normalized_text": "text_norm"})
df["label"] = df["label"].astype(int)

def mask(t):
    t = str(t).lower()
    t = re.sub(r"\d[\d,\.]*", "<n>", t)                      # numbers
    t = re.sub(r"nayapay|sadapay|easypaisa|jazzcash|bisp|hbl|ubl|meezan|allied|"
               r"alfalah|ptcl|jazz|zong|ufone|telenor|tcs|leopards|fbr|nadra",
               "<org>", t)                                    # common brands
    return t

df["template_id"] = pd.factorize(df["source_type"] + "||" + df["text"].map(mask))[0]
df[["text", "label", "source_type", "template_id", "text_norm"]].to_csv(
    "data/processed/roman_urdu_zenodo.csv", index=False)

print("Rows:", len(df), df["label"].value_counts().to_dict())
print("Unique templates:", df["template_id"].nunique())
print("Unique source types:", df["source_type"].nunique())
print(df.groupby(["label", "source_type"]).size().to_string())
