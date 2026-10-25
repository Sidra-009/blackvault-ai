import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv("data/processed/text.csv")
Xtr, Xte, ytr, yte = train_test_split(
    df["text"], df["label"], test_size=0.2, stratify=df["label"], random_state=42)

model = make_pipeline(
    TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2),
    LogisticRegression(max_iter=1000, class_weight="balanced"),
)
model.fit(Xtr, ytr)
pred = model.predict(Xte)

report = classification_report(yte, pred, digits=4)
cm = confusion_matrix(yte, pred)
tn, fp, fn, tp = cm.ravel()
fpr = fp / (fp + tn)

print(report)
print("Confusion matrix:\n", cm)
print(f"False positive rate: {fpr:.4f}")

with open("results/text_baseline.md", "w") as f:
    f.write("# TF-IDF (char n-grams) + Logistic Regression baseline\n\n")
    f.write("```\n" + report + "\n```\n")
    f.write(f"Confusion matrix:\n```\n{cm}\n```\n")
    f.write(f"False positive rate: {fpr:.4f}\n")
