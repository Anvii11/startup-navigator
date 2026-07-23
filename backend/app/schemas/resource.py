from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.resource import ResourceType
from app.schemas.category import CategoryRead


class ResourceBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    url: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    type: ResourceType
    category_id: Optional[int] = None
    is_featured: bool = False
    thumbnail: Optional[str] = Field(default=None, max_length=500)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        value = value.strip()
        if not (value.startswith("http://") or value.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return value


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    url: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = None
    type: Optional[ResourceType] = None
    category_id: Optional[int] = None
    is_featured: Optional[bool] = None
    thumbnail: Optional[str] = Field(default=None, max_length=500)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not (value.startswith("http://") or value.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return value


class ResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    description: Optional[str] = None
    type: ResourceType
    category_id: Optional[int] = None
    is_featured: bool
    thumbnail: Optional[str] = None
    created_at: datetime
    category: Optional[CategoryRead] = None
