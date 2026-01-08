# test_text_cleaner.py
import pytest
from text_cleaner import TextCleaner
from pdf_extractor import PDFExtractor

@pytest.fixture
def sample_dirty_text():
    """Sample text with common PDF extraction issues."""
    return """

CHAPTER 1    

Introduction  to   Your  Vehicle


This    is   a    sample    paragraph    with    extra
spaces   and   line-
breaks.



42



CHAPTER 2

Engine   Specifications

"""

@pytest.fixture
def sample_indonesian_text():
    """Sample Bahasa Indonesia text."""
    return """

BAB 1

Pengenalan Kendaraan Anda


Ini    adalah   contoh    paragraf    dengan   spasi
berlebih   dan   per-
pindahan baris.



15



BAB 2

Spesifikasi Mesin

Mesin kendaraan ini memiliki kapasitas 1500cc.

"""

def test_clean_text(sample_dirty_text):
    """Test basic text cleaning."""
    cleaner = TextCleaner()
    cleaned = cleaner.clean_text(sample_dirty_text)
    
    # Check NO triple newlines exist
    assert '\n\n\n' not in cleaned, f"Triple newlines found in: {repr(cleaned)}"
    
    # Check multiple spaces are removed
    assert '   ' not in cleaned
    
    # Check hyphenated word is fixed
    assert 'line-\nbreaks' not in cleaned
    
    # Should have some double newlines (paragraph breaks)
    assert '\n\n' in cleaned
    
    print(f"\n=== Original ===\n{repr(sample_dirty_text)}")
    print(f"\n=== Cleaned ===\n{repr(cleaned)}")
    print(f"\n=== Cleaned (pretty) ===\n{cleaned}")

def test_clean_indonesian_text(sample_indonesian_text):
    """Test cleaning Bahasa Indonesia text."""
    cleaner = TextCleaner()
    cleaned = cleaner.clean_text(sample_indonesian_text)
    
    assert '\n\n\n' not in cleaned
    assert '   ' not in cleaned
    assert 'BAB 1' in cleaned
    assert 'BAB 2' in cleaned
    
    print(f"\n=== Indonesian Text (cleaned) ===\n{cleaned}")

def test_identify_headers(sample_dirty_text):
    """Test header identification."""
    cleaner = TextCleaner()
    cleaned = cleaner.clean_text(sample_dirty_text)
    headers = cleaner.identify_headers(cleaned)
    
    # Should find the CHAPTER headers
    assert len(headers) >= 2
    assert any('CHAPTER 1' in h[1] for h in headers)
    assert any('CHAPTER 2' in h[1] for h in headers)
    
    print(f"\n=== Found Headers ===")
    for line_num, header in headers:
        print(f"Line {line_num}: {header}")

def test_identify_indonesian_headers(sample_indonesian_text):
    """Test header identification for Indonesian text."""
    cleaner = TextCleaner()
    cleaned = cleaner.clean_text(sample_indonesian_text)
    headers = cleaner.identify_headers(cleaned)
    
    # Should find the BAB headers
    assert len(headers) >= 2
    assert any('BAB 1' in h[1] for h in headers)
    assert any('BAB 2' in h[1] for h in headers)
    
    print(f"\n=== Found Indonesian Headers ===")
    for line_num, header in headers:
        print(f"Line {line_num}: {header}")

def test_split_into_sections(sample_dirty_text):
    """Test section splitting."""
    cleaner = TextCleaner()
    cleaned = cleaner.clean_text(sample_dirty_text)
    sections = cleaner.split_into_sections(cleaned)
    
    # Should have sections based on headers
    assert len(sections) >= 2
    
    print(f"\n=== Sections Found: {len(sections)} ===")
    for i, section in enumerate(sections):
        print(f"\n--- Section {i} ---")
        print(f"Header: {section['header']}")
        print(f"Content preview: {section['content'][:100] if len(section['content']) > 100 else section['content']}")

def test_split_indonesian_sections(sample_indonesian_text):
    """Test section splitting for Indonesian text."""
    cleaner = TextCleaner()
    cleaned = cleaner.clean_text(sample_indonesian_text)
    sections = cleaner.split_into_sections(cleaned)
    
    assert len(sections) >= 2
    
    print(f"\n=== Indonesian Sections: {len(sections)} ===")
    for i, section in enumerate(sections):
        print(f"\n--- Bagian {i} ---")
        print(f"Judul: {section['header']}")
        print(f"Isi: {section['content'][:150] if len(section['content']) > 150 else section['content']}")

def test_with_real_pdf():
    """Test with actual car manual."""
    # Only run if PDF exists
    import os
    if not os.path.exists("car_manual.pdf"):
        pytest.skip("car_manual.pdf not found")
    
    extractor = PDFExtractor("car_manual.pdf")
    cleaner = TextCleaner()
    
    # Get first 3 pages
    text_by_page = extractor.extract_text_by_page()
    
    for page_num in range(min(3, len(text_by_page))):
        print(f"\n{'='*50}")
        print(f"HALAMAN {page_num}")  # Page in Indonesian
        print('='*50)
        
        raw_text = text_by_page[page_num]
        cleaned_text = cleaner.clean_text(raw_text)
        
        # Verify no triple newlines
        assert '\n\n\n' not in cleaned_text, f"Triple newlines found on page {page_num}"
        
        print(f"\n--- Raw (first 300 chars) ---")
        print(raw_text[:300])
        
        print(f"\n--- Cleaned (first 300 chars) ---")
        print(cleaned_text[:300])
        
        # Identify headers on this page
        headers = cleaner.identify_headers(cleaned_text)
        if headers:
            print(f"\n--- Headers found on page {page_num} ---")
            for _, header in headers:
                print(f"  • {header}")
    
    extractor.close()

# Run with: pytest test_text_cleaner.py -v -s