# similarity_search.py
from core.db_connection import DatabaseConnection
from services.embedding_generator import EmbeddingGenerator
from typing import List, Dict, Optional
import numpy as np

class SimilaritySearch:
    def __init__(self, db: DatabaseConnection, embedder: EmbeddingGenerator):
        self.db = db
        self.embedder = embedder
    
    def search_similar_chunks(
        self, 
        query: str, 
        top_k: int = 5,
        similarity_threshold: float = 0.5
    ) -> List[Dict]:
        """
        Search for chunks similar to the query.
        
        Args:
            query: User's question
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)
        
        Returns:
            List of dicts with chunk info and similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_query_embedding(query)
        
        # Convert to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        # Search using cosine similarity
        search_query = """
        SELECT 
            dc.id,
            dc.chunk_text,
            dc.page_number,
            dc.section_header,
            dc.chunk_index,
            1 - (ce.embedding <=> %s::vector) as similarity
        FROM document_chunks dc
        JOIN chunk_embeddings ce ON dc.id = ce.chunk_id
        WHERE 1 - (ce.embedding <=> %s::vector) > %s
        ORDER BY ce.embedding <=> %s::vector
        LIMIT %s;
        """
        
        cursor = self.db.connection.cursor()
        cursor.execute(
            search_query, 
            (embedding_str, embedding_str, similarity_threshold, embedding_str, top_k)
        )
        results = cursor.fetchall()
        cursor.close()
        
        # Format results
        chunks = []
        for row in results:
            chunks.append({
                'id': row[0],
                'text': row[1],
                'page_number': row[2],
                'section_header': row[3],
                'chunk_index': row[4],
                'similarity': float(row[5])
            })
        
        return chunks
    
    def search_by_page(
        self,
        query: str,
        page_number: int,
        top_k: int = 3
    ) -> List[Dict]:
        """Search for similar chunks within a specific page."""
        query_embedding = self.embedder.generate_query_embedding(query)
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        search_query = """
        SELECT 
            dc.id,
            dc.chunk_text,
            dc.page_number,
            dc.section_header,
            1 - (ce.embedding <=> %s::vector) as similarity
        FROM document_chunks dc
        JOIN chunk_embeddings ce ON dc.id = ce.chunk_id
        WHERE dc.page_number = %s
        ORDER BY ce.embedding <=> %s::vector
        LIMIT %s;
        """
        
        cursor = self.db.connection.cursor()
        cursor.execute(search_query, (embedding_str, page_number, embedding_str, top_k))
        results = cursor.fetchall()
        cursor.close()
        
        chunks = []
        for row in results:
            chunks.append({
                'id': row[0],
                'text': row[1],
                'page_number': row[2],
                'section_header': row[3],
                'similarity': float(row[4])
            })
        
        return chunks
    
    def search_by_section(
        self,
        query: str,
        section_header: str,
        top_k: int = 3
    ) -> List[Dict]:
        """Search for similar chunks within a specific section."""
        query_embedding = self.embedder.generate_query_embedding(query)
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        search_query = """
        SELECT 
            dc.id,
            dc.chunk_text,
            dc.page_number,
            dc.section_header,
            1 - (ce.embedding <=> %s::vector) as similarity
        FROM document_chunks dc
        JOIN chunk_embeddings ce ON dc.id = ce.chunk_id
        WHERE dc.section_header ILIKE %s
        ORDER BY ce.embedding <=> %s::vector
        LIMIT %s;
        """
        
        cursor = self.db.connection.cursor()
        cursor.execute(
            search_query, 
            (embedding_str, f"%{section_header}%", embedding_str, top_k)
        )
        results = cursor.fetchall()
        cursor.close()
        
        chunks = []
        for row in results:
            chunks.append({
                'id': row[0],
                'text': row[1],
                'page_number': row[2],
                'section_header': row[3],
                'similarity': float(row[4])
            })
        
        return chunks