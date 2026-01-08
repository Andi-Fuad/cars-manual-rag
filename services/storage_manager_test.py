# test_storage_manager.py
import pytest
from core.db_connection import DatabaseConnection
from schemas.database import DatabaseSchema
from services.embedding_generator import EmbeddingGenerator
from services.storage_manager import StorageManager
import os

@pytest.fixture
def setup_storage():
    """Setup database and storage manager."""
    # Skip if no API key
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
    
    # Setup embedding generator
    embedder = EmbeddingGenerator()
    
    # Create storage manager
    storage = StorageManager(db, embedder)
    
    yield storage, db
    
    # Cleanup
    storage.clear_all_data()
    db.close()

def test_store_single_chunk(setup_storage):
    """Test storing a single chunk without embedding."""
    storage, db = setup_storage
    
    chunk_id = storage.store_chunk(
        chunk_text="Ini adalah contoh teks dari manual mobil.",
        chunk_size=42,
        page_number=1,
        section_header="BAB 1: Pengenalan",
        chunk_index=0
    )
    
    assert chunk_id > 0
    print(f"\n✓ Stored chunk with ID: {chunk_id}")
    
    # Verify it's stored
    count = storage.get_chunk_count()
    assert count == 1

def test_store_chunk_with_embedding(setup_storage):
    """Test storing a chunk with its embedding."""
    storage, db = setup_storage
    
    chunk_id, emb_id = storage.store_chunk_with_embedding(
        chunk_text="Mesin kendaraan ini memiliki kapasitas 1500cc dan menggunakan teknologi fuel injection.",
        chunk_size=87,
        page_number=5,
        section_header="BAB 2: Spesifikasi Mesin",
        chunk_index=0
    )
    
    assert chunk_id > 0
    assert emb_id > 0
    
    print(f"\n✓ Stored chunk {chunk_id} with embedding {emb_id}")
    
    # Verify counts
    assert storage.get_chunk_count() == 1
    assert storage.get_embedding_count() == 1

def test_store_multiple_chunks(setup_storage):
    """Test storing multiple chunks as a batch."""
    storage, db = setup_storage
    
    chunks = [
        {
            'text': 'Periksa tekanan ban secara rutin setiap bulan.',
            'chunk_size': 47,
            'page_number': 10,
            'section_header': 'BAB 3: Perawatan Rutin'
        },
        {
            'text': 'Ganti oli mesin setiap 5000 km atau 6 bulan.',
            'chunk_size': 45,
            'page_number': 10,
            'section_header': 'BAB 3: Perawatan Rutin'
        },
        {
            'text': 'Sistem rem harus diperiksa setiap 10000 km.',
            'chunk_size': 44,
            'page_number': 11,
            'section_header': 'BAB 3: Perawatan Rutin'
        }
    ]
    
    results = storage.store_chunks_batch(chunks, batch_size=2, delay=0.5)
    
    assert len(results) == 3
    assert all(chunk_id > 0 and emb_id > 0 for chunk_id, emb_id in results)
    
    print(f"\n✓ Stored {len(results)} chunks with embeddings")
    
    # Verify counts
    assert storage.get_chunk_count() == 3
    assert storage.get_embedding_count() == 3

def test_retrieve_chunks_by_page(setup_storage):
    """Test retrieving chunks from a specific page."""
    storage, db = setup_storage
    
    # Store chunks on different pages
    chunks = [
        {
            'text': 'Chunk pada halaman 1',
            'chunk_size': 21,
            'page_number': 1,
            'section_header': 'BAB 1'
        },
        {
            'text': 'Chunk lain pada halaman 1',
            'chunk_size': 26,
            'page_number': 1,
            'section_header': 'BAB 1'
        },
        {
            'text': 'Chunk pada halaman 2',
            'chunk_size': 21,
            'page_number': 2,
            'section_header': 'BAB 2'
        }
    ]
    
    storage.store_chunks_batch(chunks, batch_size=3, delay=0.5)
    
    # Retrieve page 1 chunks
    page_1_chunks = storage.get_chunks_by_page(1)
    
    assert len(page_1_chunks) == 2
    assert all(chunk['text'].startswith('Chunk') for chunk in page_1_chunks)
    
    print(f"\n✓ Retrieved {len(page_1_chunks)} chunks from page 1")
    for chunk in page_1_chunks:
        print(f"  • {chunk['text']}")

def test_store_image_metadata(setup_storage):
    """Test storing image metadata."""
    storage, db = setup_storage
    
    image_id = storage.store_image(
        page_number=15,
        image_path="/path/to/image.png",
        image_description="Diagram sistem rem ABS"
    )
    
    assert image_id > 0
    print(f"\n✓ Stored image metadata with ID: {image_id}")

def test_store_image_with_embedding(setup_storage):
    """Test storing image with embedding."""
    storage, db = setup_storage
    
    # Store image metadata
    image_id = storage.store_image(
        page_number=15,
        image_path="/path/to/diagram.png",
        image_description="Diagram menunjukkan komponen mesin utama termasuk piston, kruk as, dan katup."
    )
    
    # Generate and store embedding from description
    description = "Diagram menunjukkan komponen mesin utama termasuk piston, kruk as, dan katup."
    embedding = storage.embedder.generate_text_embedding(description)
    
    emb_id = storage.store_image_embedding(image_id, embedding)
    
    assert emb_id > 0
    print(f"\n✓ Stored image {image_id} with embedding {emb_id}")

def test_clear_all_data(setup_storage):
    """Test clearing all data."""
    storage, db = setup_storage
    
    # Add some data
    chunks = [
        {'text': 'Test 1', 'chunk_size': 6, 'page_number': 1, 'section_header': 'Test'},
        {'text': 'Test 2', 'chunk_size': 6, 'page_number': 1, 'section_header': 'Test'}
    ]
    storage.store_chunks_batch(chunks, batch_size=2, delay=0.5)
    
    # Verify data exists
    assert storage.get_chunk_count() > 0
    
    # Clear
    storage.clear_all_data()
    
    # Verify empty
    assert storage.get_chunk_count() == 0
    assert storage.get_embedding_count() == 0
    
    print("\n✓ All data cleared successfully")

def test_embedding_dimension_in_database(setup_storage):
    """Test that embeddings are stored with correct dimensions."""
    storage, db = setup_storage
    
    # Store a chunk with embedding
    chunk_id, emb_id = storage.store_chunk_with_embedding(
        chunk_text="Test embedding dimensions",
        chunk_size=25,
        page_number=1,
        section_header="Test",
        chunk_index=0
    )
    
    # Query the embedding directly
    query = """
    SELECT array_length(embedding::real[], 1) as dimension
    FROM chunk_embeddings
    WHERE id = %s;
    """
    
    cursor = db.connection.cursor()
    cursor.execute(query, (emb_id,))
    dimension = cursor.fetchone()[0]
    cursor.close()
    
    assert dimension == 768, f"Expected 768 dimensions, got {dimension}"
    print(f"\n✓ Embedding stored with correct dimension: {dimension}")

# Run with: pytest test_storage_manager.py -v -s