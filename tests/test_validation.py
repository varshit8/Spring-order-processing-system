import json
from pathlib import Path

from app.validation import (
    evaluate_validation_report,
    generate_validation_report,
    load_records,
    render_validation_summary,
    write_validation_report,
    write_validation_summary,
)

REFERENCE_PATH = Path("data/reference/baseline_inputs.json")
STABLE_PATH = Path("data/environments/dev/candidate_inputs.json")
DRIFTED_PATH = Path("data/environments/prod/candidate_inputs.json")


def test_stable_batch_does_not_trigger_drift() -> None:
    reference_records = load_records(REFERENCE_PATH)
    candidate_records = load_records(STABLE_PATH)

    report = generate_validation_report(reference_records, candidate_records)

    assert report["drift_detected"] is False
    assert all(not check["drift_detected"] for check in report["feature_checks"])


def test_drifted_batch_flags_multiple_features() -> None:
    reference_records = load_records(REFERENCE_PATH)
    candidate_records = load_records(DRIFTED_PATH)

    report = generate_validation_report(reference_records, candidate_records)
    drifted_features = {
        check["feature"] for check in report["feature_checks"] if check["drift_detected"]
    }

    assert report["drift_detected"] is True
    assert {"age", "bmi", "glucose", "blood_pressure"} == drifted_features
    assert report["candidate_prediction_summary"]["average_risk_score"] > report["reference_prediction_summary"]["average_risk_score"]


def test_validation_report_can_be_written_to_disk(tmp_path: Path) -> None:
    reference_records = load_records(REFERENCE_PATH)
    candidate_records = load_records(STABLE_PATH)

    report = generate_validation_report(reference_records, candidate_records)
    output_path = write_validation_report(report, tmp_path / "validation_report.json")
    saved_report = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path.exists()
    assert saved_report["candidate_record_count"] == len(candidate_records)
    assert "generated_at_utc" in saved_report


def test_validation_evaluation_allows_clean_batch() -> None:
    reference_records = load_records(REFERENCE_PATH)
    candidate_records = load_records(STABLE_PATH)

    report = generate_validation_report(reference_records, candidate_records)
    evaluation = evaluate_validation_report(report, fail_on_drift=True, max_drifted_features=0)

    assert evaluation["should_fail"] is False
    assert evaluation["drifted_feature_count"] == 0


def test_validation_evaluation_fails_when_drift_threshold_is_exceeded() -> None:
    reference_records = load_records(REFERENCE_PATH)
    candidate_records = load_records(DRIFTED_PATH)

    report = generate_validation_report(reference_records, candidate_records)
    evaluation = evaluate_validation_report(report, fail_on_drift=True, max_drifted_features=1)

    assert evaluation["should_fail"] is True
    assert "drift_detected" in evaluation["failure_reasons"]
    assert "drifted_feature_count_exceeded" in evaluation["failure_reasons"]


def test_validation_summary_can_be_written_to_disk(tmp_path: Path) -> None:
    reference_records = load_records(REFERENCE_PATH)
    candidate_records = load_records(STABLE_PATH)

    report = generate_validation_report(reference_records, candidate_records)
    evaluation = evaluate_validation_report(report, fail_on_drift=True, max_drifted_features=0)
    summary = render_validation_summary(report, evaluation, mode="pr")
    output_path = write_validation_summary(summary, tmp_path / "validation_summary.md")

    assert output_path.exists()
    contents = output_path.read_text(encoding="utf-8")
    assert "# Validation Summary" in contents
    assert "- Mode: pr" in contents
