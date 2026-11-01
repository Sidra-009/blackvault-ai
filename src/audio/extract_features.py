"""Extract wav2vec2-base hidden-state features (mean+std pooled, all 13 layers) for a list of clips.
Clips that fail to load are DROPPED (never filled with zeros); path/y/speaker stay aligned with the features.
Output .npz keys: feats (n, 13, 1536), y, g (speaker ids), path."""
import argparse
import os

import numpy as np
import pandas as pd

from common import SR, CLIP_SEC, N_LAYERS


def load_clip(path):
    import librosa
    wav, _ = librosa.load(path, sr=SR, mono=True, duration=CLIP_SEC)
    n = SR * CLIP_SEC
    if len(wav) < n:
        wav = np.pad(wav, (0, n - len(wav)))
    return wav[:n]


def extract(paths, device=None):
    import torch
    from tqdm import tqdm
    from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2Model

    dev = device or ("cuda" if torch.cuda.is_available() else "cpu")
    print("device:", dev)
    fe = Wav2Vec2FeatureExtractor.from_pretrained("facebook/wav2vec2-base")
    mdl = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base").to(dev).eval()

    feats, ok = [], []
    for p in tqdm(list(paths)):
        try:
            wav = load_clip(p)
            inp = fe(wav, sampling_rate=SR, return_tensors="pt").to(dev)
            with torch.no_grad():
                hidden = mdl(**inp, output_hidden_states=True).hidden_states
            if len(hidden) != N_LAYERS:
                raise ValueError(f"expected {N_LAYERS} hidden states, got {len(hidden)}")
            per_layer = []
            for h in hidden:
                h = h.squeeze(0).cpu().numpy()
                per_layer.append(np.concatenate([h.mean(axis=0), h.std(axis=0)]))
            feats.append(np.stack(per_layer))
            ok.append(True)
        except Exception as e:
            print("dropped:", os.path.basename(str(p)), str(e)[:80])
            ok.append(False)
    if not feats:
        raise SystemExit("no clip could be processed")
    return np.stack(feats), np.array(ok)


def save(out, feats, kept):
    d = os.path.dirname(out)
    if d:
        os.makedirs(d, exist_ok=True)
    assert len(kept) == len(feats)
    np.savez(out, feats=feats, y=kept["y"].values,
             g=kept["speaker"].values.astype(str), path=kept["path"].values.astype(str))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="CSV with columns path,y,speaker")
    ap.add_argument("--out", required=True, help="output .npz")
    a = ap.parse_args()
    df = pd.read_csv(a.csv)
    feats, ok = extract(df["path"].tolist())
    kept = df[ok].reset_index(drop=True)
    save(a.out, feats, kept)
    print("saved", a.out, feats.shape, "dropped:", int((~ok).sum()))


if __name__ == "__main__":
    main()
