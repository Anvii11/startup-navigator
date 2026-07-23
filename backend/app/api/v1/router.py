from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, content, health, ai, user

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(content.public_router)
api_router.include_router(content.admin_router)
api_router.include_router(ai.router)
api_router.include_router(user.router)
