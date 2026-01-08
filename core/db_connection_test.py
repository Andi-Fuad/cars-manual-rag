# test_db_connection.py
import pytest
from db_connection import DatabaseConnection
import time

def test_database_connection():
    """Test that we can connect to PostgreSQL."""
    db = DatabaseConnection()
    
    # Try to connect
    conn = db.connect()
    assert conn is not None
    assert not conn.closed
    
    print("\n✓ Successfully connected to PostgreSQL")
    
    db.close()

def test_pgvector_extension():
    """Test that pgvector extension can be enabled."""
    db = DatabaseConnection()
    db.connect()
    
    # Enable pgvector
    db.enable_pgvector()
    
    # Verify it's enabled
    result = db.execute_query(
        "SELECT * FROM pg_extension WHERE extname = 'vector';",
        fetch=True
    )
    
    assert len(result) > 0, "pgvector extension not found"
    print(f"\n✓ pgvector extension is enabled")
    print(f"Extension info: {result}")
    
    db.close()

def test_basic_query():
    """Test basic SQL query execution."""
    db = DatabaseConnection()
    db.connect()
    
    # Simple query to verify database works
    result = db.execute_query("SELECT version();", fetch=True)
    
    assert len(result) > 0
    print(f"\n✓ PostgreSQL version: {result[0][0][:50]}...")
    
    db.close()

# Run with: pytest test_db_connection.py -v -s