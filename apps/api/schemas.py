from __future__ import annotations
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)
    latest_only: bool = False


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    version_id: str
    section_title: str
    score: float
    freshness_score: float


class DiagnosisResponse(BaseModel):
    failure_detected: bool
    failure_code: str | None
    root_component: str | None
    confidence: float
    recommended_repair: str | None
    evidence: list[str]


class QueryResponse(BaseModel):
    query_id: str
    answer_id: str
    answer: str
    citations: list[Citation]
    diagnosis: DiagnosisResponse
    metrics: dict[str, float]


class EvaluationRequest(BaseModel):
    query: str = Field(..., min_length=3)
    answer: str = Field(..., min_length=1)
    contexts: list[str] = Field(default_factory=list)
    expected_keywords: list[str] = Field(default_factory=list)


class EvaluationResponse(BaseModel):
    context_count: int
    answer_relevance: float
    faithfulness: float
    unsupported_claim_rate: float


class DiagnosisGraphRequest(BaseModel):
    query: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)
    latest_only: bool = False


class DiagnosisGraphResponse(BaseModel):
    graph: dict


class RepairRequest(BaseModel):
    query: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)


class RepairResponse(BaseModel):
    query: str
    action: str
    repair_applied: bool
    repair_success: bool
    before_diagnosis: dict
    after_diagnosis: dict
    before_metrics: dict
    after_metrics: dict
    deltas: dict
    before_version_ids: list[str]
    after_version_ids: list[str]
    latency_ms: float
