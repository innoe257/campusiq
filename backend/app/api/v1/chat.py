from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models import ChatHistory
from app.services.rag_service import RAGService
import uuid

router = APIRouter()
rag_service = RAGService()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List
    session_id: str

class ChatHistoryItem(BaseModel):
    id: int
    message: str
    response: str
    sources: List
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/message", response_model=ChatResponse)
async def chat(
    request: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        response_text, sources = await rag_service.query(
            question=request.message,
            session_id=session_id,
        )
    except Exception as e:
        # Fallback response if RAG service fails (e.g., Ollama not ready)
        response_text = (
            "I apologize, but I'm currently unable to access the knowledge base. "
            "Please ensure the Ollama service is running and the knowledge documents have been ingested. "
            f"Technical details: {str(e)}"
        )
        sources = []
    
    # Save to history
    chat_record = ChatHistory(
        session_id=session_id,
        user_id=current_user.id,
        message=request.message,
        response=response_text,
        sources=sources,
    )
    db.add(chat_record)
    db.commit()
    
    return ChatResponse(
        response=response_text,
        sources=sources,
        session_id=session_id,
    )


@router.get("/history/{session_id}", response_model=List[ChatHistoryItem])
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id,
        ChatHistory.user_id == current_user.id,
    ).order_by(ChatHistory.created_at.asc()).all()
    
    return history


@router.post("/ingest")
async def ingest_knowledge(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ["admin", "faculty"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        count = await rag_service.ingest_documents()
        return {"status": "success", "documents_ingested": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
