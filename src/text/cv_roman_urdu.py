import os, numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

en = pd.read_csv("data/processed/text.csv")[["text", "label"]]
ru = pd.concat([pd.read_csv("data/processed/roman_urdu.csv"),
                pd.read_csv("data/processed/roman_urdu_manual.csv")], ignore_index=True)
ru = ru.drop_duplicates(subset="text").reset_index(drop=True)

def make():
    return make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1),
        LogisticRegression(max_iter=1000, class_weight="balanced"))

setups = {"English only": "en", "Roman Urdu only": "ru", "English + Roman Urdu": "both"}
res = {k: [] for k in setups}
gkf = GroupKFold(n_splits=5)
for tr, te in gkf.split(ru, ru["label"], groups=ru["template_id"]):
    tr_df, te_df = ru.iloc[tr], ru.iloc[te]
    for name, kind in setups.items():
        train = en if kind == "en" else tr_df[["text", "label"]] if kind == "ru" \
            else pd.concat([en, tr_df[["text", "label"]]])
        m = make().fit(train["text"], train["label"])
        pred = m.predict(te_df["text"])
        p, r, f, _ = precision_recall_fscore_support(
            te_df["label"], pred, average="binary", pos_label=1, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(te_df["label"], pred, labels=[0, 1]).ravel()
        res[name].append((p, r, f, fp / max(fp + tn, 1)))

lines = ["| Training data | Precision | Recall | F1 | FPR |", "|---|---|---|---|---|"]
for name, v in res.items():
    a = np.array(v)
    cells = " | ".join(f"{a[:, i].mean():.3f} ± {a[:, i].std():.3f}" for i in range(4))
    lines.append(f"| {name} | {cells} |")
table = "\n".join(lines)
print(table)
open("results/roman_urdu_cv_results.md", "w").write(
    "# 5-fold group cross-validation (Roman Urdu, held-out templates)\n\n" + table + "\n")
