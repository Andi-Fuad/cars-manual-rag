# document_processor.py
from utils.pdf_extractor import PDFExtractor
from utils.text_cleaner import TextCleaner
from utils.text_chunker import TextChunker
from core.db_connection import DatabaseConnection
from schemas.database import DatabaseSchema
from services.embedding_generator import EmbeddingGenerator
from services.storage_manager import StorageManager
from typing import Dict, List
import time

class DocumentProcessor:
    def __init__(
        self, 
        pdf_path: str,
        chunk_size: int = 800,
        chunk_overlap: int = 150
    ):
        self.pdf_path = pdf_path
        self.extractor = PDFExtractor(pdf_path)
        self.cleaner = TextCleaner()
        self.chunker = TextChunker(chunk_size, chunk_overlap)
        
        # Database setup
        self.db = DatabaseConnection()
        self.db.connect()
        self.db.enable_pgvector()
        
        # Schema setup
        schema = DatabaseSchema(self.db)
        schema.create_tables()
        schema.create_indexes()
        
        # Storage setup
        self.embedder = EmbeddingGenerator()
        self.storage = StorageManager(self.db, self.embedder)
        
        # Statistics
        self.stats = {
            'total_pages': 0,
            'total_chunks': 0,
            'total_images': 0,
            'processing_time': 0
        }
    
    def process_page(self, page_num: int, page_text: str) -> List[Dict]:
        """Process a single page and return chunks."""
        # Clean text
        cleaned_text = self.cleaner.clean_text(page_text)
        
        # Split into sections
        sections = self.cleaner.split_into_sections(cleaned_text)
        
        # Chunk the sections
        chunks = self.chunker.chunk_sections(sections, page_num)
        
        return chunks
    
    def process_all_pages(
        self, 
        start_page: int = 0, 
        end_page: int = None,
        batch_size: int = 5,
        delay: float = 1.0
    ):
        """Process all pages and store in database."""
        start_time = time.time()
        
        # Get all text
        text_by_page = self.extractor.extract_text_by_page()
        total_pages = len(text_by_page)
        
        if end_page is None:
            end_page = total_pages
        
        print(f"\n{'='*60}")
        print(f"Processing pages {start_page} to {end_page} of {total_pages}")
        print(f"{'='*60}\n")
        
        all_chunks = []
        
        # Process each page
        for page_num in range(start_page, min(end_page, total_pages)):
            print(f"\n--- Page {page_num + 1}/{total_pages} ---")
            
            page_text = text_by_page[page_num]
            
            if not page_text.strip():
                print(f"  ⊘ Page {page_num} is empty, skipping")
                continue
            
            # Process page
            chunks = self.process_page(page_num, page_text)
            
            print(f"  ✓ Extracted {len(chunks)} chunks")
            
            all_chunks.extend(chunks)
        
        # Store all chunks in database
        print(f"\n{'='*60}")
        print(f"Storing {len(all_chunks)} chunks in database...")
        print(f"{'='*60}\n")
        
        results = self.storage.store_chunks_batch(
            all_chunks, 
            batch_size=batch_size,
            delay=delay
        )
        
        # Update statistics
        self.stats['total_pages'] = end_page - start_page
        self.stats['total_chunks'] = len(results)
        self.stats['processing_time'] = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"✓ Processing Complete!")
        print(f"{'='*60}")
        print(f"  Pages processed: {self.stats['total_pages']}")
        print(f"  Chunks created: {self.stats['total_chunks']}")
        print(f"  Processing time: {self.stats['processing_time']:.2f} seconds")
        print(f"  Average chunks/page: {self.stats['total_chunks']/self.stats['total_pages']:.1f}")
        print(f"{'='*60}\n")
        
        return results
    
    def process_images(self, output_dir: str = "extracted_images"):
        """Extract and store image metadata."""
        print(f"\n{'='*60}")
        print(f"Extracting images...")
        print(f"{'='*60}\n")
        
        images_by_page = self.extractor.extract_images_by_page(output_dir)
        
        total_images = 0
        for page_num, image_paths in images_by_page.items():
            for img_path in image_paths:
                self.storage.store_image(
                    page_number=page_num,
                    image_path=img_path,
                    image_description=None  # We'll add descriptions later
                )
                total_images += 1
        
        self.stats['total_images'] = total_images
        
        print(f"\n✓ Extracted and stored {total_images} images")
    
    def get_statistics(self) -> Dict:
        """Get processing statistics."""
        return self.stats
    
    def close(self):
        """Clean up resources."""
        self.extractor.close()
        self.db.close()
        print("\n✓ All resources closed")