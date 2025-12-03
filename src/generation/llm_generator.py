"""LLM-based answer generation using Groq"""
from groq import Groq
import os

class MedicalAnswerGenerator:
    def __init__(self, api_key=None, model="llama-3.1-70b-versatile"):
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model = model
    
    def generate_answer(self, query, context_docs, max_tokens=512):
        """Generate answer using retrieved context"""
        
        # Build context from documents
        context = ""
        for i, doc in enumerate(context_docs[:5], 1):
            context += f"[Source {i}]: {doc['title']}\n"
            context += f"{doc['text'][:500]}...\n\n"
        
        # System prompt
        system_prompt = """You are a medical AI assistant. Answer questions using ONLY the provided context from medical literature.

Guidelines:
1. Be precise and evidence-based
2. Cite sources using [Source X] notation  
3. If information is insufficient, state limitations
4. Use medical terminology appropriately
5. Never make definitive diagnoses
6. Always recommend consulting healthcare professionals
"""
        
        # User prompt
        user_prompt = f"""Context:
{context}

Question: {query}

Answer (cite sources):"""
        
        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=max_tokens,
            top_p=0.9
        )
        
        answer = response.choices[0].message.content
        
        return {
            'answer': answer,
            'sources': context_docs[:5],
            'model': self.model
        }

if __name__ == "__main__":
    # Test
    generator = MedicalAnswerGenerator()
    
    test_docs = [{
        'title': 'Diabetes Management',
        'text': 'Metformin is first-line therapy for type 2 diabetes...',
        'score': 0.95
    }]
    
    result = generator.generate_answer(
        "What is first-line treatment for diabetes?",
        test_docs
    )
    
    print(result['answer'])
