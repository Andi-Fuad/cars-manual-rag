# api/utils.py
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_manual_id() -> str:
    """Generate unique manual ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"manual_{timestamp}"

def find_duplicate_manual(file_hash: str, manuals_metadata: dict) -> Optional[str]:
    """Check if a manual with the same hash already exists."""
    for manual_id, metadata in manuals_metadata.items():
        if metadata['file_hash'] == file_hash:
            return manual_id
    return None

def load_manuals_metadata(upload_dir: Path) -> dict:
    """Load existing manuals metadata from upload directory."""
    manuals_metadata = {}
    
    if upload_dir.exists():
        for pdf_file in upload_dir.glob("*.pdf"):
            manual_id = pdf_file.stem
            manuals_metadata[manual_id] = {
                'manual_id': manual_id,
                'filename': pdf_file.name,
                'file_hash': calculate_file_hash(str(pdf_file)),
                'upload_date': datetime.fromtimestamp(pdf_file.stat().st_mtime).isoformat(),
                'file_size': pdf_file.stat().st_size,
                'processed': False,
                'file_path': str(pdf_file)
            }
    
    return manuals_metadata