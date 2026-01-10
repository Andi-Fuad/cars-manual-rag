# routes/query.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict

from dependencies import get_rag_pipeline, get_manuals_metadata
from models.response import QueryResponse
from models.request import QueryRequest, FilteredQueryRequest, ChatRequest

router = APIRouter(prefix="/api", tags=["Query"])

@router.post("/query", response_model=QueryResponse)
async def query_manual(
    request: QueryRequest,
    rag_pipeline = Depends(get_rag_pipeline),
    manuals_metadata: Dict = Depends(get_manuals_metadata)
):
    """Query a car manual with a question."""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    # Validate manual_id if provided
    if request.manual_id:
        if request.manual_id not in manuals_metadata:
            raise HTTPException(status_code=404, detail="Manual not found")
        
        if not manuals_metadata[request.manual_id]['processed']:
            raise HTTPException(
                status_code=400,
                detail="Manual has not been processed yet. Please process it first."
            )
    
    try:
        result = rag_pipeline.query(
            question=request.question,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            include_sources=request.include_sources
        )
        
        result['manual_id'] = request.manual_id
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.post("/query/filtered")
async def filtered_query(
    request: FilteredQueryRequest,
    rag_pipeline = Depends(get_rag_pipeline),
    manuals_metadata: Dict = Depends(get_manuals_metadata)
):
    """Query with filters for specific pages or sections."""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    if request.manual_id:
        if request.manual_id not in manuals_metadata:
            raise HTTPException(status_code=404, detail="Manual not found")
        
        if not manuals_metadata[request.manual_id]['processed']:
            raise HTTPException(status_code=400, detail="Manual not processed")
    
    try:
        result = rag_pipeline.query_with_filters(
            question=request.question,
            page_number=request.page_number,
            section_header=request.section_header,
            top_k=request.top_k
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filtered query failed: {str(e)}")

@router.post("/chat")
async def chat(
    request: ChatRequest,
    rag_pipeline = Depends(get_rag_pipeline),
    manuals_metadata: Dict = Depends(get_manuals_metadata)
):
    """Multi-turn conversation with a car manual."""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    if request.manual_id:
        if request.manual_id not in manuals_metadata:
            raise HTTPException(status_code=404, detail="Manual not found")
        
        if not manuals_metadata[request.manual_id]['processed']:
            raise HTTPException(status_code=400, detail="Manual not processed")
    
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        result = rag_pipeline.chat(messages=messages, top_k=request.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")