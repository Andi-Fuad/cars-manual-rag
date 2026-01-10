# answer_generator.py
import google.generativeai as genai
from typing import Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class AnswerGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        
        # Use the correct Gemini model name
        # Updated model name for Gemini 
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
        
        # System instruction for car manual assistant
        self.system_instruction = """Anda adalah asisten virtual untuk manual mobil dalam Bahasa Indonesia. 
Tugas Anda:
1. Jawab pertanyaan berdasarkan konteks yang diberikan dari manual mobil
2. Jika informasi tidak ada dalam konteks, katakan dengan jelas
3. Berikan jawaban yang akurat, jelas, dan membantu
4. Sertakan referensi halaman jika relevan
5. Gunakan Bahasa Indonesia yang baik dan benar
6. Jika ada informasi keamanan penting, tekankan dengan jelas"""
     
    def generate_answer(
        self,
        query: str,
        context: str,
        include_sources: bool = True
    ) -> str:
        """
        Generate answer based on query and context.
        
        Args:
            query: User's question
            context: Retrieved context from manual
            include_sources: Whether to remind about checking sources
        
        Returns:
            Generated answer
        """
        # Build prompt
        prompt = f"""{self.system_instruction}

Konteks dari Manual Mobil:
{context}

Pertanyaan Pengguna:
{query}

Jawaban:"""
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text
            
            # Add source reminder if requested
            if include_sources and "Tidak ada informasi" not in context:
                answer += "\n\n💡 Tip: Periksa halaman yang disebutkan di atas untuk informasi lengkap."
            
            return answer
            
        except Exception as e:
            return f"Maaf, terjadi kesalahan saat menghasilkan jawaban: {str(e)}"
    
    def generate_with_safety_check(
        self,
        query: str,
        context: str
    ) -> Dict[str, str]:
        """
        Generate answer with safety and reliability checks.
        
        Returns dict with:
            - answer: The generated answer
            - confidence: Low/Medium/High based on context quality
            - warning: Any safety warnings if applicable
        """
        # Check context quality - updated thresholds
        if "Tidak ada informasi" in context:
            confidence = "Low"
        elif len(context) > 300:  # Adjusted threshold
            confidence = "High"
        else:
            confidence = "Medium"
        
        # Generate answer
        answer = self.generate_answer(query, context, include_sources=True)
        
        # Check for safety-critical topics
        safety_keywords = [
            'rem', 'brake', 'airbag', 'sabuk pengaman', 'kecelakaan',
            'kebakaran', 'gas', 'bensin', 'bahan bakar'
        ]
        
        warning = None
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in safety_keywords):
            warning = "⚠️ PENTING: Topik ini berkaitan dengan keselamatan. Selalu ikuti instruksi manual dengan teliti dan konsultasikan dengan mekanik profesional jika ragu."
        
        return {
            'answer': answer,
            'confidence': confidence,
            'warning': warning
        }

    def chat_with_history(
        self,
        messages: list[Dict[str, str]],
        context: str
    ) -> str:
        """
        Generate answer considering conversation history.
        
        Args:
            messages: List of {"role": "user/assistant", "content": "..."}
            context: Current context from retrieval
        
        Returns:
            Generated answer
        """
        # Build conversation prompt
        conversation = ""
        for msg in messages:
            role = "Pengguna" if msg["role"] == "user" else "Asisten"
            conversation += f"{role}: {msg['content']}\n\n"
        
        prompt = f"""{self.system_instruction}

Konteks dari Manual Mobil:
{context}

Riwayat Percakapan:
{conversation}

Jawaban:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Maaf, terjadi kesalahan: {str(e)}"