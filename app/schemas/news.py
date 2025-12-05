from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional
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
    pass

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    category: Optional[str] = None
    raw_summary: Optional[str] = None
    althara_summary: Optional[str] = None
    tags: Optional[str] = None
    used_in_social: Optional[bool] = None

class NewsResponse(NewsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

