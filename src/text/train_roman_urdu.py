import os, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

en = pd.read_csv("data/processed/text.csv")
ru = pd.read_csv("data/processed/roman_urdu.csv")
manual = "data/processed/roman_urdu_manual.csv"
if os.path.exists(manual):
    ru = pd.concat([ru, pd.read_csv(manual)], ignore_index=True)
ru = ru.drop_duplicates(subset="text").reset_index(drop=True)

gss = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
tr, te = next(gss.split(ru, ru["label"], groups=ru["template_id"]))
ru_tr, ru_te = ru.iloc[tr], ru.iloc[te]
print("RU train:", ru_tr.label.value_counts().to_dict(),
      "| RU test:", ru_te.label.value_counts().to_dict())

def make():
    return make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1),
        LogisticRegression(max_iter=1000, class_weight="balanced"))

def run(name, train_df):
    m = make().fit(train_df["text"], train_df["label"])
    pred = m.predict(ru_te["text"])
    p, r, f, _ = precision_recall_fscore_support(
        ru_te["label"], pred, average="binary", pos_label=1, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(ru_te["label"], pred, labels=[0, 1]).ravel()
    return f"| {name} | {p:.3f} | {r:.3f} | {f:.3f} | {fp/(fp+tn):.3f} |"

rows = [
    run("English only", en),
    run("Roman Urdu only", ru_tr),
    run("English + Roman Urdu", pd.concat([en[["text", "label"]], ru_tr[["text", "label"]]])),
]
table = ("| Training data | Spam precision | Spam recall | Spam F1 | FPR |\n"
         "|---|---|---|---|---|\n" + "\n".join(rows))
print(table)
open("results/roman_urdu_results.md", "w").write(
    "# Evaluation on held-out Roman Urdu templates\n\n" + table + "\n")
