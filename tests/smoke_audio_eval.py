"""Local smoke test. Needs only numpy, pandas and scikit-learn (no torch, no audio, no network)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "audio"))

from common import eer, bootstrap_ci  # noqa: E402
from eval_layers import cv_layer  # noqa: E402
import extract_features, augment_codec, eval_augmented, prepare_itw, prepare_dfeval  # noqa: E402,F401  (import check only)

rng = np.random.default_rng(0)

assert eer([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) < 1e-9
y = np.array([i % 2 for i in range(200)])
g = np.array([f"s{(i // 2) % 10}" for i in range(200)])
assert 0.3 < eer(y, rng.random(200)) < 0.7

X_sep = rng.normal(size=(200, 20)) + y[:, None] * 2.0
e, sd, auc = cv_layer(X_sep, y, g)
assert e < 0.2 and auc > 0.9, (e, auc)

X_noise = rng.normal(size=(200, 20))
e2, _, _ = cv_layer(X_noise, y, g)
assert e2 > 0.3, e2

ci_e, ci_a = bootstrap_ci(y, y + rng.normal(size=200), n=50)
assert len(ci_e) == 2 and len(ci_a) == 2 and ci_e[0] <= ci_e[1]

print("audio smoke test passed")
