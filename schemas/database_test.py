# test_db_schema.py
import pytest
from core.db_connection import DatabaseConnection
from schemas.database import DatabaseSchema

@pytest.fixture
def db_with_schema():
    """Setup database with schema."""
    db = DatabaseConnection()
    db.connect()
    db.enable_pgvector()
    
    schema = DatabaseSchema(db)
    
    # Clean slate for testing
    schema.drop_all_tables()
    
    yield db, schema
    
    # Cleanup
    db.close()

def test_create_tables(db_with_schema):
    """Test table creation."""
    db, schema = db_with_schema
    
    schema.create_tables()
    
    # Verify tables exist
    tables = schema.get_table_info()
    table_names = [t[0] for t in tables]
    
    assert 'document_chunks' in table_names
    assert 'chunk_embeddings' in table_names
    assert 'document_images' in table_names
    assert 'image_embeddings' in table_names
    
    print(f"\n✓ All tables created successfully")
    print(f"Tables: {table_names}")

def test_create_indexes(db_with_schema):
    """Test index creation."""
    db, schema = db_with_schema
    
    schema.create_tables()
    schema.create_indexes()
    
    # Verify indexes exist
    query = """
    SELECT indexname 
    FROM pg_indexes 
    WHERE schemaname = 'public'
    ORDER BY indexname;
    """
    
    indexes = db.execute_query(query, fetch=True)
    index_names = [i[0] for i in indexes]
    
    print(f"\n✓ Indexes created")
    for idx in index_names:
        print(f"  • {idx}")
    
    assert any('chunk_embeddings_vector_idx' in idx for idx in index_names)

def test_insert_sample_chunk(db_with_schema):
    """Test inserting a sample chunk."""
    db, schema = db_with_schema
    
    schema.create_tables()
    
    # Insert a test chunk
    insert_query = """
    INSERT INTO document_chunks (chunk_text, chunk_size, page_number, section_header)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """
    
    test_data = (
        "Ini adalah contoh teks dari manual mobil.",
        42,
        1,
        "BAB 1: Pengenalan"
    )
    
    cursor = db.connection.cursor()
    cursor.execute(insert_query, test_data)
    chunk_id = cursor.fetchone()[0]
    db.connection.commit()
    cursor.close()
    
    assert chunk_id is not None
    print(f"\n✓ Inserted test chunk with ID: {chunk_id}")
    
    # Verify we can retrieve it
    select_query = "SELECT * FROM document_chunks WHERE id = %s;"
    result = db.execute_query(select_query, (chunk_id,), fetch=True)
    
    assert len(result) == 1
    assert result[0][1] == test_data[0]  # chunk_text
    print(f"✓ Retrieved chunk: {result[0][1][:50]}...")

def test_vector_column_type(db_with_schema):
    """Test that vector column is properly created."""
    db, schema = db_with_schema
    
    schema.create_tables()
    
    # Check column type
    query = """
    SELECT column_name, data_type, udt_name
    FROM information_schema.columns
    WHERE table_name = 'chunk_embeddings' AND column_name = 'embedding';
    """
    
    result = db.execute_query(query, fetch=True)
    
    assert len(result) > 0
    print(f"\n✓ Vector column info: {result}")
    
    # The data_type might be 'USER-DEFINED' and udt_name should be 'vector'
    assert result[0][2] == 'vector' or result[0][1] == 'vector'
