from math import ceil
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.article import Article
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.utils.slug import slugify


class CategoryService:
    @staticmethod
    def _unique_slug(db: Session, base: str, *, exclude_id: Optional[int] = None) -> str:
        slug = slugify(base)
        candidate = slug
        counter = 2
        while True:
            stmt = select(Category).where(Category.slug == candidate)
            if exclude_id is not None:
                stmt = stmt.where(Category.id != exclude_id)
            existing = db.scalar(stmt)
            if not existing:
                return candidate
            candidate = f"{slug}-{counter}"
            counter += 1

    @staticmethod
    def list_categories(
        db: Session,
        *,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Category], int]:
        filters = []
        if search:
            term = f"%{search.strip()}%"
            filters.append(or_(Category.name.ilike(term), Category.description.ilike(term)))

        count_stmt = select(func.count()).select_from(Category)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = db.scalar(count_stmt) or 0

        stmt = select(Category).order_by(Category.name.asc())
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        items = list(db.scalars(stmt).all())
        return items, total

    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[Category]:
        return db.scalar(select(Category).where(Category.slug == slug))

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[Category]:
        return db.get(Category, category_id)

    @staticmethod
    def article_counts(db: Session, category_ids: list[int], *, published_only: bool = False) -> dict[int, int]:
        if not category_ids:
            return {}
        from app.models.article import ArticleStatus

        stmt = (
            select(Article.category_id, func.count())
            .where(Article.category_id.in_(category_ids))
            .group_by(Article.category_id)
        )
        if published_only:
            stmt = stmt.where(Article.status == ArticleStatus.published)
        rows = db.execute(stmt).all()
        return {cid: count for cid, count in rows}

    @staticmethod
    def create(db: Session, payload: CategoryCreate) -> Category:
        slug = payload.slug or CategoryService._unique_slug(db, payload.name)
        if db.scalar(select(Category).where(Category.slug == slug)):
            slug = CategoryService._unique_slug(db, slug)

        category = Category(
            name=payload.name.strip(),
            slug=slug,
            description=payload.description,
            icon=payload.icon,
            color=payload.color,
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def update(db: Session, category: Category, payload: CategoryUpdate) -> Category:
        data = payload.model_dump(exclude_unset=True)
        if "name" in data and data["name"]:
            data["name"] = data["name"].strip()
        if "slug" in data and data["slug"]:
            data["slug"] = CategoryService._unique_slug(db, data["slug"], exclude_id=category.id)
        elif "name" in data and "slug" not in data:
            data["slug"] = CategoryService._unique_slug(db, data["name"], exclude_id=category.id)

        for key, value in data.items():
            setattr(category, key, value)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete(db: Session, category: Category) -> None:
        published_count = db.scalar(
            select(func.count()).select_from(Article).where(Article.category_id == category.id)
        ) or 0
        if published_count:
            raise ValueError("Cannot delete category with existing ideas")
        db.delete(category)
        db.commit()


def pages_for(total: int, page_size: int) -> int:
    return ceil(total / page_size) if page_size else 0
