# api/models/response.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict]
    chunks_found: int
    confidence: str
    warning: Optional[str] = None
    manual_id: Optional[str] = None

class ManualInfo(BaseModel):
    manual_id: str
    filename: str
    file_hash: str
    upload_date: str
    file_size: int
    processed: bool
    total_chunks: Optional[int] = None
    total_pages: Optional[int] = None

class UploadResponse(BaseModel):
    message: str
    manual_id: str
    filename: str
    file_hash: str
    duplicate: bool
    existing_manual_id: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    total_manuals: int
    processed_manuals: int
    total_chunks: int
    total_embeddings: int
    ready: bool

class ProcessingStatusResponse(BaseModel):
    manual_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    message: str
    stats: Optional[Dict] = None

class HealthResponse(BaseModel):
    status: str
    rag_initialized: bool
    total_manuals: int

class MessageResponse(BaseModel):
    message: str
    manual_id: Optional[str] = None
    status: Optional[str] = None