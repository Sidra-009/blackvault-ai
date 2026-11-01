"""Evaluate codec-augmented training for ONE layer.
--layer MUST be the layer selected from the In-The-Wild CV in results/audio_layers.md (never chosen from DFE-Val)."""
import argparse
import os

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

from common import eer, make_classifier, bootstrap_ci


def load(path):
    d = np.load(path, allow_pickle=False)
    return d["feats"], d["y"], d["g"]


def cv_eer(X, y, g, eval_mask):
    eers = []
    for tr, te in GroupKFold(n_splits=5).split(X, y, groups=g):
        assert not (set(g[tr]) & set(g[te])), "speaker leakage between train and test folds"
        te = te[eval_mask[te]]
        m = make_classifier().fit(X[tr], y[tr])
        eers.append(eer(y[te], m.predict_proba(X[te])[:, 1]))
    return float(np.mean(eers)), float(np.std(eers))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", type=int, required=True)
    ap.add_argument("--itw", required=True)
    ap.add_argument("--aug", nargs="+", required=True, help="augmented .npz files from augment_codec.py")
    ap.add_argument("--dfe", required=True)
    ap.add_argument("--out-md", default="results/audio_augmented.md")
    a = ap.parse_args()
    L = a.layer

    Xo, yo, go = load(a.itw)
    Xo, Xd_all = Xo[:, L], load(a.dfe)
    Xd, yd = Xd_all[0][:, L], Xd_all[1]

    parts = [(Xo, yo, go)]
    for f in a.aug:
        Xa, ya, ga = load(f)
        parts.append((Xa[:, L], ya, ga))  # ga holds the ORIGINAL speaker ids
    X = np.vstack([p[0] for p in parts])
    y = np.concatenate([p[1] for p in parts])
    g = np.concatenate([p[2] for p in parts])
    is_orig = np.arange(len(y)) < len(yo)

    base_cv = cv_eer(Xo, yo, go, np.ones(len(yo), dtype=bool))
    aug_cv = cv_eer(X, y, g, is_orig)  # test only on ORIGINAL clips of held-out speakers

    res = {}
    for name, (Xt, yt) in {"original only": (Xo, yo), "original + MP3 copies": (X, y)}.items():
        s = make_classifier().fit(Xt, yt).predict_proba(Xd)[:, 1]
        ci_e, ci_a = bootstrap_ci(yd, s)
        res[name] = (eer(yd, s), float(roc_auc_score(yd, s)), ci_e, ci_a)

    lines = [
        f"# Codec augmentation, layer {a.layer} (layer taken from the ITW-CV selection, not from DFE-Val)",
        "",
        f"Training clips: {len(yo)} original + {len(y) - len(yo)} re-encoded copies from {len(a.aug)} file(s)",
        "",
        "| Training data | ITW speaker-disjoint CV EER (originals only in test) | DFE-Val EER (95% CI) | DFE-Val AUC (95% CI) |",
        "|---|---|---|---|",
        f"| original only | {base_cv[0]:.4f} +/- {base_cv[1]:.4f} | {res['original only'][0]:.4f} "
        f"({res['original only'][2][0]:.4f} to {res['original only'][2][1]:.4f}) | {res['original only'][1]:.4f} "
        f"({res['original only'][3][0]:.4f} to {res['original only'][3][1]:.4f}) |",
        f"| original + MP3 copies | {aug_cv[0]:.4f} +/- {aug_cv[1]:.4f} | {res['original + MP3 copies'][0]:.4f} "
        f"({res['original + MP3 copies'][2][0]:.4f} to {res['original + MP3 copies'][2][1]:.4f}) | "
        f"{res['original + MP3 copies'][1]:.4f} "
        f"({res['original + MP3 copies'][3][0]:.4f} to {res['original + MP3 copies'][3][1]:.4f}) |",
        "",
        "Caveat: DFE-Val has only 102 clips and many fake clips come from the same account, "
        "so the effective sample size is smaller than 102. Do not claim generalization unless the DFE-Val "
        "confidence interval clearly excludes chance (EER 0.5, AUC 0.5).",
    ]
    d = os.path.dirname(a.out_md)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(a.out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
