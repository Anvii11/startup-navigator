from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    icon: Optional[str] = Field(default=None, max_length=80)
    color: Optional[str] = Field(default=None, max_length=32)
    slug: Optional[str] = Field(default=None, max_length=150)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = None
    icon: Optional[str] = Field(default=None, max_length=80)
    color: Optional[str] = Field(default=None, max_length=32)
    slug: Optional[str] = Field(default=None, max_length=150)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime
    idea_count: int = 0
