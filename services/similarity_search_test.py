# test_similarity_search.py
import pytest
from core.db_connection import DatabaseConnection
from schemas.database import DatabaseSchema
from services.embedding_generator import EmbeddingGenerator
from services.storage_manager import StorageManager
from services.similarity_search import SimilaritySearch
import os

@pytest.fixture
def setup_search():
    """Setup database with sample data for search testing."""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")
    
    # Setup
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
            'text': 'Mesin kendaraan ini memiliki kapasitas 1500cc dengan teknologi fuel injection modern.',
            'chunk_size': 85,
            'page_number': 5,
            'section_header': 'BAB 2: Spesifikasi Mesin'
        },
        {
            'text': 'Periksa tekanan ban secara rutin setiap bulan. Tekanan yang direkomendasikan adalah 32 PSI.',
            'chunk_size': 92,
            'page_number': 10,
            'section_header': 'BAB 3: Perawatan Rutin'
        },
        {
            'text': 'Ganti oli mesin setiap 5000 km atau 6 bulan. Gunakan oli dengan viskositas 10W-40.',
            'chunk_size': 80,
            'page_number': 11,
            'section_header': 'BAB 3: Perawatan Rutin'
        },
        {
            'text': 'Sistem rem ABS memberikan kontrol maksimal saat pengereman darurat di berbagai kondisi jalan.',
            'chunk_size': 99,
            'page_number': 15,
            'section_header': 'BAB 4: Sistem Keamanan'
        },
        {
            'text': 'Transmisi manual 5-percepatan memberikan kontrol penuh kepada pengemudi.',
            'chunk_size': 76,
            'page_number': 6,
            'section_header': 'BAB 2: Spesifikasi Mesin'
        }
    ]
    
    print("\nStoring sample chunks...")
    storage.store_chunks_batch(sample_chunks, batch_size=2, delay=0.5)
    print("✓ Sample data ready")
    
    search = SimilaritySearch(db, embedder)
    
    yield search, db, storage
    
    # Cleanup
    storage.clear_all_data()
    db.close()

def test_basic_similarity_search(setup_search):
    """Test basic similarity search."""
    search, db, storage = setup_search
    
    query = "Berapa kapasitas mesin mobil ini?"
    
    results = search.search_similar_chunks(query, top_k=3)
    
    assert len(results) > 0
    assert all('similarity' in r for r in results)
    assert all('text' in r for r in results)
    
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity: {result['similarity']:.4f}")
        print(f"   Page: {result['page_number']}")
        print(f"   Section: {result['section_header']}")
        print(f"   Text: {result['text'][:100]}...")
    
    # Top result should be about engine capacity
    assert '1500cc' in results[0]['text'] or 'mesin' in results[0]['text'].lower()

def test_search_with_threshold(setup_search):
    """Test similarity search with threshold."""
    search, db, storage = setup_search
    
    query = "Bagaimana cara mengganti oli?"
    
    # High threshold - fewer results
    results_high = search.search_similar_chunks(
        query, 
        top_k=5, 
        similarity_threshold=0.7
    )
    
    # Low threshold - more results
    results_low = search.search_similar_chunks(
        query, 
        top_k=5, 
        similarity_threshold=0.3
    )
    
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    print(f"Results with threshold 0.7: {len(results_high)}")
    print(f"Results with threshold 0.3: {len(results_low)}")
    
    assert len(results_low) >= len(results_high)

def test_search_by_page(setup_search):
    """Test searching within a specific page."""
    search, db, storage = setup_search
    
    query = "perawatan rutin"
    page_number = 10
    
    results = search.search_by_page(query, page_number, top_k=2)
    
    assert len(results) > 0
    assert all(r['page_number'] == page_number for r in results)
    
    print(f"\n{'='*60}")
    print(f"Search in page {page_number}: {query}")
    print(f"{'='*60}")
    
    for result in results:
        print(f"\nSimilarity: {result['similarity']:.4f}")
        print(f"Text: {result['text']}")

def test_search_by_section(setup_search):
    """Test searching within a specific section."""
    search, db, storage = setup_search
    
    query = "spesifikasi"
    section = "Spesifikasi Mesin"
    
    results = search.search_by_section(query, section, top_k=3)
    
    assert len(results) > 0
    assert all('Spesifikasi Mesin' in r['section_header'] for r in results)
    
    print(f"\n{'='*60}")
    print(f"Search in section '{section}': {query}")
    print(f"{'='*60}")
    
    for result in results:
        print(f"\nPage: {result['page_number']}")
        print(f"Text: {result['text'][:80]}...")

def test_irrelevant_query(setup_search):
    """Test with irrelevant query."""
    search, db, storage = setup_search
    
    query = "resep masakan nasi goreng"  # Completely irrelevant
    
    results = search.search_similar_chunks(
        query, 
        top_k=3,
        similarity_threshold=0.5
    )
    
    print(f"\n{'='*60}")
    print(f"Irrelevant query: {query}")
    print(f"{'='*60}")
    print(f"Results found: {len(results)}")
    
    if results:
        print(f"Top similarity: {results[0]['similarity']:.4f}")
    
    # With high threshold, should return few or no results
    assert len(results) < 3

# Run with: pytest test_similarity_search.py -v -s