# db_schema.py
from core.db_connection import DatabaseConnection

class DatabaseSchema:
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def create_tables(self):
        """Create all necessary tables."""
        
        # Table for storing document chunks
        create_chunks_table = """
        CREATE TABLE IF NOT EXISTS document_chunks (
            id SERIAL PRIMARY KEY,
            chunk_text TEXT NOT NULL,
            chunk_size INTEGER,
            page_number INTEGER,
            section_header TEXT,
            chunk_index INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Table for storing text embeddings
        # Gemini text-embedding-004 produces 768-dimensional vectors
        create_embeddings_table = """
        CREATE TABLE IF NOT EXISTS chunk_embeddings (
            id SERIAL PRIMARY KEY,
            chunk_id INTEGER REFERENCES document_chunks(id) ON DELETE CASCADE,
            embedding vector(768),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Table for storing images
        create_images_table = """
        CREATE TABLE IF NOT EXISTS document_images (
            id SERIAL PRIMARY KEY,
            page_number INTEGER,
            image_path TEXT NOT NULL,
            image_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Table for storing image embeddings
        create_image_embeddings_table = """
        CREATE TABLE IF NOT EXISTS image_embeddings (
            id SERIAL PRIMARY KEY,
            image_id INTEGER REFERENCES document_images(id) ON DELETE CASCADE,
            embedding vector(768),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Execute table creation
        print("Creating tables...")
        self.db.execute_query(create_chunks_table)
        print("✓ document_chunks table created")
        
        self.db.execute_query(create_embeddings_table)
        print("✓ chunk_embeddings table created")
        
        self.db.execute_query(create_images_table)
        print("✓ document_images table created")
        
        self.db.execute_query(create_image_embeddings_table)
        print("✓ image_embeddings table created")
    
    def create_indexes(self):
        """Create indexes for better query performance."""
        
        # Index for vector similarity search using HNSW (Hierarchical Navigable Small World)
        create_vector_index = """
        CREATE INDEX IF NOT EXISTS chunk_embeddings_vector_idx 
        ON chunk_embeddings 
        USING hnsw (embedding vector_cosine_ops);
        """
        
        # Index for image embeddings
        create_image_vector_index = """
        CREATE INDEX IF NOT EXISTS image_embeddings_vector_idx 
        ON image_embeddings 
        USING hnsw (embedding vector_cosine_ops);
        """
        
        # Index for page number lookups
        create_page_index = """
        CREATE INDEX IF NOT EXISTS chunks_page_number_idx 
        ON document_chunks(page_number);
        """
        
        print("Creating indexes...")
        self.db.execute_query(create_vector_index)
        print("✓ Vector index on chunk_embeddings created")
        
        self.db.execute_query(create_image_vector_index)
        print("✓ Vector index on image_embeddings created")
        
        self.db.execute_query(create_page_index)
        print("✓ Page number index created")
    
    def drop_all_tables(self):
        """Drop all tables (useful for testing)."""
        tables = [
            "image_embeddings",
            "document_images",
            "chunk_embeddings",
            "document_chunks"
        ]
        
        for table in tables:
            self.db.execute_query(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"✓ Dropped table: {table}")
    
    def get_table_info(self):
        """Get information about all tables."""
        query = """
        SELECT table_name, 
               (SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        
        return self.db.execute_query(query, fetch=True)