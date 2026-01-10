# api/services/manual_service.py
import shutil
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from datetime import datetime
from fastapi import UploadFile

from utils.manual_metadata import calculate_file_hash, generate_manual_id, find_duplicate_manual

class ManualService:
    """Service for managing car manuals."""
    
    def __init__(self, upload_dir: Path, manuals_metadata: dict):
        self.upload_dir = upload_dir
        self.manuals_metadata = manuals_metadata
    
    def upload_manual(self, file: UploadFile) -> Tuple[bool, Dict]:
        """
        Upload a manual and check for duplicates.
        
        Returns:
            (success, response_data)
        """
        # Validate file type
        if not file.filename.endswith('.pdf'):
            return False, {"error": "Only PDF files are allowed"}
        
        # Generate manual ID
        manual_id = generate_manual_id()
        
        # Save file temporarily
        temp_path = self.upload_dir / f"temp_{file.filename}"
        
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Calculate hash
            file_hash = calculate_file_hash(str(temp_path))
            
            # Check for duplicates
            existing_manual_id = find_duplicate_manual(file_hash, self.manuals_metadata)
            
            if existing_manual_id:
                # Duplicate found
                temp_path.unlink()
                
                return True, {
                    "message": "Manual already exists in the system",
                    "manual_id": existing_manual_id,
                    "filename": self.manuals_metadata[existing_manual_id]['filename'],
                    "file_hash": file_hash,
                    "duplicate": True,
                    "existing_manual_id": existing_manual_id
                }
            
            # No duplicate, save with manual_id
            final_path = self.upload_dir / f"{manual_id}.pdf"
            temp_path.rename(final_path)
            
            # Store metadata
            self.manuals_metadata[manual_id] = {
                'manual_id': manual_id,
                'filename': file.filename,
                'file_hash': file_hash,
                'upload_date': datetime.now().isoformat(),
                'file_size': final_path.stat().st_size,
                'processed': False,
                'file_path': str(final_path)
            }
            
            return True, {
                "message": "Manual uploaded successfully",
                "manual_id": manual_id,
                "filename": file.filename,
                "file_hash": file_hash,
                "duplicate": False,
                "existing_manual_id": None
            }
            
        except Exception as e:
            # Cleanup on error
            if temp_path.exists():
                temp_path.unlink()
            return False, {"error": str(e)}
    
    def list_manuals(self) -> List[Dict]:
        """Get list of all manuals."""
        manuals = []
        
        for manual_id, metadata in self.manuals_metadata.items():
            manual_info = {
                'manual_id': manual_id,
                'filename': metadata['filename'],
                'file_hash': metadata['file_hash'],
                'upload_date': metadata['upload_date'],
                'file_size': metadata['file_size'],
                'processed': metadata['processed'],
                'total_chunks': metadata.get('total_chunks'),
                'total_pages': metadata.get('total_pages')
            }
            manuals.append(manual_info)
        
        return manuals
    
    def get_manual(self, manual_id: str) -> Optional[Dict]:
        """Get specific manual metadata."""
        if manual_id not in self.manuals_metadata:
            return None
        
        metadata = self.manuals_metadata[manual_id]
        
        return {
            'manual_id': manual_id,
            'filename': metadata['filename'],
            'file_hash': metadata['file_hash'],
            'upload_date': metadata['upload_date'],
            'file_size': metadata['file_size'],
            'processed': metadata['processed'],
            'total_chunks': metadata.get('total_chunks'),
            'total_pages': metadata.get('total_pages')
        }
    
    def delete_manual(self, manual_id: str) -> bool:
        """Delete a manual and its file."""
        if manual_id not in self.manuals_metadata:
            return False
        
        try:
            metadata = self.manuals_metadata[manual_id]
            
            # Delete file
            file_path = Path(metadata['file_path'])
            if file_path.exists():
                file_path.unlink()
            
            # Remove from metadata
            del self.manuals_metadata[manual_id]
            
            return True
        except Exception:
            return False
    
    def mark_as_processed(self, manual_id: str, stats: Dict):
        """Mark manual as processed with statistics."""
        if manual_id in self.manuals_metadata:
            self.manuals_metadata[manual_id]['processed'] = True
            self.manuals_metadata[manual_id]['total_chunks'] = stats.get('total_chunks')
            self.manuals_metadata[manual_id]['total_pages'] = stats.get('total_pages')