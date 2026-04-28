import argparse
import json
import sys
from pathlib import Path

from app.validation import (
    evaluate_validation_report,
    generate_validation_report,
    load_records,
    render_validation_summary,
    write_validation_report,
    write_validation_summary,
)

ENVIRONMENT_CONFIG_PATH = Path("data/environments/config.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a drift and prediction validation report."
    )
    parser.add_argument(
        "--reference",
        help="Path to baseline reference input records in JSON format.",
    )
    parser.add_argument(
        "--candidate",
        help="Path to current input records in JSON format.",
    )
    parser.add_argument(
        "--environment",
        choices=("dev", "qa", "prod"),
        help="Environment name used to resolve dataset paths and default drift policy.",
    )
    parser.add_argument(
        "--output",
        default="reports/latest_validation_report.json",
        help="Path where the JSON validation report should be written.",
    )
    parser.add_argument(
        "--summary-output",
        default="reports/latest_validation_summary.md",
        help="Path where the markdown validation summary should be written.",
    )
    parser.add_argument(
        "--mode",
        choices=("pr", "scheduled", "manual"),
        default="manual",
        help="Validation execution mode used for reporting and CI behavior.",
    )
    parser.add_argument(
        "--fail-on-drift",
        action="store_true",
        help="Fail the command when any drift is detected.",
    )
    parser.add_argument(
        "--max-drifted-features",
        type=int,
        help="Maximum number of drifted features allowed before the command fails.",
    )
    return parser.parse_args()


def load_environment_config(environment: str) -> dict:
    with ENVIRONMENT_CONFIG_PATH.open(encoding="utf-8") as config_file:
        return json.load(config_file)[environment]


def resolve_inputs(args: argparse.Namespace) -> dict:
    if args.environment:
        config = load_environment_config(args.environment)
        return {
            "reference": args.reference or config["reference"],
            "candidate": args.candidate or config["candidate"],
            "fail_on_drift": args.fail_on_drift or config["fail_on_drift"],
            "max_drifted_features": (
                args.max_drifted_features
                if args.max_drifted_features is not None
                else config["max_drifted_features"]
            ),
        }

    if not args.reference or not args.candidate:
        raise ValueError("Either provide --environment or provide both --reference and --candidate.")

    return {
        "reference": args.reference,
        "candidate": args.candidate,
        "fail_on_drift": args.fail_on_drift,
        "max_drifted_features": 0 if args.max_drifted_features is None else args.max_drifted_features,
    }


def main() -> None:
    args = parse_args()
    resolved = resolve_inputs(args)
    reference_records = load_records(resolved["reference"])
    candidate_records = load_records(resolved["candidate"])
    report = generate_validation_report(reference_records, candidate_records)
    report["environment"] = args.environment or "custom"
    evaluation = evaluate_validation_report(
        report,
        fail_on_drift=resolved["fail_on_drift"],
        max_drifted_features=resolved["max_drifted_features"],
    )
    summary = render_validation_summary(report, evaluation, args.mode)
    output_path = write_validation_report(report, args.output)
    summary_path = write_validation_summary(summary, args.summary_output)

    print(f"Validation report written to {output_path}")
    print(f"Validation summary written to {summary_path}")
    print(
        "Validation status: {status}; drifted_features={count}; environment={environment}".format(
            status="FAILED" if evaluation["should_fail"] else "PASSED",
            count=evaluation["drifted_feature_count"],
            environment=report["environment"],
        )
    )

    if evaluation["should_fail"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
