import os
import json
import asyncio
from typing import List, Tuple, Optional
import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import get_settings

settings = get_settings()

class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )
        self.ollama_host = settings.OLLAMA_HOST
        self.llm_model = settings.LLM_MODEL
        self.vector_dimension = settings.VECTOR_DIMENSION
    
    async def ingest_documents(self) -> int:
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
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(question)
        
        # Search vector store
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
        
        # Build context
        context_parts = []
        sources = []
        for doc in docs:
            if doc.similarity > 0.3:  # Similarity threshold
                context_parts.append(f"Document: {doc.document_id}\n{doc.content}")
                sources.append({
                    "document_id": doc.document_id,
                    "content": doc.content[:200] + "...",
                    "similarity": float(doc.similarity),
                })
        
        if not context_parts:
            return "I couldn't find relevant information for your question. Please try a different query.", []
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Build prompt for Ollama
        prompt = f"""You are CampusIQ, an AI academic advisor for a university. Answer the student's question based ONLY on the provided context. If the answer isn't in the context, say so clearly. Be concise, accurate, and helpful.

Context:
{context}

Question: {question}

Answer:"""
        
        # Call Ollama
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
