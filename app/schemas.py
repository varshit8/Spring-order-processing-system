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


class DocumentIngestRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=180)
    content: str = Field(..., min_length=20)
    source_type: Literal["text", "markdown", "policy", "requirements", "notes"] = "text"


class DocumentIngestResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    status: Literal["indexed"]


class DocumentSummary(BaseModel):
    document_id: str
    filename: str
    source_type: str
    chunk_count: int


class Citation(BaseModel):
    document_id: str
    filename: str
    chunk_id: str
    excerpt: str
    score: float


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    top_k: int = Field(3, ge=1, le=8)


class SearchResponse(BaseModel):
    query: str
    citations: list[Citation]


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    top_k: int = Field(3, ge=1, le=8)


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieval_mode: Literal["local_keyword_rag"]


class AgentRequest(BaseModel):
    document_id: str


class AgentResponse(BaseModel):
    document_id: str
    result: str
    citations: list[Citation]
