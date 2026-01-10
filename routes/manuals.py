# routes/manuals.py
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from typing import List
import os

from dependencies import get_manual_service  # Import the dependency function
from models.response import ManualInfo, UploadResponse, ProcessingStatusResponse, MessageResponse

router = APIRouter(prefix="/api/manuals", tags=["Manuals"])

@router.post("/upload", response_model=UploadResponse)
async def upload_manual(
    file: UploadFile = File(...),
    manual_service = Depends(get_manual_service)  # Use Depends() here
):
    """Upload a car manual PDF."""
    if manual_service is None:
        raise HTTPException(status_code=503, detail="Manual service not initialized")
    
    success, response = manual_service.upload_manual(file)
    
    if not success:
        raise HTTPException(status_code=500, detail=response.get('error', 'Upload failed'))
    
    return UploadResponse(**response)

@router.get("", response_model=List[ManualInfo])
async def list_manuals(
    manual_service = Depends(get_manual_service)  # Use Depends() here
):
    """List all uploaded manuals with their metadata."""
    if manual_service is None:
        raise HTTPException(status_code=503, detail="Manual service not initialized")
    
    manuals = manual_service.list_manuals()
    return [ManualInfo(**m) for m in manuals]

@router.get("/{manual_id}", response_model=ManualInfo)
async def get_manual_info(
    manual_id: str,
    manual_service = Depends(get_manual_service)  # Use Depends() here
):
    """Get information about a specific manual."""
    if manual_service is None:
        raise HTTPException(status_code=503, detail="Manual service not initialized")
    
    manual = manual_service.get_manual(manual_id)
    
    if manual is None:
        raise HTTPException(status_code=404, detail="Manual not found")
    
    return ManualInfo(**manual)

@router.delete("/{manual_id}", response_model=MessageResponse)
async def delete_manual(
    manual_id: str,
    manual_service = Depends(get_manual_service)  # Use Depends() here
):
    """Delete a manual and its data."""
    if manual_service is None:
        raise HTTPException(status_code=503, detail="Manual service not initialized")
    
    success = manual_service.delete_manual(manual_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Manual not found or delete failed")
    
    return MessageResponse(
        message=f"Manual {manual_id} deleted successfully",
        manual_id=manual_id
    )

@router.post("/{manual_id}/process", response_model=MessageResponse)
async def process_manual(
    manual_id: str,
    background_tasks: BackgroundTasks,
    start_page: int = 0,
    end_page: int = None,
    process_images: bool = False,
    manual_service = Depends(get_manual_service),  # Use Depends() here
    processing_service=None  # You'll need to implement this
):
    """Process a manual (extract text, generate embeddings, store in database)."""
    if manual_service is None:
        raise HTTPException(status_code=503, detail="Manual service not initialized")
    
    # Check if manual exists
    manual = manual_service.get_manual(manual_id)
    if manual is None:
        raise HTTPException(status_code=404, detail="Manual not found")
    
    # TODO: You need to implement processing_service
    # For now, let's create a placeholder or skip this check
    # if processing_service.is_processing(manual_id):
    #     raise HTTPException(status_code=409, detail="Manual is already being processed")
    
    # Get file path
    metadata = manual_service.manuals_metadata[manual_id]
    pdf_path = metadata['file_path']
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Manual file not found on disk")
    
    # Start background processing
    def process_task():
        # TODO: Implement actual processing
        # For now, just mark as processed
        stats = {
            'total_pages': 0,
            'chunks_created': 0,
            'embeddings_generated': 0,
            'status': 'completed'
        }
        
        manual_service.mark_as_processed(manual_id, stats)
    
    background_tasks.add_task(process_task)
    
    return MessageResponse(
        message=f"Processing started for manual {manual_id}",
        manual_id=manual_id,
        status="processing"
    )

@router.get("/{manual_id}/process/status", response_model=ProcessingStatusResponse)
async def get_processing_status(
    manual_id: str,
    processing_service=None  # You'll need to implement this
):
    """Get processing status for a specific manual."""
    # TODO: Implement processing_service
    # For now, return a placeholder
    from datetime import datetime
    return ProcessingStatusResponse(
        manual_id=manual_id,
        status="not_implemented",
        progress=0,
        message="Processing service not implemented yet",
        last_updated=datetime.now().isoformat()
    )