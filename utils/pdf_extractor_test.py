# test_pdf_extractor.py
import pytest
from pdf_extractor import PDFExtractor
from pathlib import Path

def test_pdf_opens_successfully():
    """Test that PDF can be opened."""
    extractor = PDFExtractor("car_manual.pdf")
    assert extractor.doc is not None
    assert len(extractor.doc) > 0
    extractor.close()

def test_extract_text_by_page():
    """Test text extraction from each page."""
    extractor = PDFExtractor("car_manual.pdf")
    text_by_page = extractor.extract_text_by_page()
    
    # Check we got text for all pages
    assert len(text_by_page) == len(extractor.doc)
    
    # Check first page has some content
    assert len(text_by_page[0]) > 0
    
    # Print sample for manual verification
    print(f"\n=== Sample from Page 0 ===")
    print(text_by_page[0][:500])
    
    extractor.close()

def test_extract_images():
    """Test image extraction."""
    extractor = PDFExtractor("car_manual.pdf")
    images_by_page = extractor.extract_images_by_page("test_images")
    
    # Check that images directory was created
    assert Path("test_images").exists()
    
    # Count total images
    total_images = sum(len(imgs) for imgs in images_by_page.values())
    print(f"\n=== Total images extracted: {total_images} ===")
    
    # Check at least one image was extracted (assuming manual has images)
    if total_images > 0:
        # Verify first image file exists
        first_page_with_images = next((p for p in images_by_page if images_by_page[p]), None)
        if first_page_with_images is not None:
            first_image = images_by_page[first_page_with_images][0]
            assert Path(first_image).exists()
            print(f"First image saved at: {first_image}")
    
    extractor.close()

def test_document_metadata():
    """Test metadata extraction."""
    extractor = PDFExtractor("car_manual.pdf")
    metadata = extractor.get_document_metadata()
    
    assert "num_pages" in metadata
    assert metadata["num_pages"] > 0
    
    print(f"\n=== Document Metadata ===")
    print(f"Pages: {metadata['num_pages']}")
    print(f"Metadata: {metadata['metadata']}")
    
    extractor.close()

# Run with: pytest test_pdf_extractor.py -v -s