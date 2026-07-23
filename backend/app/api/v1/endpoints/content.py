from math import ceil
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import AdminUser, DbSession
from app.models.article import ArticleDifficulty, ArticleStatus
from app.schemas.article import ArticleCreate, ArticleDetail, ArticleListItem, ArticleUpdate
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.common import PaginatedResponse
from app.schemas.resource import ResourceCreate, ResourceRead, ResourceUpdate
from app.services.article import ArticleService
from app.services.category import CategoryService
from app.services.resource import ResourceService
from app.models.resource import ResourceType

public_router = APIRouter(tags=["content"])
admin_router = APIRouter(prefix="/admin", tags=["admin-content"])


def _category_read(db, category, *, published_only: bool = True) -> CategoryRead:
    counts = CategoryService.article_counts(db, [category.id], published_only=published_only)
    data = CategoryRead.model_validate(category)
    data.idea_count = counts.get(category.id, 0)
    return data


def _pages(total: int, page_size: int) -> int:
    return ceil(total / page_size) if page_size else 0


# ---------- Public: Categories ----------


@public_router.get("/categories", response_model=PaginatedResponse[CategoryRead])
def list_categories(
    db: DbSession,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    items, total = CategoryService.list_categories(db, search=search, page=page, page_size=page_size)
    counts = CategoryService.article_counts(db, [c.id for c in items], published_only=True)
    payload = []
    for c in items:
        row = CategoryRead.model_validate(c)
        row.idea_count = counts.get(c.id, 0)
        payload.append(row)
    return PaginatedResponse(
        items=payload,
        total=total,
        page=page,
        page_size=page_size,
        pages=_pages(total, page_size),
    )


@public_router.get("/categories/{slug}", response_model=CategoryRead)
def get_category(slug: str, db: DbSession):
    category = CategoryService.get_by_slug(db, slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return _category_read(db, category)


@public_router.get("/categories/{slug}/articles", response_model=PaginatedResponse[ArticleListItem])
def list_category_articles(
    slug: str,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    search: Optional[str] = None,
    difficulty: Optional[ArticleDifficulty] = None,
    sort: str = Query("newest", pattern="^(newest|oldest|trending|title)$"),
):
    category = CategoryService.get_by_slug(db, slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    items, total = ArticleService.list_articles(
        db,
        page=page,
        page_size=page_size,
        search=search,
        category_slug=slug,
        difficulty=difficulty,
        sort=sort,
        include_drafts=False,
    )
    return PaginatedResponse(
        items=[ArticleListItem.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=_pages(total, page_size),
    )


# ---------- Public: Startup Ideas ----------


@public_router.get("/articles", response_model=PaginatedResponse[ArticleListItem])
def list_articles(
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = Query(None, description="Category slug"),
    category_id: Optional[int] = None,
    difficulty: Optional[ArticleDifficulty] = None,
    tag: Optional[str] = None,
    sort: str = Query("newest", pattern="^(newest|oldest|trending|title)$"),
):
    items, total = ArticleService.list_articles(
        db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        category_slug=category,
        difficulty=difficulty,
        tag=tag,
        sort=sort,
        include_drafts=False,
    )
    return PaginatedResponse(
        items=[ArticleListItem.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=_pages(total, page_size),
    )


@public_router.get("/articles/{slug}", response_model=ArticleDetail)
def get_article(slug: str, db: DbSession):
    article = ArticleService.get_by_slug(db, slug, include_drafts=False)
    if not article:
        raise HTTPException(status_code=404, detail="Idea not found")
    ArticleService.increment_views(db, article)
    article = ArticleService.get_by_slug(db, slug, include_drafts=False)
    return ArticleDetail.model_validate(article)


@public_router.get("/articles/{slug}/related", response_model=list[ArticleListItem])
def related_articles(slug: str, db: DbSession, limit: int = Query(4, ge=1, le=12)):
    article = ArticleService.get_by_slug(db, slug, include_drafts=False)
    if not article:
        raise HTTPException(status_code=404, detail="Idea not found")
    items = ArticleService.related(db, article, limit=limit)
    return [ArticleListItem.model_validate(a) for a in items]


# ---------- Public: Resources ----------


@public_router.get("/resources", response_model=PaginatedResponse[ResourceRead])
def list_resources(
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    category_id: Optional[int] = None,
    type: Optional[ResourceType] = None,
    featured: Optional[bool] = None,
    sort: str = Query("newest", pattern="^(newest|oldest|title)$"),
):
    items, total = ResourceService.list_resources(
        db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        category_slug=category,
        resource_type=type,
        featured=featured,
        sort=sort,
    )
    return PaginatedResponse(
        items=[ResourceRead.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=_pages(total, page_size),
    )


# ---------- Admin: Categories ----------


@admin_router.get("/categories", response_model=PaginatedResponse[CategoryRead])
def admin_list_categories(
    db: DbSession,
    _: AdminUser,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    items, total = CategoryService.list_categories(db, search=search, page=page, page_size=page_size)
    counts = CategoryService.article_counts(db, [c.id for c in items], published_only=False)
    payload = []
    for c in items:
        row = CategoryRead.model_validate(c)
        row.idea_count = counts.get(c.id, 0)
        payload.append(row)
    return PaginatedResponse(
        items=payload, total=total, page=page, page_size=page_size, pages=_pages(total, page_size)
    )


@admin_router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def admin_create_category(payload: CategoryCreate, db: DbSession, _: AdminUser):
    category = CategoryService.create(db, payload)
    return _category_read(db, category, published_only=False)


@admin_router.put("/categories/{category_id}", response_model=CategoryRead)
def admin_update_category(category_id: int, payload: CategoryUpdate, db: DbSession, _: AdminUser):
    category = CategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category = CategoryService.update(db, category, payload)
    return _category_read(db, category, published_only=False)


@admin_router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_category(category_id: int, db: DbSession, _: AdminUser):
    category = CategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    try:
        CategoryService.delete(db, category)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ---------- Admin: Startup Ideas ----------


@admin_router.get("/articles", response_model=PaginatedResponse[ArticleListItem])
def admin_list_articles(
    db: DbSession,
    _: AdminUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    status_filter: Optional[ArticleStatus] = Query(None, alias="status"),
    difficulty: Optional[ArticleDifficulty] = None,
    sort: str = Query("newest", pattern="^(newest|oldest|trending|title)$"),
):
    items, total = ArticleService.list_articles(
        db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        difficulty=difficulty,
        status=status_filter,
        sort=sort,
        include_drafts=True,
    )
    return PaginatedResponse(
        items=[ArticleListItem.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=_pages(total, page_size),
    )


@admin_router.get("/articles/{article_id}", response_model=ArticleDetail)
def admin_get_article(article_id: int, db: DbSession, _: AdminUser):
    article = ArticleService.get_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Idea not found")
    return ArticleDetail.model_validate(article)


@admin_router.post("/articles", response_model=ArticleDetail, status_code=status.HTTP_201_CREATED)
def admin_create_article(payload: ArticleCreate, db: DbSession, admin: AdminUser):
    try:
        article = ArticleService.create(db, payload, author_id=admin.id)
        # Synchronize RAG vector store in background
        try:
            from app.rag.ingest import rebuild_vector_index
            rebuild_vector_index()
        except Exception as e:
            print("Vector reindex warning:", e)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ArticleDetail.model_validate(article)


@admin_router.put("/articles/{article_id}", response_model=ArticleDetail)
def admin_update_article(article_id: int, payload: ArticleUpdate, db: DbSession, _: AdminUser):
    article = ArticleService.get_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Idea not found")
    try:
        article = ArticleService.update(db, article, payload)
        try:
            from app.rag.ingest import rebuild_vector_index
            rebuild_vector_index()
        except Exception as e:
            print("Vector reindex warning:", e)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ArticleDetail.model_validate(article)


@admin_router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_article(article_id: int, db: DbSession, _: AdminUser):
    article = ArticleService.get_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Idea not found")
    ArticleService.delete(db, article)
    try:
        from app.rag.ingest import rebuild_vector_index
        rebuild_vector_index()
    except Exception as e:
        print("Vector reindex warning:", e)


# ---------- Admin: Resources ----------


@admin_router.get("/resources", response_model=PaginatedResponse[ResourceRead])
def admin_list_resources(
    db: DbSession,
    _: AdminUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    type: Optional[ResourceType] = None,
    featured: Optional[bool] = None,
    sort: str = Query("newest", pattern="^(newest|oldest|title)$"),
):
    items, total = ResourceService.list_resources(
        db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        resource_type=type,
        featured=featured,
        sort=sort,
    )
    return PaginatedResponse(
        items=[ResourceRead.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=_pages(total, page_size),
    )


@admin_router.post("/resources", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
def admin_create_resource(payload: ResourceCreate, db: DbSession, _: AdminUser):
    try:
        resource = ResourceService.create(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ResourceRead.model_validate(resource)


@admin_router.put("/resources/{resource_id}", response_model=ResourceRead)
def admin_update_resource(resource_id: int, payload: ResourceUpdate, db: DbSession, _: AdminUser):
    resource = ResourceService.get_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    try:
        resource = ResourceService.update(db, resource, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ResourceRead.model_validate(resource)


@admin_router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_resource(resource_id: int, db: DbSession, _: AdminUser):
    resource = ResourceService.get_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    ResourceService.delete(db, resource)
