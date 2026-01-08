# test_embedding_generator.py
import pytest
from embedding_generator import EmbeddingGenerator
import os

@pytest.fixture
def embedder():
    """Create embedding generator instance."""
    # Check if API key exists
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")
    
    return EmbeddingGenerator()

def test_embedding_generator_initialization(embedder):
    """Test that embedding generator initializes correctly."""
    assert embedder is not None
    assert embedder.model_name == "models/text-embedding-004"
    print("\n✓ Embedding generator initialized")

def test_generate_single_embedding(embedder):
    """Test generating a single embedding."""
    text = "Mesin kendaraan ini memiliki kapasitas 1500cc."
    
    embedding = embedder.generate_text_embedding(text)
    
    # Check embedding is a list of floats
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)
    
    print(f"\n✓ Generated embedding")
    print(f"  Dimension: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")
    print(f"  Embedding type: {type(embedding[0])}")

def test_embedding_dimension(embedder):
    """Test that embedding dimension is 768."""
    dimension = embedder.get_embedding_dimension()
    
    assert dimension == 768, f"Expected 768 dimensions, got {dimension}"
    print(f"\n✓ Embedding dimension confirmed: {dimension}")

def test_different_texts_different_embeddings(embedder):
    """Test that different texts produce different embeddings."""
    text1 = "Mesin mobil sangat kuat."
    text2 = "Rem harus diperiksa secara berkala."
    
    emb1 = embedder.generate_text_embedding(text1)
    emb2 = embedder.generate_text_embedding(text2)
    
    # Embeddings should be different
    assert emb1 != emb2
    print(f"\n✓ Different texts produce different embeddings")

def test_similar_texts_similar_embeddings(embedder):
    """Test that similar texts produce similar embeddings."""
    import numpy as np
    
    text1 = "Mesin mobil memerlukan oli."
    text2 = "Mobil membutuhkan oli mesin."
    text3 = "Cuaca hari ini cerah sekali."
    
    emb1 = embedder.generate_text_embedding(text1)
    emb2 = embedder.generate_text_embedding(text2)
    emb3 = embedder.generate_text_embedding(text3)
    
    # Calculate cosine similarity
    def cosine_similarity(a, b):
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    sim_1_2 = cosine_similarity(emb1, emb2)
    sim_1_3 = cosine_similarity(emb1, emb3)
    
    print(f"\n✓ Similarity test results:")
    print(f"  '{text1}' vs '{text2}': {sim_1_2:.4f}")
    print(f"  '{text1}' vs '{text3}': {sim_1_3:.4f}")
    
    # Similar texts should have higher similarity
    assert sim_1_2 > sim_1_3

def test_generate_batch_embeddings(embedder):
    """Test batch embedding generation."""
    texts = [
        "Periksa tekanan ban secara rutin.",
        "Ganti oli setiap 5000 km.",
        "Sistem rem harus diperiksa berkala.",
        "Gunakan bahan bakar yang direkomendasikan.",
    ]
    
    embeddings = embedder.generate_batch_embeddings(
        texts, 
        batch_size=2,
        delay=0.5
    )
    
    assert len(embeddings) == len(texts)
    assert all(len(emb) == 768 for emb in embeddings)
    
    print(f"\n✓ Generated {len(embeddings)} embeddings in batch")

def test_query_vs_document_embedding(embedder):
    """Test difference between query and document embeddings."""
    text = "Mesin mobil memerlukan perawatan berkala."
    
    doc_emb = embedder.generate_text_embedding(text, task_type="RETRIEVAL_DOCUMENT")
    query_emb = embedder.generate_query_embedding(text)
    
    # Both should be valid embeddings
    assert len(doc_emb) == 768
    assert len(query_emb) == 768
    
    # They might be slightly different due to different task types
    print(f"\n✓ Document and query embeddings generated")
    print(f"  Document embedding sample: {doc_emb[:3]}")
    print(f"  Query embedding sample: {query_emb[:3]}")

# Run with: pytest test_embedding_generator.py -v -s