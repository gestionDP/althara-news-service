from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
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
    tags = Column(Text, nullable=True)
    used_in_social = Column(Boolean, default=False, nullable=False)
    provincia = Column(String, nullable=True)
    poblacion = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

