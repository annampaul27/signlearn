import os
import threading

import joblib
import numpy as np
from django.conf import settings

MODELS_DIR = os.path.join(settings.BASE_DIR, "recognition", "ml_models")

NUM_LANDMARKS = 21
FEATURES_PER_HAND = NUM_LANDMARKS * 3       # 63
TOTAL_FEATURES = FEATURES_PER_HAND * 2      # 126

_lock = threading.Lock()
_model = None
_label_encoder = None
_scaler = None


def _load():
    global _model, _label_encoder, _scaler

    if _model is not None:
        return

    with _lock:
        if _model is not None:
            return

        model_path = os.path.join(MODELS_DIR, "isl_mlp_model.pkl")
        le_path = os.path.join(MODELS_DIR, "label_encoder.pkl")
        scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")

        for path in (model_path, le_path, scaler_path):
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Missing '{path}'. Copy isl_mlp_model.pkl, "
                    "label_encoder.pkl and scaler.pkl from your "
                    "real-time-isl-recognition/models/ folder into "
                    "recognition/ml_models/."
                )

        _model = joblib.load(model_path)
        _label_encoder = joblib.load(le_path)
        _scaler = joblib.load(scaler_path)

        if _model.n_features_in_ != TOTAL_FEATURES:
            raise ValueError(
                f"Loaded model expects {_model.n_features_in_} features, "
                f"but this pipeline builds {TOTAL_FEATURES}-dim vectors. "
                "Make sure you copied the two-hand (126-feature) model."
            )


def predict_from_vector(vector):
    _load()

    vector = np.asarray(vector, dtype=float)
    if vector.shape[0] != TOTAL_FEATURES:
        raise ValueError(f"Expected {TOTAL_FEATURES} features, got {vector.shape[0]}")

    scaled = _scaler.transform([vector])
    proba = _model.predict_proba(scaled)[0]
    idx = int(np.argmax(proba))
    confidence = float(proba[idx])
    letter = _label_encoder.inverse_transform([idx])[0]

    return letter.upper(), confidence