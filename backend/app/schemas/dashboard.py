from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.article import ArticleListItem


class SavedIdeaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    saved_at: datetime
    article: ArticleListItem


class DashboardStats(BaseModel):
    total_ai_searches: int
    reading_progress_percent: float
    most_read_category: Optional[str] = None
    recent_chats: List[dict]
    saved_ideas: List[ArticleListItem]
    recently_viewed: List[ArticleListItem]
