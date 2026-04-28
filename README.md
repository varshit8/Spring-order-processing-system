# ML Service Validation Platform

This project is a starter implementation of an ML inference API with built-in validation and automated tests.

## What is included

- FastAPI service for model inference
- Trained logistic regression model artifact for inference
- Request and response schema validation
- Input feature validation
- Health and readiness endpoints
- Dataset-driven regression tests for prediction behavior
- Batch-based drift detection for incoming model features
- JSON validation report generation for CI and scheduled checks
- PR and scheduled CI validation modes with drift-based failure rules
- Environment-specific validation datasets for dev, qa, and prod
- Docker packaging for deployment-ready API startup
- Azure DevOps pipeline scaffold

## Project structure

```text
app/
  main.py
  model.py
  schemas.py
  validation.py
data/
  environments/
    config.json
    dev/
      candidate_inputs.json
    qa/
      candidate_inputs.json
    prod/
      candidate_inputs.json
  reference/
    baseline_inputs.json
  training/
    diabetes_risk_training_data.json
models/
  diabetes_risk_logreg_v1.json
scripts/
  demo_workflow.py
  generate_validation_report.py
  train_model.py
tests/
  fixtures/
    regression_cases.json
  test_api.py
  test_regression.py
  test_validation.py
azure-pipelines.yml
Dockerfile
requirements.txt
```

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m scripts.train_model
python -m pytest
uvicorn app.main:app --reload
```

After starting the API, open `http://127.0.0.1:8000/` to use the visual dashboard.

## Example request

```json
{
  "age": 45,
  "bmi": 27.3,
  "glucose": 142,
  "blood_pressure": 88
}
```

## Regression validation

The regression suite uses [tests/fixtures/regression_cases.json](c:\Users\varsh\OneDrive\Desktop\project_Z\tests\fixtures\regression_cases.json) as a golden dataset. Each case stores a request payload and the exact expected API response.

When model logic changes, update the expected outputs only after confirming the new behavior is intentional. This makes pull requests clearly show whether prediction behavior changed.

## Model training and versioning

The inference API loads a versioned model artifact from [models/diabetes_risk_logreg_v1.json](c:\Users\varsh\OneDrive\Desktop\project_Z\models\diabetes_risk_logreg_v1.json). Rebuild it with:

```powershell
python -m scripts.train_model `
  --training-data data\training\diabetes_risk_training_data.json `
  --output models\diabetes_risk_logreg_v1.json `
  --model-version diabetes-risk-logreg-v1
```

This keeps training data, model coefficients, and model version aligned so the API and validation framework always report the active model version.

## Drift validation and reporting

The drift workflow compares a baseline input batch in [data/reference/baseline_inputs.json](c:\Users\varsh\OneDrive\Desktop\project_Z\data\reference\baseline_inputs.json) against a current batch and flags large mean shifts in core features.

Run the report locally with:

```powershell
python -m scripts.generate_validation_report `
  --environment qa `
  --output reports\latest_validation_report.json `
  --summary-output reports\latest_validation_summary.md `
  --mode manual
```

The generated report includes:

- feature-level drift checks
- reference and candidate batch summaries
- average risk score and high-risk rate comparisons
- a top-level `drift_detected` flag for pipeline decisions
- a markdown summary artifact for PR reviews and scheduled monitoring

In CI, use stricter settings for pull requests to block merges on unexpected drift, and scheduled runs to continuously monitor production-like batches and publish artifacts for review.

## Environment-specific validation

The validation CLI can resolve environment defaults from [data/environments/config.json](c:\Users\varsh\OneDrive\Desktop\project_Z\data\environments\config.json).

- `dev`: stable baseline-like data used for PR gating
- `qa`: slightly shifted data used for manual validation and release checks
- `prod`: drifted data used to simulate production monitoring and alerting

## Deployment packaging

Build and run the API container with:

```powershell
docker build -t ml-validation-api .
docker run -p 8000:8000 ml-validation-api
```

## End-to-end demo

Run the demo workflow with:

```powershell
python -m scripts.demo_workflow
```

It exercises:

- `/health`
- `/ready`
- `/predict`
- environment-specific validation for `dev`, `qa`, and `prod`

## Visual dashboard

The browser dashboard is served directly by FastAPI at:

`http://127.0.0.1:8000/`

It includes:

- manual prediction inputs
- live health and readiness status
- environment validation cards for `dev`, `qa`, and `prod`

## Next steps

- Persist validation results for dashboards and audits
- Add external storage for validation history and alert integrations
