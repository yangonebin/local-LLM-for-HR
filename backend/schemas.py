from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ── Dataset ──────────────────────────────────────────────
class DatasetInfo(BaseModel):
    id: str
    name: str
    description: str
    estimated_tokens: int
    size_gb: float
    category: str
    available: bool


class TrainingConfig(BaseModel):
    dataset_ids: list[str]
    d_model: int = 768
    n_layers: int = 12
    n_heads: int = 12
    d_ff: int = 3072
    max_seq_len: int = 1024
    batch_size: int = 16
    learning_rate: float = 3e-4
    max_epochs: int = 10
    vocab_size: int = 32000


class TrainingEstimate(BaseModel):
    total_tokens: int
    total_parameters: int
    estimated_hours: float
    datasets: list[DatasetInfo]


# ── Training Status ───────────────────────────────────────
class TrainingStatus(BaseModel):
    task_id: Optional[str]
    status: str  # idle | running | completed | failed | stopped
    epoch: int = 0
    total_epochs: int = 0
    step: int = 0
    loss: float = 0.0
    progress: float = 0.0
    elapsed_seconds: float = 0.0
    message: str = ""


# ── RAG ──────────────────────────────────────────────────
class DocumentInfo(BaseModel):
    id: str
    filename: str
    uploaded_at: datetime
    chunk_count: int
    size_bytes: int


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    qa_id: str


# ── RLHF ─────────────────────────────────────────────────
class FeedbackRequest(BaseModel):
    qa_id: str
    rating: int  # 1 (좋아요) or -1 (싫어요)
    comment: Optional[str] = None


class RLHFStats(BaseModel):
    total_feedback: int
    positive: int
    negative: int
    last_rlhf_at: Optional[datetime]
