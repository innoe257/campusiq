import os
import json
from typing import List, Tuple, Optional
import httpx
from sqlalchemy import create_engine, text
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import get_settings

settings = get_settings()

# Demo responses for when Ollama is not available
DEMO_RESPONSES = {
    "course": "I can help you find courses! Based on our catalog, popular options include CS101 (Intro to Programming), MATH201 (Calculus II), and PSYCH101 (Introduction to Psychology). Would you like details on any specific course?",
    "prerequisite": "Prerequisites vary by course. For example, CS201 requires CS101, and MATH301 requires MATH201. You can check the full course catalog for detailed prerequisite chains.",
    "career": "Our Career Services office offers resume reviews, mock interviews, and job placement assistance. Many Computer Science graduates find roles in software engineering, data science, and AI/ML engineering.",
    "gpa": "Your GPA is calculated by dividing total grade points by total credits attempted. Most programs require a minimum 2.0 GPA for good standing. If you need help improving your GPA, consider academic coaching or tutoring services.",
    "financial aid": "Financial aid options include scholarships, grants, work-study programs, and student loans. The Financial Aid office is located in Building C, Room 205. Deadlines for next semester are typically March 1st.",
    "withdraw": "Students may withdraw from courses through Week 8 with a 'W' grade. After Week 8, withdrawals require Dean approval. Full semester withdrawal requires advisor consultation.",
    "accommodation": "Students with disabilities should register with Accessibility Services. Documentation is required within 14 days of request.",
    "default": "I apologize, but I need more information to help with that. Could you rephrase your question or ask about specific courses, programs, policies, or career services?"
}


class RAGService:
    def __init__(self):
        self.embeddings = None
        self.ollama_host = settings.OLLAMA_HOST
        self.llm_model = settings.LLM_MODEL
        self.vector_dimension = settings.VECTOR_DIMENSION
        self.is_render = settings.RENDER
        
        # Only load embeddings if not on Render (saves memory)
        if not self.is_render:
            try:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=settings.EMBEDDING_MODEL,
                    model_kwargs={"device": "cpu"},
                )
            except Exception:
                self.embeddings = None
    
    async def ingest_documents(self) -> int:
        if self.is_render:
            # On Render, skip vector ingestion
            return 0
        
        knowledge_dir = "/app/knowledge_base"
        if not os.path.exists(knowledge_dir):
            knowledge_dir = "../knowledge_base"
        
        documents = []
        for filename in os.listdir(knowledge_dir):
            if filename.endswith(".md"):
                with open(os.path.join(knowledge_dir, filename), "r") as f:
                    content = f.read()
                    documents.append({
                        "id": filename.replace(".md", ""),
                        "content": content,
                        "metadata": {"source": filename, "type": "policy"},
                    })
        
        if not documents:
            return 0
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )
        
        chunks = []
        for doc in documents:
            splits = text_splitter.split_text(doc["content"])
            for i, split in enumerate(splits):
                chunks.append({
                    "document_id": f"{doc['id']}_chunk_{i}",
                    "content": split,
                    "metadata": {**doc["metadata"], "chunk_index": i},
                })
        
        # Generate embeddings
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embeddings.embed_documents(texts)
        
        # Store in pgvector
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM knowledge_embeddings"))
            conn.execute(text("""
                INSERT INTO knowledge_embeddings (document_id, content, metadata, embedding)
                VALUES (:document_id, :content, :metadata, :embedding)
            """), [
                {
                    "document_id": chunk["document_id"],
                    "content": chunk["content"],
                    "metadata": json.dumps(chunk["metadata"]),
                    "embedding": json.dumps(emb),
                }
                for chunk, emb in zip(chunks, embeddings)
            ])
            conn.commit()
        
        return len(chunks)
    
    async def query(self, question: str, session_id: str) -> Tuple[str, List]:
        # If on Render or Ollama not available, use demo mode
        if self.is_render or not self.ollama_host or not self.embeddings:
            return self._demo_response(question)
        
        # Full RAG pipeline (local dev only)
        query_embedding = self.embeddings.embed_query(question)
        
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT document_id, content, metadata, 
                       1 - (embedding <=> :embedding) as similarity
                FROM knowledge_embeddings
                ORDER BY embedding <=> :embedding
                LIMIT 5
            """), {"embedding": json.dumps(query_embedding)})
            
            docs = result.fetchall()
        
        if not docs:
            return "I don't have specific information about that in my knowledge base. Please try rephrasing or contact the student services office.", []
        
        context_parts = []
        sources = []
        for doc in docs:
            if doc.similarity > 0.3:
                context_parts.append(f"Document: {doc.document_id}\n{doc.content}")
                sources.append({
                    "document_id": doc.document_id,
                    "content": doc.content[:200] + "...",
                    "similarity": float(doc.similarity),
                })
        
        if not context_parts:
            return "I couldn't find relevant information for your question. Please try a different query.", []
        
        context = "\n\n---\n\n".join(context_parts)
        
        prompt = f"""You are CampusIQ, an AI academic advisor for a university. Answer the student's question based ONLY on the provided context. If the answer isn't in the context, say so clearly. Be concise, accurate, and helpful.

Context:
{context}

Question: {question}

Answer:"""
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.llm_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.3, "num_predict": 500},
                    },
                    timeout=60.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("response", "No response generated")
                else:
                    answer = f"Error: LLM service returned status {response.status_code}"
            except Exception as e:
                answer = f"Error connecting to LLM service: {str(e)}. Please ensure Ollama is running with model '{self.llm_model}' loaded."
        
        return answer, sources
    
    def _demo_response(self, question: str) -> Tuple[str, List]:
        """Return intelligent demo responses when LLM/RAG is unavailable."""
        lower_q = question.lower()
        
        for keyword, response in DEMO_RESPONSES.items():
            if keyword in lower_q:
                return response, [{"document_id": "demo_mode", "similarity": 1.0}]
        
        # Check for specific course codes
        import re
        course_codes = re.findall(r'[A-Z]{2,4}\d{3}', question.upper())
        if course_codes:
            return f"I see you're asking about {', '.join(course_codes)}. These courses are in our catalog. For detailed information including prerequisites and scheduling, please check the course catalog or speak with your academic advisor.", [{"document_id": "course_catalog", "similarity": 0.9}]
        
        return DEMO_RESPONSES["default"], []
