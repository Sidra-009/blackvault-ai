import os, joblib, numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold

ru = pd.read_csv("data/processed/roman_urdu_zenodo.csv")

def make():
    return make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2),
        LogisticRegression(max_iter=1000, class_weight="balanced"))

pred = np.zeros(len(ru), dtype=int)
prob = np.zeros(len(ru))
for tr, te in GroupKFold(n_splits=5).split(ru, ru["label"], groups=ru["source_type"]):
    m = make().fit(ru.iloc[tr]["text"], ru.iloc[tr]["label"])
    pred[te] = m.predict(ru.iloc[te]["text"])
    prob[te] = m.predict_proba(ru.iloc[te]["text"])[:, 1]

ru["pred"], ru["prob_scam"] = pred, prob
ru["correct"] = ru["pred"] == ru["label"]

print("Accuracy per source_type (held-out):")
print(ru.groupby(["label", "source_type"])["correct"].agg(["mean", "count"]).round(3).to_string())

err = ru[~ru["correct"]][["source_type", "label", "pred", "prob_scam", "text"]]
err.to_csv("results/errors_scamtype_heldout.csv", index=False)
print("\nTotal errors:", len(err))
print(err.sort_values("source_type").head(15).to_string(index=False))

os.makedirs("models", exist_ok=True)
joblib.dump(make().fit(ru["text"], ru["label"]), "models/text_model.joblib")
print("\nSaved models/text_model.joblib")
