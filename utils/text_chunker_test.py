# test_text_chunker.py
import pytest
from text_chunker import TextChunker
from text_cleaner import TextCleaner
from pdf_extractor import PDFExtractor

@pytest.fixture
def sample_text():
    return """This is the first paragraph about engine maintenance. It contains important information about oil changes and filter replacements.

This is the second paragraph discussing tire pressure. You should check your tire pressure monthly and maintain the recommended PSI levels.

This is the third paragraph about brake systems. Regular brake inspections are crucial for vehicle safety. The brake pads should be checked every 10,000 miles.

This is a fourth paragraph with more details about brake maintenance and when to replace brake fluid."""

def test_chunk_by_characters(sample_text):
    """Test character-based chunking."""
    chunker = TextChunker(chunk_size=150, chunk_overlap=30)
    chunks = chunker.chunk_by_characters(sample_text)
    
    assert len(chunks) > 0
    
    # Check overlap exists
    if len(chunks) > 1:
        # Last chars of chunk 0 should appear in chunk 1
        overlap_sample = chunks[0]["text"][-20:]
        assert overlap_sample in chunks[1]["text"]
    
    print(f"\n=== Character Chunking: {len(chunks)} chunks ===")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i} (size: {chunk['chunk_size']}) ---")
        print(chunk["text"][:100] + "...")

def test_chunk_by_paragraphs(sample_text):
    """Test paragraph-based chunking."""
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    chunks = chunker.chunk_by_paragraphs(sample_text)
    
    assert len(chunks) > 0
    
    print(f"\n=== Paragraph Chunking: {len(chunks)} chunks ===")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i} (size: {chunk['chunk_size']}) ---")
        print(chunk["text"])

def test_chunk_real_manual():
    """Test chunking with real car manual."""
    extractor = PDFExtractor("car_manual.pdf")
    cleaner = TextCleaner()
    chunker = TextChunker(chunk_size=800, chunk_overlap=150)
    
    # Process first page
    text_by_page = extractor.extract_text_by_page()
    page_0_text = text_by_page[0]
    
    # Clean and split into sections
    cleaned = cleaner.clean_text(page_0_text)
    sections = cleaner.split_into_sections(cleaned)
    
    # Chunk the sections
    chunks = chunker.chunk_sections(sections, page_num=0)
    
    print(f"\n=== Page 0: {len(chunks)} chunks created ===")
    for i, chunk in enumerate(chunks[:3]):  # Show first 3
        print(f"\n--- Chunk {i} ---")
        print(f"Section: {chunk.get('section_header', 'N/A')}")
        print(f"Size: {chunk['chunk_size']} chars")
        print(f"Text preview: {chunk['text'][:150]}...")
    
    # Verify metadata is attached
    assert all("section_header" in c for c in chunks)
    assert all("page_number" in c for c in chunks)
    
    extractor.close()

def test_chunk_size_consistency():
    """Test that chunks are within reasonable size bounds."""
    chunker = TextChunker(chunk_size=500, chunk_overlap=100)
    
    # Create a long text
    long_text = "This is a sentence. " * 200
    chunks = chunker.chunk_by_characters(long_text)
    
    for chunk in chunks:
        # Chunks should be roughly around chunk_size (with some flexibility)
        assert chunk["chunk_size"] <= chunker.chunk_size + 200  # Allow some overage for sentence breaks
        print(f"Chunk size: {chunk['chunk_size']}")

# Run with: pytest test_text_chunker.py -v -s