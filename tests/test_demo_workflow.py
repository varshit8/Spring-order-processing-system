from app.validation import evaluate_validation_report, generate_validation_report, load_records


def test_environment_validation_profiles() -> None:
    reference_records = load_records("data/reference/baseline_inputs.json")
    dev_report = generate_validation_report(
        reference_records,
        load_records("data/environments/dev/candidate_inputs.json"),
    )
    qa_report = generate_validation_report(
        reference_records,
        load_records("data/environments/qa/candidate_inputs.json"),
    )
    prod_report = generate_validation_report(
        reference_records,
        load_records("data/environments/prod/candidate_inputs.json"),
    )

    dev_eval = evaluate_validation_report(dev_report, fail_on_drift=True, max_drifted_features=0)
    qa_eval = evaluate_validation_report(qa_report, fail_on_drift=True, max_drifted_features=1)
    prod_eval = evaluate_validation_report(prod_report, fail_on_drift=True, max_drifted_features=1)

    assert dev_eval["should_fail"] is False
    assert qa_eval["drifted_feature_count"] <= 1
    assert qa_eval["should_fail"] is False
    assert prod_eval["should_fail"] is True
