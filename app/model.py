import json
import math
from functools import lru_cache
from pathlib import Path

from app.schemas import PredictionRequest

FEATURE_ORDER = ("age", "bmi", "glucose", "blood_pressure")
DEFAULT_MODEL_PATH = Path("models/diabetes_risk_logreg_v1.json")


@lru_cache(maxsize=1)
def load_model_artifact(model_path: str = str(DEFAULT_MODEL_PATH)) -> dict:
    artifact_path = Path(model_path)
    with artifact_path.open(encoding="utf-8") as model_file:
        return json.load(model_file)


def get_model_version() -> str:
    return str(load_model_artifact()["model_version"])


MODEL_VERSION = get_model_version()


def _standardize_features(payload: PredictionRequest, artifact: dict) -> list[float]:
    values = []
    means = artifact["feature_stats"]["mean"]
    stds = artifact["feature_stats"]["std"]

    for feature in FEATURE_ORDER:
        raw_value = float(getattr(payload, feature))
        values.append((raw_value - means[feature]) / stds[feature])

    return values


def score_prediction(payload: PredictionRequest) -> float:
    """Score a request using the trained logistic regression artifact."""
    artifact = load_model_artifact()
    standardized_values = _standardize_features(payload, artifact)
    logit = artifact["bias"]

    for weight, value in zip(artifact["weights"], standardized_values):
        logit += weight * value

    probability = 1.0 / (1.0 + math.exp(-logit))
    return round(probability, 4)


def classify_prediction(score: float) -> str:
    artifact = load_model_artifact()
    return "high_risk" if score >= artifact["classification_threshold"] else "low_risk"
