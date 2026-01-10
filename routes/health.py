# api/routes/health.py
from fastapi import APIRouter, HTTPException
from models.response import HealthResponse, StatusResponse

router = APIRouter(tags=["Health"])

@router.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Car Manual RAG API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "upload": "/api/manuals/upload",
            "list": "/api/manuals",
            "query": "/api/query",
            "status": "/api/status"
        }
    }

@router.get("/health", response_model=HealthResponse)
async def health_check(rag_pipeline=None, manuals_metadata: dict = {}):
    """Health check endpoint."""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    return HealthResponse(
        status="healthy",
        rag_initialized=rag_pipeline is not None,
        total_manuals=len(manuals_metadata)
    )

router = APIRouter(prefix="/api", tags=["System"])

@router.get("/status", response_model=StatusResponse)
async def get_status(rag_pipeline=None, manuals_metadata: dict = {}):
    """Get system status and statistics."""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        stats = rag_pipeline.get_statistics()
        processed_count = sum(1 for m in manuals_metadata.values() if m['processed'])
        
        return StatusResponse(
            status="ready" if stats['total_chunks'] > 0 else "no_data",
            total_manuals=len(manuals_metadata),
            processed_manuals=processed_count,
            total_chunks=stats['total_chunks'],
            total_embeddings=stats['total_embeddings'],
            ready=stats['total_chunks'] > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")