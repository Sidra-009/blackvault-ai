import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/text.csv")
df["length"] = df["text"].str.len()

df["label"].value_counts().rename({0: "ham", 1: "spam"}).plot(kind="bar", title="Class balance")
plt.tight_layout(); plt.savefig("results/class_balance.png"); plt.clf()

for lab, name in [(0, "ham"), (1, "spam")]:
    plt.hist(df[df.label == lab]["length"], bins=40, alpha=0.6, label=name)
plt.legend(); plt.title("Message length by class"); plt.xlabel("characters")
plt.tight_layout(); plt.savefig("results/length_dist.png")

print(df.groupby("label")["length"].describe())
