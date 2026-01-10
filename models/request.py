# api/models/request.py
from pydantic import BaseModel, Field
from typing import Optional, List

class QueryRequest(BaseModel):
    question: str = Field(..., description="The question to ask")
    manual_id: Optional[str] = Field(None, description="Manual ID to query (optional, uses latest if not specified)")
    top_k: int = Field(5, ge=1, le=20, description="Number of relevant chunks to retrieve")
    similarity_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum similarity score")
    include_sources: bool = Field(True, description="Whether to include source references")

class FilteredQueryRequest(BaseModel):
    question: str = Field(..., description="The question to ask")
    manual_id: Optional[str] = Field(None, description="Manual ID to query")
    page_number: Optional[int] = Field(None, ge=0, description="Filter by specific page number")
    section_header: Optional[str] = Field(None, description="Filter by section name")
    top_k: int = Field(5, ge=1, le=20, description="Number of results")

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Conversation history")
    manual_id: Optional[str] = Field(None, description="Manual ID to query")
    top_k: int = Field(3, ge=1, le=10, description="Number of relevant chunks")

class ProcessRequest(BaseModel):
    start_page: int = Field(0, ge=0, description="Starting page number")
    end_page: Optional[int] = Field(None, ge=0, description="Ending page number (optional)")
    process_images: bool = Field(False, description="Whether to process images")