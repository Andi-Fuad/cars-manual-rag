# test_context_builder.py
import pytest
from services.context_builder import ContextBuilder
from core.db_connection import DatabaseConnection
from schemas.database import DatabaseSchema
from services.embedding_generator import EmbeddingGenerator
from services.storage_manager import StorageManager
from services.similarity_search import SimilaritySearch
import os

@pytest.fixture
def setup_context_builder():
    """Setup context builder with sample data."""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")
    
    db = DatabaseConnection()
    db.connect()
    db.enable_pgvector()
    
    schema = DatabaseSchema(db)
    schema.drop_all_tables()
    schema.create_tables()
    schema.create_indexes()
    
    embedder = EmbeddingGenerator()
    storage = StorageManager(db, embedder)
    
    # Add sample data
    sample_chunks = [
        {
            'text': 'Mesin kendaraan ini memiliki kapasitas 1500cc.',
            'chunk_size': 47,
            'page_number': 5,
            'section_header': 'BAB 2: Spesifikasi Mesin'
        },
        {
            'text': 'Ganti oli mesin setiap 5000 km.',
            'chunk_size': 31,
            'page_number': 10,
            'section_header': 'BAB 3: Perawatan'
        }
    ]
    
    storage.store_chunks_batch(sample_chunks, batch_size=2, delay=0.5)
    
    search = SimilaritySearch(db, embedder)
    context_builder = ContextBuilder(search)
    
    yield context_builder, search, db, storage
    
    storage.clear_all_data()
    db.close()

def test_build_basic_context(setup_context_builder):
    """Test building basic context."""
    context_builder, search, db, storage = setup_context_builder
    
    # Get some chunks
    chunks = search.search_similar_chunks("mesin", top_k=2)
    
    context = context_builder.build_context(chunks)
    
    assert len(context) > 0
    assert "Sumber" in context
    assert "Halaman" in context
    
    print(f"\n{'='*60}")
    print("Generated Context:")
    print(f"{'='*60}")
    print(context)

def test_build_context_with_sources(setup_context_builder):
    """Test building context with separate sources."""
    context_builder, search, db, storage = setup_context_builder
    
    chunks = search.search_similar_chunks("oli", top_k=2)
    
    context, sources = context_builder.build_context_with_sources(chunks)
    
    assert len(context) > 0
    assert len(sources) > 0
    assert 'page' in sources[0]
    assert 'section' in sources[0]
    assert 'similarity' in sources[0]
    
    print(f"\n{'='*60}")
    print("Context:")
    print(f"{'='*60}")
    print(context)
    print(f"\n{'='*60}")
    print("Sources:")
    print(f"{'='*60}")
    for source in sources:
        print(f"  Page {source['page']}: {source['section']} ({source['similarity']:.2%})")

def test_format_sources(setup_context_builder):
    """Test source formatting."""
    context_builder, search, db, storage = setup_context_builder
    
    chunks = search.search_similar_chunks("mesin", top_k=2)
    _, sources = context_builder.build_context_with_sources(chunks)
    
    formatted = context_builder.format_sources(sources)
    
    assert len(formatted) > 0
    assert "📚" in formatted
    assert "Halaman" in formatted
    
    print(f"\n{formatted}")

def test_empty_chunks(setup_context_builder):
    """Test handling empty chunks."""
    context_builder, search, db, storage = setup_context_builder
    
    context = context_builder.build_context([])
    
    assert "Tidak ada informasi" in context
    print(f"\n{context}")

# Run with: pytest test_context_builder.py -v -s