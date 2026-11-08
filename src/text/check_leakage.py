import pandas as pd
from sklearn.model_selection import GroupKFold

ru = pd.read_csv("data/processed/roman_urdu_zenodo.csv")
ru["fold"] = -1
for k, (tr, te) in enumerate(GroupKFold(n_splits=5).split(ru, ru["label"], groups=ru["template_id"])):
    ru.loc[ru.index[te], "fold"] = k
for col in ["text", "text_norm", "k_raw", "k_norm"]:
    n = int((ru.groupby(col)["fold"].nunique() > 1).sum())
    print(f"{col}: {n} values appear in more than one fold   (must be 0)")
