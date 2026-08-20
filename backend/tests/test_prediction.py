import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    # Using TestClient as a context manager triggers the app's lifespan
    # (startup/shutdown), which is what loads the model once.
    with TestClient(app) as c:
        yield c


def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_happy_path(client) -> None:
    payload = {
        "location": "Mumbai Sector 10",
        "bhk": 3,
        "carpet_area_sqft": 1200.0,
        "floor_num": 3,
        "bathroom": 2,
        "balcony": 1,
        "car_parking": 1,
        "furnishing": "Semi-Furnished",
        "transaction": "Resale",
        "ownership": "Freehold",
        "facing": "East",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "predicted_price" in body
    assert body["predicted_price"] > 0


def test_predict_unknown_location_falls_back_to_other(client) -> None:
    payload = {
        "location": "Some Never Before Seen Locality",
        "bhk": 2,
        "carpet_area_sqft": 900.0,
        "floor_num": 1,
        "bathroom": 1,
        "balcony": 0,
        "car_parking": 0,
        "furnishing": "Unfurnished",
        "transaction": "New Property",
        "ownership": "Freehold",
        "facing": "North",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200


def test_predict_invalid_input_returns_422(client) -> None:
    payload = {
        "location": "Mumbai Sector 10",
        "bhk": 3,
        "carpet_area_sqft": -50.0,  # invalid: must be > 0
        "floor_num": 3,
        "bathroom": 2,
        "balcony": 1,
        "furnishing": "Semi-Furnished",
        "transaction": "Resale",
        "ownership": "Freehold",
        "facing": "East",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
