from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, ConfigDict
import jwt

from app.core.deps import CurrentUser, DbSession
from app.models.chat import ChatSession, ChatMessage
from app.models.user import User
from app.rag.service import RAGService

router = APIRouter(prefix="/ai", tags=["ai"])
bearer_scheme = HTTPBearer(auto_error=False)

# ---------- Pydantic Schemas ----------

class AIAskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The query to ask the startup assistant.")
    session_id: Optional[int] = Field(None, description="Optional active session ID to append conversation.")

class SourceCitation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    slug: str
    url: str
    score: float

class AIAskResponse(BaseModel):
    session_id: int
    session_title: str
    answer: str
    sources: List[SourceCitation]
    latency_ms: int

class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    content: str
    sources_json: Optional[Any] = None
    created_at: datetime

class ChatSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: Optional[int]
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[ChatMessageRead]] = None

class AIDeleteResponse(BaseModel):
    status: str
    message: str

# ---------- Optional Auth Helper ----------

def get_optional_current_user(
    db: DbSession,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[User]:
    """
    Parses and returns the logged-in User if valid Authorization Bearer header is present.
    Returns None for anonymous sessions without raising 401.
    """
    if credentials is None or not credentials.credentials:
        return None
    try:
        from app.core.security import decode_token
        token = credentials.credentials
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user = db.get(User, int(user_id))
        if user and user.is_active:
            return user
    except jwt.PyJWTError:
        pass
    except Exception:
        pass
    return None

# ---------- Endpoints ----------

@router.post("/ask", response_model=AIAskResponse)
def ask_question(
    payload: AIAskRequest,
    db: DbSession,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Asks the AI assistant a startup query grounded in startup ideas.
    Supports authenticated and anonymous users.
    """
    user_id = current_user.id if current_user else None
    try:
        result = RAGService.query_assistant(
            db=db,
            question=payload.question,
            session_id=payload.session_id,
            user_id=user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in RAG pipeline: {str(e)}"
        )

@router.get("/sessions", response_model=List[ChatSessionRead])
def list_sessions(
    db: DbSession,
    current_user: CurrentUser
):
    """
    Lists all chat sessions belonging to the current authenticated user with messages.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    stmt = (
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .options(selectinload(ChatSession.messages))
        .order_by(ChatSession.updated_at.desc())
    )
    sessions = db.scalars(stmt).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=ChatSessionRead)
def get_session(
    session_id: int,
    db: DbSession,
    current_user: CurrentUser
):
    """
    Gets details and messages for a single chat session belonging to the user.
    """
    session = db.get(ChatSession, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or access denied"
        )
    return session

@router.delete("/sessions/{session_id}", response_model=AIDeleteResponse)
def delete_session(
    session_id: int,
    db: DbSession,
    current_user: CurrentUser
):
    """
    Deletes an active chat session belonging to the current user.
    """
    session = db.get(ChatSession, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or access denied"
        )
    
    try:
        db.delete(session)
        db.commit()
        return AIDeleteResponse(status="ok", message="Chat session successfully deleted")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete session: {str(e)}"
        )
