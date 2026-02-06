from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Generic, TypeVar, List, Dict, Any
from uuid import UUID

class NewsBase(BaseModel):
    title: str
    source: str
    url: str
    published_at: datetime
    category: str
    raw_summary: Optional[str] = None
    althara_summary: Optional[str] = None
    instagram_post: Optional[str] = None
    althara_content: Optional[Dict[str, Any]] = None
    tags: Optional[str] = None
    used_in_social: bool = False
    provincia: Optional[str] = None
    poblacion: Optional[str] = None
    domain: str = "real_estate"
    relevance_score: Optional[int] = None

class NewsCreate(NewsBase):
    """Schema for creating a news item. Excludes id, created_at, updated_at"""
    pass

class NewsRead(NewsBase):
    """Schema for reading a news item. Includes all fields"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Schema for paginated responses"""
    items: List[T]
    total: int
    limit: int
    offset: int
    has_more: bool

    class Config:
        from_attributes = True
