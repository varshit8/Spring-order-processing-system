import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "regression_cases.json"


def load_regression_cases() -> list[dict]:
    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


@pytest.mark.parametrize("case", load_regression_cases(), ids=lambda case: case["name"])
def test_prediction_regression_cases(case: dict) -> None:
    response = client.post("/predict", json=case["request"])

    assert response.status_code == 200
    assert response.json() == case["expected_response"]
