"""Import all models so Alembic and Base.metadata see them."""

from app.db.base import Base
from app.models.user import User
from app.models.category import Category
from app.models.article import Article
from app.models.resource import Resource
from app.models.saved_article import SavedArticle
from app.models.chat import ChatSession, ChatMessage
from app.models.search_log import SearchLog
from app.models.contact import ContactMessage

__all__ = [
    "Base",
    "User",
    "Category",
    "Article",
    "Resource",
    "SavedArticle",
    "ChatSession",
    "ChatMessage",
    "SearchLog",
    "ContactMessage",
]
