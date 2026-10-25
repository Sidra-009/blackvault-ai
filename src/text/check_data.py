import re, pandas as pd

ru = pd.concat([pd.read_csv("data/processed/roman_urdu.csv"),
                pd.read_csv("data/processed/roman_urdu_manual.csv")], ignore_index=True)
ru = ru.drop_duplicates(subset="text")

print("Rows:", len(ru))
print("Per class:", ru.label.value_counts().to_dict())
print("Unique templates per class:", ru.groupby("label")["template_id"].nunique().to_dict())

phone = re.compile(r"(\+?92|0)3\d{2}[-\s]?\d{7}")
cnic = re.compile(r"\b\d{5}-?\d{7}-?\d\b")
link = re.compile(r"https?://(?!\S*\.example)\S+")
for name, rx in [("PHONE", phone), ("CNIC", cnic), ("REAL LINK", link)]:
    bad = ru[ru["text"].str.contains(rx)]
    if len(bad):
        print(f"\nWARNING {name} found in {len(bad)} rows (remove before pushing):")
        print(bad[["text"]].to_string(index=False))
print("\nCheck done.")
