import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report

en = pd.read_csv("data/processed/text.csv")
ru = pd.read_csv("data/processed/roman_urdu.csv")

model = make_pipeline(
    TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2),
    LogisticRegression(max_iter=1000, class_weight="balanced"))
model.fit(en["text"], en["label"])

print("English-trained model on Roman Urdu:")
print(classification_report(ru["label"], model.predict(ru["text"]), digits=4))
