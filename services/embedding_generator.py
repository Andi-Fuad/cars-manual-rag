# embedding_generator.py
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Optional
import time

load_dotenv()

class EmbeddingGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Gemini's embedding model
        self.model_name = "models/text-embedding-004"
        
    def generate_text_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
        """
        Generate embedding for a text chunk.
        
        task_type options:
        - RETRIEVAL_DOCUMENT: for chunks you want to search through
        - RETRIEVAL_QUERY: for user queries
        - SEMANTIC_SIMILARITY: for comparing similarity
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type=task_type
            )
            return result['embedding']
        except Exception as e:
            print(f"✗ Error generating embedding: {e}")
            raise
    
    def generate_batch_embeddings(
        self, 
        texts: List[str], 
        task_type: str = "RETRIEVAL_DOCUMENT",
        batch_size: int = 10,
        delay: float = 1.0
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with rate limiting.
        
        batch_size: number of texts to process at once
        delay: seconds to wait between batches (to avoid rate limits)
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            print(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}...")
            
            for text in batch:
                embedding = self.generate_text_embedding(text, task_type)
                embeddings.append(embedding)
            
            # Rate limiting
            if i + batch_size < len(texts):
                time.sleep(delay)
        
        return embeddings
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a user query."""
        return self.generate_text_embedding(query, task_type="RETRIEVAL_QUERY")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings (should be 768 for text-embedding-004)."""
        # Test with a simple text
        test_embedding = self.generate_text_embedding("test")
        return len(test_embedding)