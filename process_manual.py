# process_manual.py
from services.document_processor import DocumentProcessor
import sys

def main():
    # Check if PDF path is provided
    if len(sys.argv) < 2:
        print("Usage: python process_manual.py <path_to_car_manual.pdf>")
        print("\nOptions:")
        print("  --test : Process only first 3 pages for testing")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    test_mode = '--test' in sys.argv
    
    print(f"\n🚗 Car Manual RAG - Document Processor")
    print(f"{'='*60}")
    print(f"PDF: {pdf_path}")
    print(f"Mode: {'TEST (first 3 pages)' if test_mode else 'FULL DOCUMENT'}")
    print(f"{'='*60}\n")
    
    # Create processor
    processor = DocumentProcessor(
        pdf_path=pdf_path,
        chunk_size=800,
        chunk_overlap=150
    )
    
    try:
        # Process pages
        if test_mode:
            # Process only first 3 pages for testing
            processor.process_all_pages(
                start_page=0,
                end_page=3,
                batch_size=3,
                delay=1.0
            )
        else:
            # Process entire document
            processor.process_all_pages(
                batch_size=5,
                delay=1.0
            )
        
        # Optionally process images
        process_images = input("\nProcess images? (y/n): ").strip().lower()
        if process_images == 'y':
            processor.process_images()
        
        # Show final statistics
        stats = processor.get_statistics()
        print(f"\n📊 Final Statistics:")
        print(f"  Total pages: {stats['total_pages']}")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Total images: {stats['total_images']}")
        print(f"  Processing time: {stats['processing_time']:.2f} seconds")
        
    finally:
        processor.close()

if __name__ == "__main__":
    main()