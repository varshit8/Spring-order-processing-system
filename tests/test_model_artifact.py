import json
from pathlib import Path

from app.model import DEFAULT_MODEL_PATH, MODEL_VERSION, load_model_artifact


def test_model_artifact_exists() -> None:
    assert DEFAULT_MODEL_PATH.exists()


def test_model_artifact_version_matches_runtime_version() -> None:
    artifact = load_model_artifact()

    assert artifact["model_version"] == MODEL_VERSION
    assert artifact["train_metrics"]["record_count"] > 0
    assert artifact["eval_metrics"]["record_count"] > 0
    assert artifact["data_split"]["eval_record_count"] > 0


def test_model_artifact_contains_expected_features() -> None:
    artifact = json.loads(Path(DEFAULT_MODEL_PATH).read_text(encoding="utf-8"))

    assert artifact["feature_order"] == ["age", "bmi", "glucose", "blood_pressure"]
    assert set(artifact["feature_stats"]["mean"]) == {"age", "bmi", "glucose", "blood_pressure"}
    assert "accuracy" in artifact["eval_metrics"]
