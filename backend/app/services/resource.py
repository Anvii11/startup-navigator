from math import ceil
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.category import Category
from app.models.resource import Resource, ResourceType
from app.schemas.resource import ResourceCreate, ResourceUpdate


class ResourceService:
    @staticmethod
    def list_resources(
        db: Session,
        *,
        page: int = 1,
        page_size: int = 12,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        category_slug: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        featured: Optional[bool] = None,
        sort: str = "newest",
    ) -> tuple[list[Resource], int]:
        filters = []
        if category_id is not None:
            filters.append(Resource.category_id == category_id)
        if category_slug:
            cat = db.scalar(select(Category).where(Category.slug == category_slug))
            if cat is None:
                return [], 0
            filters.append(Resource.category_id == cat.id)
        if resource_type is not None:
            filters.append(Resource.type == resource_type)
        if featured is not None:
            filters.append(Resource.is_featured.is_(featured))
        if search:
            term = f"%{search.strip()}%"
            filters.append(
                or_(
                    Resource.title.ilike(term),
                    Resource.description.ilike(term),
                    Resource.url.ilike(term),
                )
            )

        count_stmt = select(func.count()).select_from(Resource)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = db.scalar(count_stmt) or 0

        stmt = select(Resource).options(selectinload(Resource.category))
        if filters:
            stmt = stmt.where(*filters)

        if sort == "title":
            stmt = stmt.order_by(Resource.title.asc())
        elif sort == "oldest":
            stmt = stmt.order_by(Resource.created_at.asc())
        else:
            stmt = stmt.order_by(Resource.is_featured.desc(), Resource.created_at.desc())

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        return list(db.scalars(stmt).all()), total

    @staticmethod
    def get_by_id(db: Session, resource_id: int) -> Optional[Resource]:
        return db.scalar(
            select(Resource)
            .options(selectinload(Resource.category))
            .where(Resource.id == resource_id)
        )

    @staticmethod
    def create(db: Session, payload: ResourceCreate) -> Resource:
        if payload.category_id is not None and not db.get(Category, payload.category_id):
            raise ValueError("Category not found")

        resource = Resource(
            title=payload.title.strip(),
            url=payload.url.strip(),
            description=payload.description,
            type=payload.type,
            category_id=payload.category_id,
            is_featured=payload.is_featured,
            thumbnail=payload.thumbnail,
        )
        db.add(resource)
        db.commit()
        return ResourceService.get_by_id(db, resource.id)

    @staticmethod
    def update(db: Session, resource: Resource, payload: ResourceUpdate) -> Resource:
        data = payload.model_dump(exclude_unset=True)
        if "category_id" in data and data["category_id"] is not None:
            if not db.get(Category, data["category_id"]):
                raise ValueError("Category not found")
        if "title" in data and data["title"]:
            data["title"] = data["title"].strip()
        if "url" in data and data["url"]:
            data["url"] = data["url"].strip()

        for key, value in data.items():
            setattr(resource, key, value)
        db.commit()
        return ResourceService.get_by_id(db, resource.id)

    @staticmethod
    def delete(db: Session, resource: Resource) -> None:
        db.delete(resource)
        db.commit()


def pages_for(total: int, page_size: int) -> int:
    return ceil(total / page_size) if page_size else 0
