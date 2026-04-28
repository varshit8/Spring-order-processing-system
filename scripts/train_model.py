import argparse
import json
import math
from pathlib import Path
from statistics import mean

FEATURE_ORDER = ("age", "bmi", "glucose", "blood_pressure")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train and export a lightweight logistic regression model.")
    parser.add_argument(
        "--training-data",
        default="data/training/diabetes_risk_training_data.json",
        help="Path to labeled training data in JSON format.",
    )
    parser.add_argument(
        "--output",
        default="models/diabetes_risk_logreg_v1.json",
        help="Path where the trained model artifact should be saved.",
    )
    parser.add_argument(
        "--model-version",
        default="diabetes-risk-logreg-v1",
        help="Version string to embed in the model artifact.",
    )
    parser.add_argument(
        "--eval-ratio",
        type=float,
        default=0.25,
        help="Fraction of records reserved for evaluation.",
    )
    return parser.parse_args()


def load_training_data(path: str) -> list[dict]:
    with Path(path).open(encoding="utf-8") as training_file:
        return json.load(training_file)


def split_records(records: list[dict], eval_ratio: float) -> tuple[list[dict], list[dict]]:
    eval_count = max(1, int(len(records) * eval_ratio))
    train_count = len(records) - eval_count
    return records[:train_count], records[train_count:]


def compute_feature_stats(records: list[dict]) -> dict:
    stats = {"mean": {}, "std": {}}
    for feature in FEATURE_ORDER:
        values = [float(record[feature]) for record in records]
        avg = mean(values)
        variance = sum((value - avg) ** 2 for value in values) / len(values)
        stats["mean"][feature] = round(avg, 6)
        stats["std"][feature] = round(math.sqrt(variance) or 1.0, 6)
    return stats


def standardize_record(record: dict, stats: dict) -> list[float]:
    return [
        (float(record[feature]) - stats["mean"][feature]) / stats["std"][feature]
        for feature in FEATURE_ORDER
    ]


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def score_row(weights: list[float], bias: float, row: list[float]) -> float:
    return sigmoid(sum(weight * value for weight, value in zip(weights, row)) + bias)


def train_logistic_regression(records: list[dict], iterations: int = 5000, learning_rate: float = 0.1) -> dict:
    stats = compute_feature_stats(records)
    features = [standardize_record(record, stats) for record in records]
    labels = [int(record["label"]) for record in records]

    weights = [0.0 for _ in FEATURE_ORDER]
    bias = 0.0

    for _ in range(iterations):
        gradient_weights = [0.0 for _ in FEATURE_ORDER]
        gradient_bias = 0.0

        for row, label in zip(features, labels):
            prediction = score_row(weights, bias, row)
            error = prediction - label

            for index, value in enumerate(row):
                gradient_weights[index] += error * value
            gradient_bias += error

        sample_count = len(records)
        for index in range(len(weights)):
            weights[index] -= learning_rate * gradient_weights[index] / sample_count
        bias -= learning_rate * gradient_bias / sample_count

    return {
        "feature_order": list(FEATURE_ORDER),
        "feature_stats": stats,
        "weights": [round(weight, 6) for weight in weights],
        "bias": round(bias, 6),
        "classification_threshold": 0.5,
    }


def evaluate_model(records: list[dict], artifact: dict) -> dict:
    features = [standardize_record(record, artifact["feature_stats"]) for record in records]
    labels = [int(record["label"]) for record in records]
    probabilities = [score_row(artifact["weights"], artifact["bias"], row) for row in features]
    predictions = [1 if probability >= artifact["classification_threshold"] else 0 for probability in probabilities]

    true_positive = sum(pred == 1 and label == 1 for pred, label in zip(predictions, labels))
    true_negative = sum(pred == 0 and label == 0 for pred, label in zip(predictions, labels))
    false_positive = sum(pred == 1 and label == 0 for pred, label in zip(predictions, labels))
    false_negative = sum(pred == 0 and label == 1 for pred, label in zip(predictions, labels))

    accuracy = (true_positive + true_negative) / len(records)
    precision = true_positive / max(1, true_positive + false_positive)
    recall = true_positive / max(1, true_positive + false_negative)

    return {
        "record_count": len(records),
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "positive_rate": round(sum(predictions) / len(records), 4),
    }


def write_model_artifact(artifact: dict, output_path: str) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    return destination


def main() -> None:
    args = parse_args()
    records = load_training_data(args.training_data)
    train_records, eval_records = split_records(records, args.eval_ratio)
    artifact = train_logistic_regression(train_records)
    artifact["model_version"] = args.model_version
    artifact["training_data_path"] = args.training_data
    artifact["data_split"] = {
        "train_record_count": len(train_records),
        "eval_record_count": len(eval_records),
        "eval_ratio": args.eval_ratio,
    }
    artifact["train_metrics"] = evaluate_model(train_records, artifact)
    artifact["eval_metrics"] = evaluate_model(eval_records, artifact)
    output_path = write_model_artifact(artifact, args.output)
    print(f"Model artifact written to {output_path}")
    print(f"Train accuracy: {artifact['train_metrics']['accuracy']}")
    print(f"Eval accuracy: {artifact['eval_metrics']['accuracy']}")


if __name__ == "__main__":
    main()
