# Audio deepfake experiments (run on Google Colab with a GPU)

These scripts reproduce the audio experiments. They are NOT meant to run on the laptop (no GPU, no torch installed).
Status: the numbers quoted in the project README come from an earlier Colab notebook run (last-layer mean pooling).
The layer-wise and MP3-codec-augmentation results are NOT produced yet; they are produced by the steps below.

Rules built into the scripts
- The layer is chosen ONLY from the In-The-Wild (ITW) speaker-disjoint 5-fold CV. DFE-Val is never used for selection.
- Clips that fail to load are dropped, never replaced by zeros.
- MP3 copies keep the original speaker id so CV never splits a clip from its copy.

Colab cells (run in this order, from the repo root)
    !git clone <repo url>
    %cd blackvault-ai
    !pip -q install -r requirements-audio.txt
    !wget -q https://huggingface.co/datasets/mueller91/In-The-Wild/resolve/main/release_in_the_wild.zip -O itw.zip
    !unzip -q itw.zip -d itw
    !python src/audio/prepare_itw.py --root itw --out itw_subset.csv
    !python src/audio/prepare_dfeval.py --out dfeval_subset.csv
    !python src/audio/extract_features.py --csv itw_subset.csv --out itw_feats.npz
    !python src/audio/extract_features.py --csv dfeval_subset.csv --out dfe_feats.npz
    !python src/audio/eval_layers.py --itw itw_feats.npz --dfe dfe_feats.npz
    # read results/audio_layers.md and note the selected layer N (chosen from ITW CV only)
    !python src/audio/augment_codec.py --csv itw_subset.csv --bitrate 64 --out itw_aug64.npz
    !python src/audio/augment_codec.py --csv itw_subset.csv --bitrate 32 --out itw_aug32.npz
    !python src/audio/eval_augmented.py --layer N --itw itw_feats.npz --aug itw_aug64.npz itw_aug32.npz --dfe dfe_feats.npz

Local check (no GPU needed):  python tests\smoke_audio_eval.py

Data credits: In-The-Wild (Mueller et al., arXiv:2203.16263, CC BY-SA 4.0); DFE-Val (Hugging Face ALLA1N/In-the-wild_validation-dataset).
