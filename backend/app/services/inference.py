import joblib
import numpy as np
import pandas as pd

from app.core.config import settings


class ModelService:
    """Wraps the trained sklearn Pipeline. Loaded once at app startup (see main.py)."""

    def __init__(self) -> None:
        self._model = None

    def load(self) -> None:
        self._model = joblib.load(settings.MODEL_PATH)

    @property
    def is_ready(self) -> bool:
        return self._model is not None

    def predict(self, row: pd.DataFrame) -> float:
        if self._model is None:
            raise RuntimeError("Model has not been loaded yet.")
        # The notebook trained on log1p(price); invert with expm1 to get rupees.
        pred_log = self._model.predict(row)[0]
        return float(np.expm1(pred_log))


# Singleton used across the app / request lifecycle.
model_service = ModelService()
