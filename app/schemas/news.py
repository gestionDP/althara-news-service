from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Generic, TypeVar, List
from uuid import UUID

class NewsBase(BaseModel):
    title: str
    source: str
    url: str
    published_at: datetime
    category: str
    raw_summary: Optional[str] = None
    althara_summary: Optional[str] = None
    tags: Optional[str] = None
    used_in_social: bool = False

class NewsCreate(NewsBase):
    """Schema para crear una noticia. No incluye id, created_at, updated_at"""
    pass

class NewsRead(NewsBase):
    """Schema para leer una noticia. Incluye todos los campos"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema para respuesta paginada
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Schema para respuestas paginadas"""
    items: List[T]
    total: int
    limit: int
    offset: int
    has_more: bool

    class Config:
        from_attributes = True
