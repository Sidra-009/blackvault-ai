"""Download DFE-Val (102 social-media clips) from Hugging Face and save a CSV (columns: path,y,speaker; y=1 means fake).
The 'speaker' column is the uploader account parsed from the file name (best effort)."""
import argparse
import glob
import os
import re

import pandas as pd


def account(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    m = re.match(r"^(.*?)-\d{8}-\d+$", stem)
    return m.group(1) if m else stem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dfeval_subset.csv")
    a = ap.parse_args()

    from huggingface_hub import snapshot_download
    root = snapshot_download("ALLA1N/In-the-wild_validation-dataset", repo_type="dataset")
    files = sorted(glob.glob(os.path.join(root, "**", "*.mp3"), recursive=True))
    df = pd.DataFrame({"path": files})
    df["y"] = df["path"].map(lambda p: 1 if "/fake/" in p.replace("\\", "/") else 0)
    df["speaker"] = df["path"].map(account)
    df.to_csv(a.out, index=False)
    print(len(df), df["y"].value_counts().to_dict(), "| accounts:", df["speaker"].nunique())


if __name__ == "__main__":
    main()
