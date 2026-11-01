"""Per-layer evaluation. The layer is selected ONLY from In-The-Wild speaker-disjoint 5-fold CV.
DFE-Val numbers are reported for the selected layer (main result) and for all layers (exploratory, never used for selection)."""
import argparse
import os

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

from common import eer, make_classifier, bootstrap_ci, N_LAYERS


def cv_layer(X, y, g):
    eers, aucs = [], []
    for tr, te in GroupKFold(n_splits=5).split(X, y, groups=g):
        assert not (set(g[tr]) & set(g[te])), "speaker leakage between train and test folds"
        m = make_classifier().fit(X[tr], y[tr])
        s = m.predict_proba(X[te])[:, 1]
        eers.append(eer(y[te], s))
        aucs.append(roc_auc_score(y[te], s))
    return float(np.mean(eers)), float(np.std(eers)), float(np.mean(aucs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--itw", required=True, help="itw features .npz from extract_features.py")
    ap.add_argument("--dfe", required=True, help="DFE-Val features .npz from extract_features.py")
    ap.add_argument("--out-csv", default="results/audio_layers.csv")
    ap.add_argument("--out-md", default="results/audio_layers.md")
    a = ap.parse_args()

    Fi, Fd = np.load(a.itw), np.load(a.dfe)
    Xi, y, g = Fi["feats"], Fi["y"], Fi["g"]
    Xd, yd = Fd["feats"], Fd["y"]
    assert Xi.shape[1] == N_LAYERS and Xd.shape[1] == N_LAYERS
    assert len(Xi) == len(y) == len(g) and len(Xd) == len(yd)

    rows, dfe_scores = [], {}
    for l in range(N_LAYERS):
        cv_e, cv_s, cv_a = cv_layer(Xi[:, l], y, g)
        m = make_classifier().fit(Xi[:, l], y)
        s = m.predict_proba(Xd[:, l])[:, 1]
        dfe_scores[l] = s
        rows.append(dict(layer=l, itw_cv_eer=cv_e, itw_cv_eer_std=cv_s, itw_cv_auc=cv_a,
                         dfe_eer=eer(yd, s), dfe_auc=float(roc_auc_score(yd, s))))
        print(f"layer {l:2d}: ITW CV EER {cv_e:.4f} +/- {cv_s:.4f} | DFE-Val EER {rows[-1]['dfe_eer']:.4f}")

    df = pd.DataFrame(rows)
    best = int(df.loc[df["itw_cv_eer"].idxmin(), "layer"])  # ITW CV ONLY
    r = df[df["layer"] == best].iloc[0]
    ci_e, ci_a = bootstrap_ci(yd, dfe_scores[best])

    lines = [
        "# Layer-wise evaluation (wav2vec2-base, mean+std pooling, StandardScaler + LogReg C=0.1)",
        "",
        f"Selected layer: **{best}** (lowest mean ITW speaker-disjoint 5-fold CV EER; chosen WITHOUT looking at DFE-Val)",
        "",
        "## Main result for the selected layer",
        f"- ITW CV EER: {r['itw_cv_eer']:.4f} +/- {r['itw_cv_eer_std']:.4f}",
        f"- DFE-Val EER: {r['dfe_eer']:.4f} (95% bootstrap CI {ci_e[0]:.4f} to {ci_e[1]:.4f})",
        f"- DFE-Val AUC: {r['dfe_auc']:.4f} (95% bootstrap CI {ci_a[0]:.4f} to {ci_a[1]:.4f})",
        "",
        "## All layers (DFE-Val columns are exploratory and were NOT used for selection)",
        "",
        "| Layer | ITW CV EER | ITW CV AUC | DFE-Val EER (exploratory) | DFE-Val AUC (exploratory) |",
        "|---|---|---|---|---|",
    ]
    for _, x in df.iterrows():
        lines.append(f"| {int(x['layer'])} | {x['itw_cv_eer']:.4f} +/- {x['itw_cv_eer_std']:.4f} | "
                     f"{x['itw_cv_auc']:.4f} | {x['dfe_eer']:.4f} | {x['dfe_auc']:.4f} |")
    lines += ["", "Caveat: DFE-Val has only 102 clips and many fake clips come from the same account, "
                  "so the effective sample size is smaller than 102."]

    for path in (a.out_csv, a.out_md):
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
    df.to_csv(a.out_csv, index=False)
    with open(a.out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("selected layer:", best, "| wrote", a.out_csv, "and", a.out_md)


if __name__ == "__main__":
    main()
