# demo_rag.py
from rag_pipeline import RAGPipeline
import sys

def main():
    print("="*60)
    print("🚗 Car Manual RAG System - Interactive Demo")
    print("="*60)
    
    # Initialize RAG
    print("\n⚙️ Initializing RAG Pipeline...")
    rag = RAGPipeline()
    
    # Show statistics
    stats = rag.get_statistics()
    print(f"\n📊 System Statistics:")
    print(f"  • Total chunks: {stats['total_chunks']}")
    print(f"  • Total pages: {stats['total_pages']}")
    
    if stats['total_chunks'] == 0:
        print("\n⚠️ No data found in database!")
        print("Please run: python process_manual.py car_manual.pdf --test")
        rag.close()
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("💬 You can now ask questions about your car manual!")
    print("Type 'quit' or 'exit' to stop")
    print("="*60)
    
    # Interactive loop
    while True:
        print(f"\n{'─'*60}")
        question = input("\n❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if not question:
            continue
        
        # Query the RAG system
        result = rag.query(question, top_k=5)
        
        # Display answer
        print(f"\n{'─'*60}")
        print(f"🤖 Answer:")
        print(f"{'─'*60}")
        print(result['answer'])
        
        # Display metadata
        print(f"\n📊 Metadata:")
        print(f"  • Confidence: {result['confidence']}")
        print(f"  • Chunks found: {result['chunks_found']}")
        
        # Display sources
        if result['sources']:
            print(f"\n📚 Sources:")
            for i, source in enumerate(result['sources'][:3], 1):
                print(f"  {i}. Page {source['page']} - {source['section']}")
                print(f"     Relevance: {source['similarity']:.1%}")
        
        # Display warning if any
        if result.get('warning'):
            print(f"\n{result['warning']}")
    
    print(f"\n{'='*60}")
    print("👋 Thank you for using Car Manual RAG!")
    print("="*60)
    
    rag.close()

if __name__ == "__main__":
    main()