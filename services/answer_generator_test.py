# test_answer_generator.py
import pytest
from services.answer_generator import AnswerGenerator
import os

@pytest.fixture
def generator():
    """Create answer generator."""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")
    
    return AnswerGenerator()

def test_generate_basic_answer(generator):
    """Test basic answer generation."""
    query = "Berapa kapasitas mesin mobil ini?"
    context = """[Sumber 1 - Halaman 5, Bagian: BAB 2: Spesifikasi Mesin]
Mesin kendaraan ini memiliki kapasitas 1500cc dengan teknologi fuel injection modern."""
    
    answer = generator.generate_answer(query, context)
    
    assert len(answer) > 0
    assert "1500cc" in answer or "1500" in answer
    
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    print(f"Context: {context}")
    print(f"{'='*60}")
    print(f"Answer: {answer}")
    print(f"{'='*60}")

def test_no_context_answer(generator):
    """Test answer when no relevant context."""
    query = "Bagaimana cara membuat nasi goreng?"
    context = "Tidak ada informasi yang relevan ditemukan dalam manual."
    
    answer = generator.generate_answer(query, context)
    
    assert len(answer) > 0
    print(f"\n{'='*60}")
    print(f"Query (irrelevant): {query}")
    print(f"{'='*60}")
    print(f"Answer: {answer}")
    print(f"{'='*60}")

def test_answer_with_safety_check(generator):
    """Test answer generation with safety check."""
    query = "Bagaimana cara memeriksa rem?"
    context = """[Sumber 1 - Halaman 15, Bagian: BAB 4: Sistem Keamanan]
Sistem rem ABS memberikan kontrol maksimal saat pengereman darurat. Periksa rem secara berkala setiap 10,000 km."""
    
    result = generator.generate_with_safety_check(query, context)
    
    assert 'answer' in result
    assert 'confidence' in result
    assert 'warning' in result
    assert result['warning'] is not None  # Should have warning for brake-related query
    
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    print(f"Confidence: {result['confidence']}")
    print(f"Answer: {result['answer']}")
    if result['warning']:
        print(f"\n{result['warning']}")
    print(f"{'='*60}")

def test_chat_with_history(generator):
    """Test multi-turn conversation."""
    context = """[Sumber 1 - Halaman 10, Bagian: BAB 3: Perawatan]
Ganti oli mesin setiap 5000 km atau 6 bulan. Gunakan oli dengan viskositas 10W-40."""
    
    messages = [
        {"role": "user", "content": "Kapan harus ganti oli?"},
        {"role": "assistant", "content": "Oli mesin harus diganti setiap 5000 km atau 6 bulan."},
        {"role": "user", "content": "Oli apa yang direkomendasikan?"}
    ]
    
    answer = generator.chat_with_history(messages, context)
    
    assert len(answer) > 0
    assert "10W-40" in answer or "10W" in answer
    print(f"\n{'='*60}")
    print("Chat History:")
    print(f"{'='*60}")
    for msg in messages:
        print(f"{msg['role'].upper()}: {msg['content']}")
    print(f"\n{'='*60}")
    print(f"Answer: {answer}")
    print(f"{'='*60}")

def test_confidence_levels(generator):
    """Test confidence assessment."""
    # Low confidence - no context
    result_low = generator.generate_with_safety_check(
    "test",
    "Tidak ada informasi yang relevan ditemukan dalam manual."
    )
    assert result_low['confidence'] == "Low"
    # Medium confidence - short context
    result_med = generator.generate_with_safety_check(
        "test",
        "Mesin 1500cc."
    )
    assert result_med['confidence'] == "Medium"

    # High confidence - long context
    result_high = generator.generate_with_safety_check(
        "test",
        "Mesin kendaraan ini memiliki kapasitas 1500cc dengan teknologi fuel injection modern yang efisien. " * 5
    )
    assert result_high['confidence'] == "High"

    print(f"\n{'='*60}")
    print("Confidence Levels:")
    print(f"{'='*60}")
    print(f"Low: {result_low['confidence']}")
    print(f"Medium: {result_med['confidence']}")
    print(f"High: {result_high['confidence']}")