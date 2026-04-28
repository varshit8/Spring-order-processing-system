from fastapi.testclient import TestClient

from app.main import app
from app.model import MODEL_VERSION

client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ml-inference-api"}


def test_dashboard_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "ML Validation Dashboard" in response.text
    assert "Environment Validation" in response.text
    assert "Manual Prediction" in response.text


def test_readiness() -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["model_version"] == MODEL_VERSION


def test_predict_success() -> None:
    payload = {
        "age": 45,
        "bmi": 27.3,
        "glucose": 142,
        "blood_pressure": 88,
    }

    response = client.post("/predict", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert body["prediction"] in {"low_risk", "high_risk"}
    assert 0.0 <= body["risk_score"] <= 1.0
    assert body["model_version"] == MODEL_VERSION
    assert body["validation_status"] == "passed"


def test_environment_validation_endpoint() -> None:
    response = client.get("/validation/qa")
    body = response.json()

    assert response.status_code == 200
    assert body["environment"] == "qa"
    assert body["status"] in {"PASSED", "FAILED"}
    assert "average_risk_score" in body


def test_environment_validation_unknown_environment() -> None:
    response = client.get("/validation/unknown")

    assert response.status_code == 404


def test_predict_schema_validation() -> None:
    payload = {
        "age": -1,
        "bmi": 27.3,
        "glucose": 142,
        "blood_pressure": 88,
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 422
