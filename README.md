# ScamShield

A defensive research prototype for detecting scam/phishing messages in English and Roman Urdu and AI-generated voice audio.  
It combines text and audio detection research in one planned application.  
Detection only; this project contains no generation tools.

## Status

| Component | Status | Evidence |
|---|---|---|
| Text baseline | DONE | [`src/text/baseline.py`](src/text/baseline.py); [`results/text_baseline.md`](results/text_baseline.md) |
| Roman Urdu evaluation | DONE (leak-fixed; see caveats) | [`src/text/cv_zenodo.py`](src/text/cv_zenodo.py), [`src/text/prepare_zenodo.py`](src/text/prepare_zenodo.py), [`src/text/check_leakage.py`](src/text/check_leakage.py); [`results/zenodo_results.md`](results/zenodo_results.md) |
| Error analysis | DONE | [`src/text/error_analysis.py`](src/text/error_analysis.py); local error output is `results/errors_scamtype_heldout.csv` |
| Audio detector | PARTIAL — experiments done in Colab; scripts and result files are being moved into the repo | Colab experiment results summarized below; no audio implementation/results files are in this repository yet |
| Whisper transcription | NOT STARTED | No implementation in the repository |
| Fusion | NOT STARTED | No combined score implementation |
| FastAPI | NOT STARTED | No API implementation |
| Streamlit | NOT STARTED | No UI implementation |

## Key findings

### Text detection

- **English-only model on Zenodo Roman Urdu, phishing/spam class:** precision **0.299**, recall **0.049**, F1 **0.085**, FPR **0.079**. English-trained detectors largely fail on Roman Urdu scams. Source: [`results/zenodo_results.md`](results/zenodo_results.md).
- **Held out by scam type (five-fold GroupKFold grouped by `source_type`):** Roman Urdu-only training gives precision **0.936**, recall **0.973**, F1 **0.954**, FPR **0.045**. English + Roman Urdu training gives precision **0.823**, recall **0.973**, F1 **0.891**, FPR **0.143**. Source: [`results/zenodo_results.md`](results/zenodo_results.md).
- **Adding English data and false positives (suggestive, small data):** false-positive rate increased in two separate evaluations: Zenodo scam-type evaluation, **0.045 → 0.143**; starter-set five-fold CV, **0.190 → 0.362**. The starter-set figures are from [`results/roman_urdu_cv_results.md`](results/roman_urdu_cv_results.md).
- **Zenodo template-held-out results:** F1 is **0.987** for Roman Urdu-only training and **0.990** for English + Roman Urdu training; FPR is **0.018** and **0.013**, respectively. These high values reflect a highly templated dataset—1,000 messages from only **189 templates**—and should not be read as real-world performance. An earlier version reported **1.000** F1 because spelling variants leaked across folds; this was found and fixed by merging rows that share either raw or normalized fingerprints with union-find. [`src/text/check_leakage.py`](src/text/check_leakage.py) checks for cross-fold overlap in raw text, normalized text, and both fingerprints. Source: [`results/zenodo_results.md`](results/zenodo_results.md).
- **English UCI baseline:** random-message 80/20 split, not template-held-out. For spam (class 1), precision **0.9612**, recall **0.9466**, F1 **0.9538**; accuracy **0.9884**, and FPR **0.0055**. Source: [`results/text_baseline.md`](results/text_baseline.md).
- **Error analysis:** the “Wrong Number Refund Scam” source type is reported as missed **11/11** times; it has no link, PIN, or urgency words and relies on social-engineering intent. “Utility Bill Payment Reminder” has **54.3%** accuracy, with legitimate messages flagged as scam. These source types come from a single template each, so treat the observations as illustrative, not stable estimates. See [`src/text/error_analysis.py`](src/text/error_analysis.py); the generated error CSV is local and git-ignored.

### Audio detection

The following experiments were run in Google Colab; they are not reproducible from this repository yet. The detector used wav2vec2-base last-layer mean-pooled embeddings from the first 4 seconds, followed by StandardScaler and LogisticRegression with C=0.1.

- **In-The-Wild:** 3,000 clips (1,500 real / 1,500 fake), 54 speakers. Five-fold speaker-disjoint CV: EER **0.1281 +/- 0.0644**, AUC **0.9419 +/- 0.0457**, accuracy **0.8840 +/- 0.0390**.
- **Cross-dataset DFE-Val test:** 102 social-media MP3 clips. EER **0.5392**, AUC **0.4375**, accuracy **0.4902**, which is chance level. **The detector does NOT generalize to social-media audio in its current form.**
- Caveats: the cross-dataset test has only 102 clips, and about 27 fake clips come from a single account. A layer-wise experiment and MP3-codec augmentation experiment are planned but not finished.

## Limitations

- The text datasets are small and highly templated; the Roman Urdu starter set is a pilot and has large standard deviations in five-fold results.
- There is no Urdu-script data in the current evaluation.
- The audio detector does not generalize to social-media audio in its current form.
- There is no end-to-end system yet: Whisper transcription, score fusion, FastAPI, and Streamlit are not implemented.
- Models are not deployable from a clean checkout; the audio model and inference code are not in the repository, and the locally generated text model is not a clean-checkout inference package.
- The reported experiments are research results, not a guarantee of performance on new messages or recordings.

## Ethics

- ScamShield is for detection only; it provides no voice-cloning or scam-generation tools.
- Do not use a model score as the sole basis for a decision. False positives and false negatives are possible.
- The SMS corpora contain phone-number-like strings and names. The UCI-derived `data/processed/text.csv` is currently tracked in Git; review privacy and license obligations before redistribution.
- The Zenodo Roman Urdu dataset license has not been verified. Its source and processed files are git-ignored and must not be redistributed until the license is confirmed.
- See [`data/README.md`](data/README.md) for dataset provenance, acquisition, license, citation, and tracking status.
