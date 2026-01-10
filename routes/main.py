# routes/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_pipeline import RAGPipeline
from routes import health, manuals, query
from services.manual_service import ManualService
from utils.manual_metadata import load_manuals_metadata

# Import dependencies module
from dependencies import set_rag_pipeline, set_manuals_metadata, set_manual_service

# Initialize FastAPI app
app = FastAPI(
    title="Car Manual RAG API",
    description="AI-powered car manual question answering system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup paths
UPLOAD_DIR = Path("/app/data/uploads") if os.path.exists("/app/data") else Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        print("🔧 Initializing RAG Pipeline...")
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline()
        
        # Load manuals metadata
        print(f"🔧 Loading manuals metadata from {UPLOAD_DIR}...")
        manuals_metadata = load_manuals_metadata(UPLOAD_DIR)
        print(f"✅ Loaded {len(manuals_metadata)} manuals")
        
        # Initialize services
        print(f"🔧 Initializing ManualService...")
        manual_service = ManualService(UPLOAD_DIR, manuals_metadata)
        print(f"✅ ManualService initialized")
        
        # Set global instances for dependencies
        set_rag_pipeline(rag_pipeline)
        set_manuals_metadata(manuals_metadata)
        set_manual_service(manual_service) 
        
        print("✅ All services initialized successfully")
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"❌ Failed to initialize services:\n{error_msg}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    from dependencies import get_rag_pipeline
    rag_pipeline = get_rag_pipeline()
    if rag_pipeline:
        rag_pipeline.close()
        print("✅ RAG Pipeline closed")

# Debug endpoint
@app.get("/debug")
async def debug_info():
    """Debug endpoint to check service status."""
    from dependencies import get_rag_pipeline, get_manuals_metadata
    return {
        "rag_pipeline_initialized": get_rag_pipeline() is not None,
        "manuals_count": len(get_manuals_metadata()),
        "upload_dir": str(UPLOAD_DIR),
        "upload_dir_exists": UPLOAD_DIR.exists(),
    }

# Include routers
app.include_router(health.router)
app.include_router(manuals.router)
app.include_router(query.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)