# scripts/process_document.py
"""
Script to process car manual - works both locally and in Docker
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.document_processor import DocumentProcessor

def main():
    print("="*60)
    print("🚗 Car Manual RAG - Document Processor")
    print("="*60)
    
    # Check for PDF file - try multiple locations
    possible_paths = [
        "/app/data/car_manual.pdf",  # Docker path
        "./data/car_manual.pdf",      # Local path
        "data/car_manual.pdf",        # Alternative local
    ]
    
    pdf_path = None
    for path in possible_paths:
        if os.path.exists(path):
            pdf_path = path
            break
    
    if not pdf_path:
        print(f"\n❌ Error: car_manual.pdf not found!")
        print("\nSearched in:")
        for path in possible_paths:
            print(f"  • {path}")
        print("\nPlease place your car_manual.pdf in the ./data/ directory")
        sys.exit(1)
    
    print(f"\n📄 Found PDF: {pdf_path}")
    
    # Ask for processing mode
    print("\nProcessing options:")
    print("  1. Test mode (first 5 pages)")
    print("  2. Partial (first 20 pages)")
    print("  3. Medium (first 50 pages)")
    print("  4. Full document")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice not in ['1', '2', '3', '4']:
        print("❌ Invalid choice. Exiting.")
        sys.exit(1)
    
    # Create processor
    print("\n⚙️ Initializing processor...")
    processor = DocumentProcessor(
        pdf_path=pdf_path,
        chunk_size=800,
        chunk_overlap=150
    )
    
    try:
        if choice == "1":
            print("\n🧪 Processing first 5 pages (test mode)...")
            processor.process_all_pages(start_page=0, end_page=5, batch_size=3, delay=1.0)
        elif choice == "2":
            print("\n📚 Processing first 20 pages...")
            processor.process_all_pages(start_page=0, end_page=20, batch_size=5, delay=1.0)
        elif choice == "3":
            print("\n📚 Processing first 50 pages...")
            processor.process_all_pages(start_page=0, end_page=50, batch_size=5, delay=1.0)
        elif choice == "4":
            print("\n📚 Processing entire document...")
            print("⚠️ This may take a while depending on document size...")
            processor.process_all_pages(batch_size=5, delay=1.0)
        
        # Ask about images
        print("\n" + "="*60)
        process_images = input("📷 Process images? (y/n): ").strip().lower()
        if process_images == 'y':
            processor.process_images()
        
        # Show statistics
        stats = processor.get_statistics()
        print(f"\n{'='*60}")
        print(f"✅ Processing Complete!")
        print(f"{'='*60}")
        print(f"  Pages processed: {stats['total_pages']}")
        print(f"  Chunks created: {stats['total_chunks']}")
        print(f"  Images extracted: {stats['total_images']}")
        print(f"  Processing time: {stats['processing_time']:.2f}s")
        
        if stats['total_chunks'] > 0:
            print(f"  Avg chunks/page: {stats['total_chunks']/stats['total_pages']:.1f}")
        
        print(f"{'='*60}")
        print("\n✅ You can now use the RAG system!")
        print("Run: python manage.py demo")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        processor.close()

if __name__ == "__main__":
    main()