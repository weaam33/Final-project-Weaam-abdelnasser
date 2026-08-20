import json

import pandas as pd

from app.core.config import settings
from app.schemas.prediction import PredictionRequest

# Columns must match exactly what the notebook's Pipeline was trained on
# (see notebooks/house_price_model.ipynb, section 2.4).
NUMERIC_FEATURES = ["carpet_area_sqft", "bhk", "floor_num", "bathroom", "balcony", "car_parking"]
CATEGORICAL_FEATURES = ["location_grouped", "Furnishing", "Transaction", "Ownership", "facing"]

with open(settings.LOCATIONS_PATH) as f:
    KNOWN_LOCATIONS = set(json.load(f))


def request_to_dataframe(payload: PredictionRequest) -> pd.DataFrame:
    """Build the exact one-row DataFrame the trained Pipeline expects.

    Because the exported model is a full sklearn Pipeline (imputation, scaling,
    one-hot encoding all included), no manual encoding is needed here — we only
    need to line up the raw feature values under the right column names.
    """
    location_grouped = payload.location if payload.location in KNOWN_LOCATIONS else "other"

    row = {
        "carpet_area_sqft": payload.carpet_area_sqft,
        "bhk": payload.bhk,
        "floor_num": payload.floor_num,
        "bathroom": payload.bathroom,
        "balcony": payload.balcony,
        "car_parking": payload.car_parking,
        "location_grouped": location_grouped,
        "Furnishing": payload.furnishing,
        "Transaction": payload.transaction,
        "Ownership": payload.ownership,
        "facing": payload.facing,
    }

    return pd.DataFrame([row], columns=NUMERIC_FEATURES + CATEGORICAL_FEATURES)
