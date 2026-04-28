import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Optional, Union

from app.model import MODEL_VERSION, score_prediction
from app.schemas import PredictionRequest

FEATURES = ("age", "bmi", "glucose", "blood_pressure")
DEFAULT_DRIFT_THRESHOLDS = {
    "age": 8.0,
    "bmi": 4.0,
    "glucose": 25.0,
    "blood_pressure": 12.0,
}


def load_records(path: Union[str, Path]) -> list[dict]:
    input_path = Path(path)
    with input_path.open(encoding="utf-8") as input_file:
        return json.load(input_file)


def summarize_batch(records: list[dict]) -> dict:
    summary: dict[str, dict[str, float | int]] = {}
    for feature in FEATURES:
        values = [float(record[feature]) for record in records]
        summary[feature] = {
            "count": len(values),
            "min": round(min(values), 4),
            "max": round(max(values), 4),
            "mean": round(mean(values), 4),
        }
    return summary


def score_batch(records: list[dict]) -> dict:
    scores = [
        score_prediction(PredictionRequest(**record))
        for record in records
    ]
    high_risk_count = sum(score >= 0.5 for score in scores)
    return {
        "average_risk_score": round(mean(scores), 4),
        "high_risk_rate": round(high_risk_count / len(scores), 4),
    }


def detect_feature_drift(
    reference_records: list[dict],
    candidate_records: list[dict],
    thresholds: Optional[dict[str, float]] = None,
) -> list[dict]:
    active_thresholds = thresholds or DEFAULT_DRIFT_THRESHOLDS
    reference_summary = summarize_batch(reference_records)
    candidate_summary = summarize_batch(candidate_records)

    feature_checks = []
    for feature in FEATURES:
        reference_mean = float(reference_summary[feature]["mean"])
        candidate_mean = float(candidate_summary[feature]["mean"])
        absolute_mean_shift = round(candidate_mean - reference_mean, 4)
        drift_detected = abs(absolute_mean_shift) > active_thresholds[feature]
        feature_checks.append(
            {
                "feature": feature,
                "reference_mean": reference_mean,
                "candidate_mean": candidate_mean,
                "absolute_mean_shift": absolute_mean_shift,
                "threshold": active_thresholds[feature],
                "drift_detected": drift_detected,
            }
        )
    return feature_checks


def generate_validation_report(
    reference_records: list[dict],
    candidate_records: list[dict],
    model_version: str = MODEL_VERSION,
) -> dict:
    feature_checks = detect_feature_drift(reference_records, candidate_records)
    drift_detected = any(check["drift_detected"] for check in feature_checks)

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_version": model_version,
        "reference_record_count": len(reference_records),
        "candidate_record_count": len(candidate_records),
        "drift_detected": drift_detected,
        "reference_summary": summarize_batch(reference_records),
        "candidate_summary": summarize_batch(candidate_records),
        "reference_prediction_summary": score_batch(reference_records),
        "candidate_prediction_summary": score_batch(candidate_records),
        "feature_checks": feature_checks,
    }


def evaluate_validation_report(
    report: dict,
    fail_on_drift: bool = False,
    max_drifted_features: int = 0,
) -> dict:
    drifted_features = [
        check["feature"] for check in report["feature_checks"] if check["drift_detected"]
    ]
    drifted_feature_count = len(drifted_features)
    should_fail = False
    failure_reasons = []

    if fail_on_drift and report["drift_detected"]:
        should_fail = True
        failure_reasons.append("drift_detected")

    if drifted_feature_count > max_drifted_features:
        should_fail = True
        failure_reasons.append("drifted_feature_count_exceeded")

    return {
        "should_fail": should_fail,
        "drifted_feature_count": drifted_feature_count,
        "drifted_features": drifted_features,
        "failure_reasons": failure_reasons,
    }


def render_validation_summary(report: dict, evaluation: dict, mode: str) -> str:
    status = "FAILED" if evaluation["should_fail"] else "PASSED"
    lines = [
        "# Validation Summary",
        "",
        "## Overview",
        f"- Mode: {mode}",
        f"- Status: {status}",
        f"- Model version: {report['model_version']}",
        f"- Drift detected: {report['drift_detected']}",
        f"- Drifted feature count: {evaluation['drifted_feature_count']}",
        "",
        "## Prediction Shift",
        f"- Reference average risk score: {report['reference_prediction_summary']['average_risk_score']}",
        f"- Candidate average risk score: {report['candidate_prediction_summary']['average_risk_score']}",
        f"- Reference high-risk rate: {report['reference_prediction_summary']['high_risk_rate']}",
        f"- Candidate high-risk rate: {report['candidate_prediction_summary']['high_risk_rate']}",
        "",
        "## Feature Checks",
    ]

    for check in report["feature_checks"]:
        lines.append(
            "- {feature}: reference_mean={reference_mean}, candidate_mean={candidate_mean}, "
            "shift={absolute_mean_shift}, threshold={threshold}, drift_detected={drift_detected}".format(
                **check
            )
        )

    if evaluation["failure_reasons"]:
        lines.extend(
            [
                "",
                "## Failure Reasons",
                *[f"- {reason}" for reason in evaluation["failure_reasons"]],
            ]
        )

    return "\n".join(lines) + "\n"


def write_validation_report(report: dict, output_path: Union[str, Path]) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return destination


def write_validation_summary(summary: str, output_path: Union[str, Path]) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(summary, encoding="utf-8")
    return destination
