# context_builder.py
from typing import List, Dict
from services.similarity_search import SimilaritySearch

class ContextBuilder:
    def __init__(self, search: SimilaritySearch):
        self.search = search
    
    def build_context(
        self, 
        chunks: List[Dict],
        max_tokens: int = 2000
    ) -> str:
        """
        Build context string from retrieved chunks.
        
        Args:
            chunks: List of retrieved chunks with metadata
            max_tokens: Approximate max tokens (rough estimate: 4 chars = 1 token)
        
        Returns:
            Formatted context string
        """
        if not chunks:
            return "Tidak ada informasi yang relevan ditemukan dalam manual."
        
        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4  # Rough estimate
        
        for i, chunk in enumerate(chunks, 1):
            # Format chunk with metadata
            chunk_text = (
                f"[Sumber {i} - Halaman {chunk['page_number']}, "
                f"Bagian: {chunk['section_header']}]\n"
                f"{chunk['text']}\n"
            )
            
            # Check if adding this chunk would exceed limit
            if total_chars + len(chunk_text) > max_chars:
                break
            
            context_parts.append(chunk_text)
            total_chars += len(chunk_text)
        
        return "\n".join(context_parts)
    
    def build_context_with_sources(
        self,
        chunks: List[Dict],
        max_tokens: int = 2000
    ) -> tuple[str, List[Dict]]:
        """
        Build context and return separate source references.
        
        Returns:
            (context_string, source_list)
        """
        context = self.build_context(chunks, max_tokens)
        
        sources = []
        for chunk in chunks:
            sources.append({
                'page': chunk['page_number'],
                'section': chunk['section_header'],
                'similarity': chunk['similarity']
            })
        
        return context, sources
    
    def format_sources(self, sources: List[Dict]) -> str:
        """Format sources as a readable string."""
        if not sources:
            return ""
        
        source_lines = ["\n📚 Sumber informasi:"]
        
        for i, source in enumerate(sources, 1):
            source_lines.append(
                f"  {i}. Halaman {source['page']} - "
                f"{source['section']} "
                f"(relevansi: {source['similarity']:.2%})"
            )
        
        return "\n".join(source_lines)