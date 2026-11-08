import time

from src.app.model import predict_text, train_in_memory


def test_model_training_and_prediction_fallback():
    started = time.perf_counter()
    train_in_memory()
    elapsed = time.perf_counter() - started

    assert elapsed < 120

    expected_keys = {"risk", "label", "language_hint", "disclaimer"}
    messages = [
        "Your bank account is locked. Click this link now to claim your prize.",
        "Hi, are we still meeting for lunch at noon?",
    ]
    for message in messages:
        prediction = predict_text(message)
        assert set(prediction) == expected_keys
        assert isinstance(prediction["risk"], float)
        assert 0 <= prediction["risk"] <= 1
