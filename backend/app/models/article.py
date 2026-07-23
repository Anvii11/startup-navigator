import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.saved_article import SavedArticle


class ArticleStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class ArticleDifficulty(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus, name="article_status", native_enum=False),
        default=ArticleStatus.draft,
        nullable=False,
        index=True,
    )
    difficulty: Mapped[ArticleDifficulty] = mapped_column(
        Enum(ArticleDifficulty, name="article_difficulty", native_enum=False),
        default=ArticleDifficulty.beginner,
        nullable=False,
        index=True,
    )
    estimated_reading_time: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    thumbnail: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    category: Mapped["Category"] = relationship(back_populates="articles")
    author: Mapped["User"] = relationship(back_populates="articles")
    saved_by: Mapped[List["SavedArticle"]] = relationship(back_populates="article")
