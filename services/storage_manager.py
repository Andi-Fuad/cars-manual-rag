# storage_manager.py
from core.db_connection import DatabaseConnection
from services.embedding_generator import EmbeddingGenerator
from typing import List, Dict, Optional
import json

class StorageManager:
    def __init__(self, db: DatabaseConnection, embedder: EmbeddingGenerator):
        self.db = db
        self.embedder = embedder
    
    def store_chunk(
        self, 
        chunk_text: str, 
        chunk_size: int,
        page_number: int,
        section_header: str,
        chunk_index: int
    ) -> int:
        """Store a single chunk and return its ID."""
        query = """
        INSERT INTO document_chunks 
        (chunk_text, chunk_size, page_number, section_header, chunk_index)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        
        cursor = self.db.connection.cursor()
        cursor.execute(query, (chunk_text, chunk_size, page_number, section_header, chunk_index))
        chunk_id = cursor.fetchone()[0]
        self.db.connection.commit()
        cursor.close()
        
        return chunk_id
    
    def store_embedding(self, chunk_id: int, embedding: List[float]) -> int:
        """Store an embedding for a chunk."""
        query = """
        INSERT INTO chunk_embeddings (chunk_id, embedding)
        VALUES (%s, %s)
        RETURNING id;
        """
        
        # Convert embedding list to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        
        cursor = self.db.connection.cursor()
        cursor.execute(query, (chunk_id, embedding_str))
        embedding_id = cursor.fetchone()[0]
        self.db.connection.commit()
        cursor.close()
        
        return embedding_id
    
    def store_chunk_with_embedding(
        self,
        chunk_text: str,
        chunk_size: int,
        page_number: int,
        section_header: str,
        chunk_index: int
    ) -> tuple[int, int]:
        """Store a chunk and generate + store its embedding."""
        # Store the chunk
        chunk_id = self.store_chunk(
            chunk_text, 
            chunk_size, 
            page_number, 
            section_header, 
            chunk_index
        )
        
        # Generate embedding
        embedding = self.embedder.generate_text_embedding(chunk_text)
        
        # Store embedding
        embedding_id = self.store_embedding(chunk_id, embedding)
        
        return chunk_id, embedding_id
    
    def store_chunks_batch(
        self, 
        chunks: List[Dict],
        batch_size: int = 5,
        delay: float = 1.0
    ) -> List[tuple[int, int]]:
        """
        Store multiple chunks with embeddings.
        
        chunks: List of dicts with keys: text, chunk_size, page_number, section_header, chunk_index
        """
        results = []
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...")
            
            try:
                chunk_id, emb_id = self.store_chunk_with_embedding(
                    chunk_text=chunk['text'],
                    chunk_size=chunk['chunk_size'],
                    page_number=chunk.get('page_number', 0),
                    section_header=chunk.get('section_header', ''),
                    chunk_index=i
                )
                
                results.append((chunk_id, emb_id))
                print(f"  ✓ Stored chunk {chunk_id} with embedding {emb_id}")
                
                # Rate limiting
                if (i + 1) % batch_size == 0 and i + 1 < len(chunks):
                    import time
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"  ✗ Error storing chunk {i}: {e}")
                raise
        
        return results
    
    def store_image(
        self,
        page_number: int,
        image_path: str,
        image_description: Optional[str] = None
    ) -> int:
        """Store image metadata."""
        query = """
        INSERT INTO document_images (page_number, image_path, image_description)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        
        cursor = self.db.connection.cursor()
        cursor.execute(query, (page_number, image_path, image_description))
        image_id = cursor.fetchone()[0]
        self.db.connection.commit()
        cursor.close()
        
        return image_id
    
    def store_image_embedding(self, image_id: int, embedding: List[float]) -> int:
        """Store embedding for an image description."""
        query = """
        INSERT INTO image_embeddings (image_id, embedding)
        VALUES (%s, %s)
        RETURNING id;
        """
        
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        
        cursor = self.db.connection.cursor()
        cursor.execute(query, (image_id, embedding_str))
        embedding_id = cursor.fetchone()[0]
        self.db.connection.commit()
        cursor.close()
        
        return embedding_id
    
    def get_chunk_count(self) -> int:
        """Get total number of stored chunks."""
        query = "SELECT COUNT(*) FROM document_chunks;"
        result = self.db.execute_query(query, fetch=True)
        return result[0][0]
    
    def get_embedding_count(self) -> int:
        """Get total number of stored embeddings."""
        query = "SELECT COUNT(*) FROM chunk_embeddings;"
        result = self.db.execute_query(query, fetch=True)
        return result[0][0]
    
    def get_chunks_by_page(self, page_number: int) -> List[Dict]:
        """Retrieve all chunks from a specific page."""
        query = """
        SELECT id, chunk_text, section_header, chunk_index
        FROM document_chunks
        WHERE page_number = %s
        ORDER BY chunk_index;
        """
        
        cursor = self.db.connection.cursor()
        cursor.execute(query, (page_number,))
        results = cursor.fetchall()
        cursor.close()
        
        chunks = []
        for row in results:
            chunks.append({
                'id': row[0],
                'text': row[1],
                'section_header': row[2],
                'chunk_index': row[3]
            })
        
        return chunks
    
    def clear_all_data(self):
        """Clear all chunks and embeddings (useful for testing)."""
        queries = [
            "DELETE FROM chunk_embeddings;",
            "DELETE FROM document_chunks;",
            "DELETE FROM image_embeddings;",
            "DELETE FROM document_images;"
        ]
        
        for query in queries:
            self.db.execute_query(query)
        
        print("✓ All data cleared")