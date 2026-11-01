"""Select a balanced subset of In-The-Wild clips and save it as a CSV (columns: path,y,speaker; y=1 means fake)."""
import argparse
import glob
import os

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="folder where release_in_the_wild.zip was extracted")
    ap.add_argument("--per-class", type=int, default=1500)
    ap.add_argument("--out", default="itw_subset.csv")
    a = ap.parse_args()

    meta_paths = glob.glob(os.path.join(a.root, "**", "meta.csv"), recursive=True)
    if not meta_paths:
        raise SystemExit(f"meta.csv not found under {a.root}")
    meta = pd.read_csv(meta_paths[0])
    need = {"file", "speaker", "label"}
    if not need.issubset(meta.columns):
        raise SystemExit(f"meta.csv must have columns {sorted(need)}, got {list(meta.columns)}")

    meta["y"] = meta["label"].astype(str).str.lower().isin(["spoof", "fake"]).astype(int)  # 1 = fake
    audio = {os.path.basename(p): p
             for p in glob.glob(os.path.join(a.root, "**", "*.*"), recursive=True)
             if p.lower().endswith((".wav", ".flac", ".mp3"))}
    meta["path"] = meta["file"].astype(str).map(lambda f: audio.get(os.path.basename(f)))
    n_missing = int(meta["path"].isna().sum())
    if n_missing:
        print(f"warning: dropping {n_missing} rows whose audio file was not found")
    meta = meta.dropna(subset=["path"])

    parts = []
    for k in (0, 1):
        sel = meta[meta["y"] == k]
        parts.append(sel.sample(min(a.per_class, len(sel)), random_state=42))
    sub = pd.concat(parts).reset_index(drop=True)[["path", "y", "speaker"]]
    sub.to_csv(a.out, index=False)
    print(sub["y"].value_counts().to_dict(), "| speakers:", sub["speaker"].nunique())


if __name__ == "__main__":
    main()
