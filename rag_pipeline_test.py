# test_rag_pipeline.py
import pytest
from core.db_connection import DatabaseConnection
from schemas.database import DatabaseSchema
from services.embedding_generator import EmbeddingGenerator
from services.storage_manager import StorageManager
from services.rag_pipeline import RAGPipeline
import os

@pytest.fixture
def setup_rag():
    """Setup RAG pipeline with sample data."""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")
    
    # Setup database
    db = DatabaseConnection()
    db.connect()
    db.enable_pgvector()
    
    schema = DatabaseSchema(db)
    schema.drop_all_tables()
    schema.create_tables()
    schema.create_indexes()
    
    # Add sample data
    embedder = EmbeddingGenerator()
    storage = StorageManager(db, embedder)
    
    sample_chunks = [
        {
            'text': 'Mesin kendaraan ini memiliki kapasitas 1500cc dengan teknologi fuel injection. Tenaga maksimal 110 HP pada 6000 RPM.',
            'chunk_size': 115,
            'page_number': 5,
            'section_header': 'BAB 2: Spesifikasi Mesin'
        },
        {
            'text': 'Periksa tekanan ban secara rutin setiap bulan. Tekanan yang direkomendasikan adalah 32 PSI untuk ban depan dan 30 PSI untuk ban belakang.',
            'chunk_size': 135,
            'page_number': 10,
            'section_header': 'BAB 3: Perawatan Rutin'
        },
        {
            'text': 'Ganti oli mesin setiap 5000 km atau 6 bulan, mana yang lebih dulu. Gunakan oli dengan viskositas SAE 10W-40 atau sesuai rekomendasi pabrikan.',
            'chunk_size': 140,
            'page_number': 11,
            'section_header': 'BAB 3: Perawatan Rutin'
        },
        {
            'text': 'Sistem rem ABS (Anti-lock Braking System) memberikan kontrol maksimal saat pengereman darurat. Jangan memompa rem saat ABS aktif.',
            'chunk_size': 135,
            'page_number': 15,
            'section_header': 'BAB 4: Sistem Keamanan'
        },
        {
            'text': 'Transmisi manual 5-percepatan memberikan kontrol penuh kepada pengemudi. Pastikan kopling ditekan penuh saat mengganti gigi.',
            'chunk_size': 130,
            'page_number': 6,
            'section_header': 'BAB 2: Spesifikasi Mesin'
        }
    ]
    
    print("\n⚙️ Setting up test data...")
    storage.store_chunks_batch(sample_chunks, batch_size=2, delay=0.5)
    print("✓ Test data ready\n")
    
    db.close()
    
    # Create RAG pipeline
    rag = RAGPipeline()
    
    yield rag
    
    # Cleanup
    rag.close()

def test_basic_query(setup_rag):
    """Test basic RAG query."""
    rag = setup_rag
    
    question = "Berapa kapasitas mesin mobil ini?"
    
    result = rag.query(question, top_k=3)
    
    assert 'answer' in result
    assert 'sources' in result
    assert 'confidence' in result
    assert result['chunks_found'] > 0
    
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}")
    print(f"Answer: {result['answer']}")
    print(f"\nConfidence: {result['confidence']}")
    print(f"Chunks found: {result['chunks_found']}")
    print(f"\nSources:")
    for source in result['sources']:
        print(f"  • Page {source['page']}: {source['section']} ({source['similarity']:.2%})")

def test_maintenance_query(setup_rag):
    """Test query about maintenance."""
    rag = setup_rag
    
    question = "Kapan harus mengganti oli mesin?"
    
    result = rag.query(question, top_k=3)
    
    assert result['chunks_found'] > 0
    assert len(result['answer']) > 0
    
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}")
    print(f"Answer: {result['answer']}")
    
    # Should mention 5000 km or 6 months
    answer_lower = result['answer'].lower()
    assert '5000' in answer_lower or 'oli' in answer_lower

def test_safety_query(setup_rag):
    """Test safety-related query with warning."""
    rag = setup_rag
    
    question = "Bagaimana cara menggunakan rem ABS?"
    
    result = rag.query(question, top_k=3)
    
    assert result['chunks_found'] > 0
    assert result['warning'] is not None  # Should have safety warning
    
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}")
    print(f"Answer: {result['answer']}")
    
    if result['warning']:
        print(f"\n{result['warning']}")

def test_query_with_page_filter(setup_rag):
    """Test querying specific page."""
    rag = setup_rag
    
    question = "Apa yang ada di halaman ini?"
    
    result = rag.query_with_filters(question, page_number=10)
    
    assert 'filter' in result
    assert result['filter']['page'] == 10
    
    if result['chunks_found'] > 0:
        # All sources should be from page 10
        assert all(s['page'] == 10 for s in result['sources'])
    
    print(f"\n{'='*60}")
    print(f"Question: {question} (Page 10)")
    print(f"{'='*60}")
    print(f"Answer: {result['answer']}")

def test_query_with_section_filter(setup_rag):
    """Test querying specific section."""
    rag = setup_rag
    
    question = "Informasi tentang perawatan"
    
    result = rag.query_with_filters(question, section_header="Perawatan")
    
    if result['chunks_found'] > 0:
        # All sources should be from maintenance section
        assert all('Perawatan' in s['section'] for s in result['sources'])
    
    print(f"\n{'='*60}")
    print(f"Question: {question} (Section: Perawatan)")
    print(f"{'='*60}")
    print(f"Answer: {result['answer']}")

def test_chat_conversation(setup_rag):
    """Test multi-turn conversation."""
    rag = setup_rag
    
    # Conversation history
    messages = [
        {"role": "user", "content": "Berapa kapasitas mesin mobil ini?"},
        {"role": "assistant", "content": "Mesin kendaraan ini memiliki kapasitas 1500cc."},
        {"role": "user", "content": "Berapa tenaga maksimalnya?"}
    ]
    
    result = rag.chat(messages, top_k=3)
    
    assert 'answer' in result
    assert len(result['answer']) > 0
    
    print(f"\n{'='*60}")
    print("Chat Conversation:")
    print(f"{'='*60}")
    for msg in messages:
        role = "👤 User" if msg['role'] == 'user' else "🤖 Assistant"
        print(f"{role}: {msg['content']}")
    
    print(f"\n🤖 Assistant: {result['answer']}")

def test_irrelevant_query(setup_rag):
    """Test with completely irrelevant query."""
    rag = setup_rag
    
    question = "Bagaimana cara membuat nasi goreng?"
    
    result = rag.query(question, top_k=3, similarity_threshold=0.6)
    
    # Should either find no chunks or have low confidence
    print(f"\n{'='*60}")
    print(f"Irrelevant Question: {question}")
    print(f"{'='*60}")
    print(f"Chunks found: {result['chunks_found']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Answer: {result['answer']}")

def test_get_statistics(setup_rag):
    """Test getting RAG statistics."""
    rag = setup_rag
    
    stats = rag.get_statistics()
    
    assert 'total_chunks' in stats
    assert 'total_embeddings' in stats
    assert 'total_pages' in stats
    assert stats['total_chunks'] > 0
    
    print(f"\n{'='*60}")
    print("RAG System Statistics:")
    print(f"{'='*60}")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Total embeddings: {stats['total_embeddings']}")
    print(f"  Total pages: {stats['total_pages']}")
    print(f"  Embedding dimension: {stats['embedding_dimension']}")

# Run with: pytest test_rag_pipeline.py -v -s