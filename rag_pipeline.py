# rag_pipeline.py
from core.db_connection import DatabaseConnection
from schemas.database import DatabaseSchema
from services.embedding_generator import EmbeddingGenerator
from services.similarity_search import SimilaritySearch
from services.context_builder import ContextBuilder
from services.answer_generator import AnswerGenerator
from typing import Dict, List, Optional

class RAGPipeline:
    def __init__(self):
        """Initialize the complete RAG pipeline."""
        # Setup database connection
        self.db = DatabaseConnection()
        self.db.connect()
        self.db.enable_pgvector()
        
        # Initialize components
        self.embedder = EmbeddingGenerator()
        self.search = SimilaritySearch(self.db, self.embedder)
        self.context_builder = ContextBuilder(self.search)
        self.answer_generator = AnswerGenerator()
        
        print("✓ RAG Pipeline initialized")
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        similarity_threshold: float = 0.5,
        include_sources: bool = True
    ) -> Dict:
        """
        Main query method - the complete RAG pipeline.
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            similarity_threshold: Minimum similarity score
            include_sources: Whether to include source information
        
        Returns:
            Dict with answer, sources, and metadata
        """
        print(f"\n🔍 Processing query: {question}")
        
        # Step 1: Search for relevant chunks
        print(f"  → Searching for relevant chunks (top_k={top_k})...")
        chunks = self.search.search_similar_chunks(
            query=question,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        
        if not chunks:
            print(f"  ✗ No relevant chunks found")
            return {
                'question': question,
                'answer': "Maaf, saya tidak dapat menemukan informasi yang relevan dalam manual mobil untuk menjawab pertanyaan Anda.",
                'sources': [],
                'chunks_found': 0,
                'confidence': 'Low'
            }
        
        print(f"  ✓ Found {len(chunks)} relevant chunks")
        
        # Step 2: Build context
        print(f"  → Building context...")
        context, sources = self.context_builder.build_context_with_sources(chunks)
        
        # Step 3: Generate answer with safety check
        print(f"  → Generating answer...")
        result = self.answer_generator.generate_with_safety_check(question, context)
        
        print(f"  ✓ Answer generated (confidence: {result['confidence']})")
        
        # Step 4: Format response
        response = {
            'question': question,
            'answer': result['answer'],
            'sources': sources if include_sources else [],
            'chunks_found': len(chunks),
            'confidence': result['confidence'],
            'warning': result.get('warning')
        }
        
        return response
    
    def query_with_filters(
        self,
        question: str,
        page_number: Optional[int] = None,
        section_header: Optional[str] = None,
        top_k: int = 5
    ) -> Dict:
        """
        Query with filters for specific pages or sections.
        
        Args:
            question: User's question
            page_number: Filter by specific page
            section_header: Filter by section name
            top_k: Number of chunks to retrieve
        """
        print(f"\n🔍 Processing filtered query: {question}")
        
        # Search with filters
        if page_number is not None:
            print(f"  → Searching in page {page_number}...")
            chunks = self.search.search_by_page(question, page_number, top_k)
        elif section_header is not None:
            print(f"  → Searching in section '{section_header}'...")
            chunks = self.search.search_by_section(question, section_header, top_k)
        else:
            return self.query(question, top_k=top_k)
        
        if not chunks:
            return {
                'question': question,
                'answer': f"Maaf, tidak ditemukan informasi yang relevan {'di halaman ' + str(page_number) if page_number else 'di bagian ' + section_header}.",
                'sources': [],
                'chunks_found': 0,
                'confidence': 'Low'
            }
        
        # Build context and generate answer
        context, sources = self.context_builder.build_context_with_sources(chunks)
        result = self.answer_generator.generate_with_safety_check(question, context)
        
        return {
            'question': question,
            'answer': result['answer'],
            'sources': sources,
            'chunks_found': len(chunks),
            'confidence': result['confidence'],
            'warning': result.get('warning'),
            'filter': {'page': page_number, 'section': section_header}
        }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        top_k: int = 3
    ) -> Dict:
        """
        Multi-turn conversation with context.
        
        Args:
            messages: Conversation history [{"role": "user/assistant", "content": "..."}]
            top_k: Number of chunks to retrieve
        
        Returns:
            Dict with answer and metadata
        """
        # Get the last user message
        last_message = messages[-1]['content']
        
        print(f"\n💬 Processing chat message: {last_message}")
        
        # Search for relevant chunks based on current question
        chunks = self.search.search_similar_chunks(last_message, top_k=top_k)
        
        if not chunks:
            context = "Tidak ada informasi yang relevan ditemukan dalam manual."
        else:
            context, sources = self.context_builder.build_context_with_sources(chunks)
        
        # Generate answer with conversation history
        answer = self.answer_generator.chat_with_history(messages, context)
        
        return {
            'answer': answer,
            'sources': sources if chunks else [],
            'chunks_found': len(chunks)
        }
    
    def get_statistics(self) -> Dict:
        """Get statistics about the RAG system."""
        chunk_count_query = "SELECT COUNT(*) FROM document_chunks;"
        embedding_count_query = "SELECT COUNT(*) FROM chunk_embeddings;"
        page_count_query = "SELECT COUNT(DISTINCT page_number) FROM document_chunks;"
        
        chunk_count = self.db.execute_query(chunk_count_query, fetch=True)[0][0]
        embedding_count = self.db.execute_query(embedding_count_query, fetch=True)[0][0]
        page_count = self.db.execute_query(page_count_query, fetch=True)[0][0]
        
        return {
            'total_chunks': chunk_count,
            'total_embeddings': embedding_count,
            'total_pages': page_count,
            'embedding_dimension': 768
        }
    
    def close(self):
        """Close database connection."""
        self.db.close()
        print("✓ RAG Pipeline closed")