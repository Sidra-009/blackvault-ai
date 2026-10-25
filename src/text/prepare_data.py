import pandas as pd

df = pd.read_csv("data/raw/SMSSpamCollection", sep="\t", names=["label", "text"])
df["label"] = (df["label"] == "spam").astype(int)   # spam=1, ham=0
df = df.dropna().drop_duplicates()
df.to_csv("data/processed/text.csv", index=False)

print(df.shape)
print(df["label"].value_counts())
