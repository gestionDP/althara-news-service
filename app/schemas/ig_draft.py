from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class CarouselSlide(BaseModel):
    title: str
    body: str


class IGDraftBase(BaseModel):
    hook: Optional[str] = None
    carousel_slides: List[dict]  # [{title, body}, ...]
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    cta: Optional[str] = None
    source_line: str
    disclaimer: Optional[str] = None
    tone: str = "neutral"
    language: str = "es"
    status: str = "DRAFT"
    editor_notes: Optional[str] = None


class IGDraftCreate(IGDraftBase):
    news_id: UUID


class IGDraftUpdate(BaseModel):
    hook: Optional[str] = None
    carousel_slides: Optional[List[dict]] = None
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    cta: Optional[str] = None
    source_line: Optional[str] = None
    disclaimer: Optional[str] = None
    tone: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = None
    editor_notes: Optional[str] = None


class IGDraftRead(IGDraftBase):
    id: UUID
    news_id: UUID
    variant_of_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
