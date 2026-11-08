import pytest

from src.app.model import MODEL_PATH, predict_text


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="text model missing; train with python src/app/model.py")
@pytest.mark.parametrize(
    "message",
    [
        "Your account will be closed unless you verify your password immediately.",
        "Are we still meeting for lunch tomorrow?",
    ],
)
def test_predict_text_structure_and_risk(message):
    result = predict_text(message)
    assert set(result) == {"risk", "label", "language_hint", "disclaimer"}
    assert isinstance(result["risk"], float)
    assert 0.0 <= result["risk"] <= 1.0
    assert result["label"] in {"scam", "not scam"}
    assert result["language_hint"] in {"roman_urdu", "english"}
    assert isinstance(result["disclaimer"], str)


def test_health_endpoint():
    from fastapi.testclient import TestClient

    from src.app.api import app

    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_empty_text_returns_422():
    from fastapi.testclient import TestClient

    from src.app.api import app

    response = TestClient(app).post("/analyze/text", json={"text": ""})
    assert response.status_code == 422


def test_audio_returns_501():
    from fastapi.testclient import TestClient

    from src.app.api import app

    response = TestClient(app).post("/analyze/audio")
    assert response.status_code == 501
