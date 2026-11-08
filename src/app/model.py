"""Train and serve the ScamShield text screening model."""
import json
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline


ROOT = Path(__file__).resolve().parents[2]
ENGLISH_DATA = ROOT / "data" / "processed" / "text.csv"
ROMAN_URDU_DATA = ROOT / "data" / "processed" / "roman_urdu_zenodo.csv"
MODEL_PATH = ROOT / "models" / "text_model.joblib"
META_PATH = ROOT / "models" / "text_model_meta.json"
DISCLAIMER = "This is a screening aid, not a guarantee. Verify suspicious messages independently."
_model = None


def train_in_memory():
    english = pd.read_csv(ENGLISH_DATA)
    training = [english[["text", "label"]]]
    training_files = [str(ENGLISH_DATA.relative_to(ROOT))]
    row_counts = {training_files[0]: int(len(english))}
    warning = None

    if ROMAN_URDU_DATA.exists():
        roman_urdu = pd.read_csv(ROMAN_URDU_DATA)
        training.append(roman_urdu[["text", "label"]])
        roman_path = str(ROMAN_URDU_DATA.relative_to(ROOT))
        training_files.append(roman_path)
        row_counts[roman_path] = int(len(roman_urdu))
    else:
        warning = (
            "Roman Urdu Zenodo data is missing; trained on English data only. "
        )

    combined = pd.concat(training, ignore_index=True)
    model = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1),
        LogisticRegression(max_iter=1000, class_weight="balanced"),
    )
    model.fit(combined["text"], combined["label"])
    metadata = {
        "training_files": training_files,
        "row_counts": row_counts,
        "date": date.today().isoformat(),
        "warning": warning,
    }
    return model, metadata


def train_and_save():
    global _model
    model, metadata = train_in_memory()
    _model = model
    try:
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        META_PATH.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    except OSError as error:
        print(f"Could not save model files: {error}")
    else:
        print(f"Saved model: {MODEL_PATH}")
        print(f"Saved metadata: {META_PATH}")
    print(f"Training files: {', '.join(metadata['training_files'])}")
    if metadata["warning"]:
        print(f"Warning: {metadata['warning']}")


def load_model():
    global _model
    if _model is not None:
        return _model
    try:
        _model = joblib.load(MODEL_PATH)
    except Exception as error:
        print(f"Could not load saved model ({error}); training a model in memory.")
        _model, _ = train_in_memory()
    return _model


def is_model_loaded():
    return _model is not None


def predict_text(text) -> dict:
    model = load_model()
    risk = float(model.predict_proba([text])[0, list(model.classes_).index(1)])
    words = text.lower().split()
    roman_urdu_words = {
        "aap", "apka", "ka", "ki", "hai", "karein", "account", "band", "click"
    }
    # Hint Roman Urdu when at least one of the common Roman Urdu words appears in the message.
    language_hint = (
        "roman_urdu"
        if words and sum(word.strip(".,!?;:") in roman_urdu_words for word in words) / len(words) >= 0.1
        else "english"
    )
    return {
        "risk": risk,
        "label": "scam" if risk >= 0.5 else "not scam",
        "language_hint": language_hint,
        "disclaimer": DISCLAIMER,
    }


if __name__ == "__main__":
    train_and_save()
