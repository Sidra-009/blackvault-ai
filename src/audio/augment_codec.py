"""Re-encode the first 4 s of each clip to low-bitrate MP3 with ffmpeg, then extract features from the re-encoded audio.
Each re-encoded copy keeps the ORIGINAL clip's speaker id, so speaker-grouped CV never splits a clip from its copy."""
import argparse
import os
import subprocess

import numpy as np
import pandas as pd

from common import CLIP_SEC
from extract_features import extract, save


def reencode(src, dst, kbps):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-t", str(CLIP_SEC), "-b:a", f"{kbps}k", dst]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return r.returncode == 0 and os.path.exists(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="CSV with columns path,y,speaker (the ITW subset)")
    ap.add_argument("--bitrate", type=int, required=True, help="MP3 bitrate in kbps, e.g. 64 or 32")
    ap.add_argument("--workdir", default="itw_mp3")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    df = pd.read_csv(a.csv)
    outdir = os.path.join(a.workdir, f"{a.bitrate}k")
    os.makedirs(outdir, exist_ok=True)

    new_paths, keep = [], []
    for i, p in enumerate(df["path"]):
        dst = os.path.join(outdir, f"{i}_{os.path.splitext(os.path.basename(p))[0]}.mp3")
        keep.append(os.path.exists(dst) or reencode(p, dst, a.bitrate))
        new_paths.append(dst)
    keep = np.array(keep)
    df = df.assign(path=new_paths)[keep].reset_index(drop=True)
    print("re-encoded:", len(df), "ffmpeg failures (dropped):", int((~keep).sum()))

    feats, ok = extract(df["path"].tolist())
    kept = df[ok].reset_index(drop=True)
    save(a.out, feats, kept)
    print("saved", a.out, feats.shape, "feature failures (dropped):", int((~ok).sum()))


if __name__ == "__main__":
    main()
