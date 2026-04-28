import json

from fastapi.testclient import TestClient

from app.main import app
from app.validation import evaluate_validation_report, generate_validation_report, load_records

client = TestClient(app)


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    print_section("Service Health")
    print(json.dumps(client.get("/health").json(), indent=2))

    print_section("Model Readiness")
    print(json.dumps(client.get("/ready").json(), indent=2))

    print_section("Prediction Demo")
    payload = {
        "age": 51,
        "bmi": 32.8,
        "glucose": 158,
        "blood_pressure": 96,
    }
    print(json.dumps({"request": payload, "response": client.post("/predict", json=payload).json()}, indent=2))

    reference_records = load_records("data/reference/baseline_inputs.json")

    for environment in ("dev", "qa", "prod"):
        print_section(f"{environment.upper()} Validation")
        candidate_records = load_records(f"data/environments/{environment}/candidate_inputs.json")
        report = generate_validation_report(reference_records, candidate_records)
        report["environment"] = environment
        max_drifted_features = 1 if environment in {"qa", "prod"} else 0
        evaluation = evaluate_validation_report(
            report,
            fail_on_drift=True,
            max_drifted_features=max_drifted_features,
        )
        summary = {
            "environment": environment,
            "drift_detected": report["drift_detected"],
            "drifted_features": evaluation["drifted_features"],
            "average_risk_score": report["candidate_prediction_summary"]["average_risk_score"],
            "status": "FAILED" if evaluation["should_fail"] else "PASSED",
        }
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
