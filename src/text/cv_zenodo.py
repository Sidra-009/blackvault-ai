import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

en = pd.read_csv("data/processed/text.csv")[["text", "label"]]
ru = pd.read_csv("data/processed/roman_urdu_zenodo.csv")

def make():
    return make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2),
        LogisticRegression(max_iter=1000, class_weight="balanced"))

def metrics(y, pred):
    p, r, f, _ = precision_recall_fscore_support(
        y, pred, average="binary", pos_label=1, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return p, r, f, fp / (fp + tn)

def oof(group_col, setup):
    pred = np.zeros(len(ru), dtype=int)
    for tr, te in GroupKFold(n_splits=5).split(ru, ru["label"], groups=ru[group_col]):
        tr_df = ru.iloc[tr][["text", "label"]]
        train = {"English only": en,
                 "Roman Urdu only": tr_df,
                 "English + Roman Urdu": pd.concat([en, tr_df])}[setup]
        m = make().fit(train["text"], train["label"])
        pred[te] = m.predict(ru.iloc[te]["text"])
    return metrics(ru["label"], pred)

lines = ["| Held-out by | Training data | Precision | Recall | F1 | FPR |",
         "|---|---|---|---|---|---|"]
for group_col, name in [("template_id", "template"), ("source_type", "scam type")]:
    for setup in ["English only", "Roman Urdu only", "English + Roman Urdu"]:
        p, r, f, fpr = oof(group_col, setup)
        lines.append(f"| {name} | {setup} | {p:.3f} | {r:.3f} | {f:.3f} | {fpr:.3f} |")
table = "\n".join(lines)
print(table)
open("results/zenodo_results.md", "w").write(
    "# Out-of-fold results on Roman Urdu Phishing SMS (Zenodo 10.5281/zenodo.21810885)\n\n"
    + table + "\n")
