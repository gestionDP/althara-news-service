from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class IGDraft(Base):
    __tablename__ = "ig_drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    news_id = Column(UUID(as_uuid=True), ForeignKey("news.id", ondelete="CASCADE"), nullable=False, index=True)
    hook = Column(Text, nullable=True)
    carousel_slides = Column(JSONB, nullable=False)  # array of {title, body}
    caption = Column(Text, nullable=True)
    hashtags = Column(JSONB, nullable=True)  # array of strings
    cta = Column(Text, nullable=True)
    source_line = Column(Text, nullable=False)
    disclaimer = Column(Text, nullable=True)
    tone = Column(Text, nullable=False, default="neutral")
    language = Column(Text, nullable=False, default="es")
    status = Column(Text, nullable=False, default="DRAFT")  # DRAFT|NEEDS_REVIEW|APPROVED|PUBLISHED
    editor_notes = Column(Text, nullable=True)
    variant_of_id = Column(UUID(as_uuid=True), ForeignKey("ig_drafts.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    news = relationship("News", back_populates="ig_drafts")
    variant_of = relationship("IGDraft", remote_side="IGDraft.id")
