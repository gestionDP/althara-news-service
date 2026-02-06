from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class News(Base):
    __tablename__ = "news"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    url = Column(String, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=False)
    category = Column(String, nullable=False)
    raw_summary = Column(Text, nullable=True)
    althara_summary = Column(Text, nullable=True)
    instagram_post = Column(Text, nullable=True)
    althara_content = Column(JSON, nullable=True)
    tags = Column(Text, nullable=True)
    used_in_social = Column(Boolean, default=False, nullable=False)
    provincia = Column(String, nullable=True)
    poblacion = Column(String, nullable=True)
    domain = Column(Text, nullable=False, default="real_estate")
    relevance_score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    ig_drafts = relationship("IGDraft", back_populates="news", cascade="all, delete-orphan")

