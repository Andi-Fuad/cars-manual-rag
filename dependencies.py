# dependencies.py
from typing import Optional, Dict, Any
from rag_pipeline import RAGPipeline
from services.manual_service import ManualService

# Global instances that will be set at startup
_rag_pipeline: Optional[RAGPipeline] = None
_manuals_metadata: Dict[str, Any] = {}
_manual_service: Optional[ManualService] = None  # Add this

def set_rag_pipeline(pipeline: RAGPipeline):
    """Set the global RAG pipeline instance."""
    global _rag_pipeline
    _rag_pipeline = pipeline

def set_manuals_metadata(metadata: Dict[str, Any]):
    """Set the global manuals metadata."""
    global _manuals_metadata
    _manuals_metadata = metadata

def set_manual_service(service: ManualService):  # Add this
    """Set the global manual service instance."""
    global _manual_service
    _manual_service = service

def get_rag_pipeline() -> Optional[RAGPipeline]:
    """Get the RAG pipeline instance."""
    return _rag_pipeline

def get_manuals_metadata() -> Dict[str, Any]:
    """Get the manuals metadata."""
    return _manuals_metadata

def get_manual_service() -> Optional[ManualService]:  # Add this
    """Get the manual service instance."""
    return _manual_service