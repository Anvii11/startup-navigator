from datetime import datetime, timezone
from math import ceil
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.article import Article, ArticleDifficulty, ArticleStatus
from app.models.category import Category
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.utils.slug import estimate_reading_time, slugify


class ArticleService:
    @staticmethod
    def _unique_slug(db: Session, base: str, *, exclude_id: Optional[int] = None) -> str:
        slug = slugify(base)
        candidate = slug
        counter = 2
        while True:
            stmt = select(Article).where(Article.slug == candidate)
            if exclude_id is not None:
                stmt = stmt.where(Article.id != exclude_id)
            if not db.scalar(stmt):
                return candidate
            candidate = f"{slug}-{counter}"
            counter += 1

    @staticmethod
    def _base_query(*, include_drafts: bool = False):
        stmt = select(Article).options(
            selectinload(Article.category),
            selectinload(Article.author),
        )
        if not include_drafts:
            stmt = stmt.where(Article.status == ArticleStatus.published)
        return stmt

    @staticmethod
    def list_articles(
        db: Session,
        *,
        page: int = 1,
        page_size: int = 12,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        category_slug: Optional[str] = None,
        difficulty: Optional[ArticleDifficulty] = None,
        status: Optional[ArticleStatus] = None,
        tag: Optional[str] = None,
        sort: str = "newest",
        include_drafts: bool = False,
        featured_only: bool = False,
        trending: bool = False,
    ) -> tuple[list[Article], int]:
        filters = []
        if not include_drafts:
            filters.append(Article.status == ArticleStatus.published)
        elif status is not None:
            filters.append(Article.status == status)

        if category_id is not None:
            filters.append(Article.category_id == category_id)
        if category_slug:
            cat = db.scalar(select(Category).where(Category.slug == category_slug))
            if cat is None:
                return [], 0
            filters.append(Article.category_id == cat.id)
        if difficulty is not None:
            filters.append(Article.difficulty == difficulty)
        if search:
            term = f"%{search.strip()}%"
            filters.append(
                or_(
                    Article.title.ilike(term),
                    Article.summary.ilike(term),
                    Article.content.ilike(term),
                )
            )
        if tag:
            from sqlalchemy import String, cast

            tag_expr = cast(Article.tags, String)
            filters.append(or_(tag_expr.ilike(f"%{tag}%"), tag_expr.ilike(f'%"{tag}"%')))

        count_stmt = select(func.count()).select_from(Article)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = db.scalar(count_stmt) or 0

        stmt = ArticleService._base_query(include_drafts=include_drafts)
        if filters:
            # Rebuild carefully for drafts inclusion
            stmt = select(Article).options(
                selectinload(Article.category),
                selectinload(Article.author),
            ).where(*filters)

        if trending or sort == "trending":
            stmt = stmt.order_by(Article.view_count.desc(), Article.published_at.desc().nullslast())
        elif sort == "oldest":
            stmt = stmt.order_by(Article.published_at.asc().nullslast(), Article.created_at.asc())
        elif sort == "title":
            stmt = stmt.order_by(Article.title.asc())
        else:
            stmt = stmt.order_by(Article.published_at.desc().nullslast(), Article.created_at.desc())

        if featured_only:
            # Use highest view published as featured selection at query time
            stmt = stmt.order_by(Article.view_count.desc()).limit(1)
            items = list(db.scalars(stmt).all())
            return items, len(items)

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        items = list(db.scalars(stmt).all())
        return items, total

    @staticmethod
    def get_by_slug(db: Session, slug: str, *, include_drafts: bool = False) -> Optional[Article]:
        stmt = (
            select(Article)
            .options(selectinload(Article.category), selectinload(Article.author))
            .where(Article.slug == slug)
        )
        if not include_drafts:
            stmt = stmt.where(Article.status == ArticleStatus.published)
        return db.scalar(stmt)

    @staticmethod
    def get_by_id(db: Session, article_id: int) -> Optional[Article]:
        return db.scalar(
            select(Article)
            .options(selectinload(Article.category), selectinload(Article.author))
            .where(Article.id == article_id)
        )

    @staticmethod
    def related(db: Session, article: Article, *, limit: int = 4) -> list[Article]:
        stmt = (
            select(Article)
            .options(selectinload(Article.category), selectinload(Article.author))
            .where(
                Article.status == ArticleStatus.published,
                Article.category_id == article.category_id,
                Article.id != article.id,
            )
            .order_by(Article.view_count.desc())
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def increment_views(db: Session, article: Article) -> Article:
        article.view_count = (article.view_count or 0) + 1
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def create(db: Session, payload: ArticleCreate, author_id: int) -> Article:
        if not db.get(Category, payload.category_id):
            raise ValueError("Category not found")

        slug = payload.slug or ArticleService._unique_slug(db, payload.title)
        if db.scalar(select(Article).where(Article.slug == slug)):
            slug = ArticleService._unique_slug(db, slug)

        reading_time = payload.estimated_reading_time or estimate_reading_time(payload.content)
        published_at = None
        if payload.status == ArticleStatus.published:
            published_at = datetime.now(timezone.utc)

        article = Article(
            title=payload.title.strip(),
            slug=slug,
            summary=payload.summary,
            content=payload.content,
            category_id=payload.category_id,
            author_id=author_id,
            status=payload.status,
            difficulty=payload.difficulty,
            estimated_reading_time=reading_time,
            thumbnail=payload.thumbnail,
            tags=payload.tags,
            published_at=published_at,
        )
        db.add(article)
        db.commit()
        return ArticleService.get_by_id(db, article.id)

    @staticmethod
    def update(db: Session, article: Article, payload: ArticleUpdate) -> Article:
        data = payload.model_dump(exclude_unset=True)
        if "category_id" in data and data["category_id"] is not None:
            if not db.get(Category, data["category_id"]):
                raise ValueError("Category not found")

        if "title" in data and data["title"]:
            data["title"] = data["title"].strip()
        if "slug" in data and data["slug"]:
            data["slug"] = ArticleService._unique_slug(db, data["slug"], exclude_id=article.id)
        elif "title" in data and "slug" not in data:
            data["slug"] = ArticleService._unique_slug(db, data["title"], exclude_id=article.id)

        if "content" in data and "estimated_reading_time" not in data:
            data["estimated_reading_time"] = estimate_reading_time(data["content"])

        new_status = data.get("status", article.status)
        if new_status == ArticleStatus.published and article.published_at is None:
            data["published_at"] = datetime.now(timezone.utc)
        if new_status == ArticleStatus.draft:
            # keep published_at history; do not clear
            pass

        for key, value in data.items():
            setattr(article, key, value)
        db.commit()
        return ArticleService.get_by_id(db, article.id)

    @staticmethod
    def delete(db: Session, article: Article) -> None:
        db.delete(article)
        db.commit()


def pages_for(total: int, page_size: int) -> int:
    return ceil(total / page_size) if page_size else 0
