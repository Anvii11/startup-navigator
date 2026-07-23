from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, delete, func, desc

from app.core.deps import CurrentUser, DbSession
from app.models.saved_article import SavedArticle
from app.models.article import Article
from app.models.chat import ChatSession, ChatMessage
from app.schemas.article import ArticleListItem

router = APIRouter(prefix="/user", tags=["user"])


class SavedIdeaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    saved_at: datetime
    article_id: int
    article: ArticleListItem


class DashboardOverviewResponse(BaseModel):
    saved_ideas_count: int
    ai_searches_count: int
    favourite_industry: Optional[str] = None
    recent_searches: List[Dict[str, Any]]
    recent_saved_ideas: List[SavedIdeaRead]


@router.get("/saved-ideas", response_model=List[SavedIdeaRead])
def get_saved_ideas(db: DbSession, current_user: CurrentUser):
    """
    Returns all saved startup ideas for the current authenticated user.
    """
    stmt = (
        select(SavedArticle)
        .where(SavedArticle.user_id == current_user.id)
        .order_by(desc(SavedArticle.saved_at))
    )
    saved_items = db.scalars(stmt).all()
    
    result = []
    for item in saved_items:
        if item.article and item.article.status == "published":
            result.append(
                SavedIdeaRead(
                    id=item.id,
                    saved_at=item.saved_at,
                    article_id=item.article_id,
                    article=ArticleListItem.model_validate(item.article)
                )
            )
    return result


@router.get("/saved-idea-ids", response_model=List[int])
def get_saved_idea_ids(db: DbSession, current_user: CurrentUser):
    """
    Returns list of article IDs saved by current authenticated user.
    """
    stmt = select(SavedArticle.article_id).where(SavedArticle.user_id == current_user.id)
    ids = db.scalars(stmt).all()
    return list(ids)


@router.post("/saved-ideas/{article_id}")
def save_idea(article_id: int, db: DbSession, current_user: CurrentUser):
    """
    Saves a startup idea for current user. Prevents duplicate saves.
    """
    article = db.get(Article, article_id)
    if not article or article.status != "published":
        raise HTTPException(status_code=404, detail="Idea not found")

    existing = db.scalar(
        select(SavedArticle).where(
            SavedArticle.user_id == current_user.id,
            SavedArticle.article_id == article_id
        )
    )
    if existing:
        return {"status": "already_saved", "saved_at": existing.saved_at}

    saved = SavedArticle(user_id=current_user.id, article_id=article_id)
    db.add(saved)
    try:
        db.commit()
        db.refresh(saved)
        return {"status": "saved", "saved_at": saved.saved_at}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not save idea")


@router.delete("/saved-ideas/{article_id}")
def remove_saved_idea(article_id: int, db: DbSession, current_user: CurrentUser):
    """
    Removes a startup idea from current user's saved list.
    """
    stmt = delete(SavedArticle).where(
        SavedArticle.user_id == current_user.id,
        SavedArticle.article_id == article_id
    )
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Saved idea not found")
    return {"status": "removed"}


@router.get("/dashboard", response_model=DashboardOverviewResponse)
def get_dashboard_overview(db: DbSession, current_user: CurrentUser):
    """
    Retrieves user dashboard metrics: saved ideas count, AI search count,
    recent searches, and favorite industry.
    """
    # 1. Saved ideas count & items
    stmt_saved = (
        select(SavedArticle)
        .where(SavedArticle.user_id == current_user.id)
        .order_by(desc(SavedArticle.saved_at))
    )
    saved_items = db.scalars(stmt_saved).all()
    saved_ideas_count = len(saved_items)

    recent_saved = []
    category_counts: Dict[str, int] = {}

    for item in saved_items[:6]:
        if item.article and item.article.status == "published":
            recent_saved.append(
                SavedIdeaRead(
                    id=item.id,
                    saved_at=item.saved_at,
                    article_id=item.article_id,
                    article=ArticleListItem.model_validate(item.article)
                )
            )
            cat_name = item.article.category.name if item.article.category else None
            if cat_name:
                category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

    # 2. AI searches count & recent chats
    stmt_chats = (
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(desc(ChatSession.updated_at))
    )
    chat_sessions = db.scalars(stmt_chats).all()
    ai_searches_count = len(chat_sessions)

    recent_searches = []
    for s in chat_sessions[:5]:
        recent_searches.append({
            "id": s.id,
            "title": s.title or "AI Search Query",
            "created_at": s.created_at,
            "updated_at": s.updated_at
        })

    # 3. Favourite Industry calculation
    favourite_industry = None
    if category_counts:
        favourite_industry = max(category_counts, key=category_counts.get)

    return DashboardOverviewResponse(
        saved_ideas_count=saved_ideas_count,
        ai_searches_count=ai_searches_count,
        favourite_industry=favourite_industry,
        recent_searches=recent_searches,
        recent_saved_ideas=recent_saved
    )
