from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.article import ArticleDifficulty, ArticleStatus
from app.schemas.category import CategoryRead


class AuthorBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class ArticleBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    summary: Optional[str] = None
    content: str = Field(min_length=1)
    category_id: int
    status: ArticleStatus = ArticleStatus.draft
    difficulty: ArticleDifficulty = ArticleDifficulty.beginner
    estimated_reading_time: Optional[int] = Field(default=None, ge=1, le=120)
    thumbnail: Optional[str] = Field(default=None, max_length=500)
    tags: Optional[List[str]] = None
    slug: Optional[str] = Field(default=None, max_length=255)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        cleaned = [t.strip() for t in value if t and t.strip()]
        return cleaned or None


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    summary: Optional[str] = None
    content: Optional[str] = Field(default=None, min_length=1)
    category_id: Optional[int] = None
    status: Optional[ArticleStatus] = None
    difficulty: Optional[ArticleDifficulty] = None
    estimated_reading_time: Optional[int] = Field(default=None, ge=1, le=120)
    thumbnail: Optional[str] = Field(default=None, max_length=500)
    tags: Optional[List[str]] = None
    slug: Optional[str] = Field(default=None, max_length=255)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        cleaned = [t.strip() for t in value if t and t.strip()]
        return cleaned or None


class ArticleListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    difficulty: ArticleDifficulty
    estimated_reading_time: int
    thumbnail: Optional[str] = None
    tags: Optional[List[str]] = None
    status: ArticleStatus
    view_count: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    category: CategoryRead
    author: AuthorBrief


class ArticleDetail(ArticleListItem):
    content: str
    category_id: int
    author_id: int
