from typing import List, Dict
import re

class TextChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        chunk_size: target number of characters per chunk
        chunk_overlap: number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_by_characters(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Simple character-based chunking."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending within next 100 chars
                sentence_end = text.rfind('. ', end, end + 100)
                if sentence_end != -1:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_data = {
                    "text": chunk_text,
                    "start_char": start,
                    "end_char": end,
                    "chunk_size": len(chunk_text)
                }
                
                if metadata:
                    chunk_data.update(metadata)
                
                chunks.append(chunk_data)
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def chunk_by_paragraphs(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Chunk by paragraphs, combining small ones."""
        paragraphs = re.split(r'\n\n+', text)
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk_size, save current and start new
            if current_chunk and len(current_chunk) + len(para) > self.chunk_size:
                chunk_data = {
                    "text": current_chunk.strip(),
                    "chunk_size": len(current_chunk)
                }
                if metadata:
                    chunk_data.update(metadata)
                chunks.append(chunk_data)
                
                # Start new chunk with overlap (last sentence of previous)
                sentences = current_chunk.split('. ')
                if len(sentences) > 1:
                    current_chunk = sentences[-1] + '. ' + para
                else:
                    current_chunk = para
            else:
                current_chunk += ("\n\n" if current_chunk else "") + para
        
        # Add last chunk
        if current_chunk:
            chunk_data = {
                "text": current_chunk.strip(),
                "chunk_size": len(current_chunk)
            }
            if metadata:
                chunk_data.update(metadata)
            chunks.append(chunk_data)
        
        return chunks
    
    def chunk_sections(self, sections: List[Dict], page_num: int = None) -> List[Dict]:
        """Chunk sections from structured text."""
        all_chunks = []
        
        for section in sections:
            metadata = {
                "section_header": section["header"],
                "page_number": page_num
            }
            
            # Chunk the section content
            chunks = self.chunk_by_paragraphs(section["content"], metadata)
            all_chunks.extend(chunks)
        
        return all_chunks