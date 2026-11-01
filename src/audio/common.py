"""Shared constants and helpers for the audio deepfake experiments."""
import numpy as np
from sklearn.metrics import roc_curve, roc_auc_score

SR = 16000
CLIP_SEC = 4
N_LAYERS = 13


def eer(y_true, scores):
    fpr, tpr, _ = roc_curve(y_true, scores)
    fnr = 1 - tpr
    i = int(np.nanargmin(np.abs(fnr - fpr)))
    return float((fpr[i] + fnr[i]) / 2)


def make_classifier():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=0.1))


def bootstrap_ci(y_true, scores, n=1000, seed=42):
    """95% percentile bootstrap CI for EER and AUC. Returns ([eer_lo, eer_hi], [auc_lo, auc_hi])."""
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    scores = np.asarray(scores)
    e, a = [], []
    for _ in range(n):
        idx = rng.integers(0, len(y_true), len(y_true))
        if len(np.unique(y_true[idx])) < 2:
            continue
        e.append(eer(y_true[idx], scores[idx]))
        a.append(roc_auc_score(y_true[idx], scores[idx]))
    return np.percentile(e, [2.5, 97.5]).tolist(), np.percentile(a, [2.5, 97.5]).tolist()
