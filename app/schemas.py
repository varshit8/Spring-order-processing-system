from typing import Literal

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    bmi: float = Field(..., ge=10.0, le=80.0, description="Body mass index")
    glucose: int = Field(..., ge=40, le=500, description="Glucose reading")
    blood_pressure: int = Field(..., ge=40, le=250, description="Blood pressure")


class PredictionResponse(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=1.0)
    prediction: Literal["low_risk", "high_risk"]
    model_version: str
    validation_status: Literal["passed"]
