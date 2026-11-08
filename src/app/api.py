"""FastAPI endpoints for text screening; audio analysis remains disabled."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.app import model


app = FastAPI(title="ScamShield text screening")


class TextRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model.is_model_loaded(),
        "audio_enabled": False,
    }


@app.post("/analyze/text")
def analyze_text(request: TextRequest):
    if not request.text.strip() or len(request.text) > 5000:
        raise HTTPException(status_code=422, detail="text must be non-empty and no longer than 5000 characters")
    return model.predict_text(request.text)


@app.post("/analyze/audio")
def analyze_audio():
    raise HTTPException(
        status_code=501,
        detail="Audio analysis is experimental and disabled: the detector did not generalize across datasets in our evaluation (see results).",
    )
