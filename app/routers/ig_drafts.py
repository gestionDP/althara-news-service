"""
IG Drafts API: generate, variants, CRUD, approve, publish.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.config import settings
from app.models.news import News
from app.models.ig_draft import IGDraft
from app.schemas.ig_draft import IGDraftRead, IGDraftUpdate, IGDraftCreate
from app.adapters.ig_adapter import generate_ig_draft, generate_variants

router = APIRouter(prefix="/api/ig", tags=["ig-drafts"])


def _require_token(x_ingest_token: Optional[str] = Header(None, alias="X-INGEST-TOKEN")):
    """Optional token check for mutations. If INGEST_TOKEN is set, require it."""
    if settings.INGEST_TOKEN:
        if not x_ingest_token or x_ingest_token != settings.INGEST_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid or missing X-INGEST-TOKEN")
    return True


@router.post("/news/{news_id}/generate", response_model=IGDraftRead)
async def generate_draft(
    news_id: UUID,
    tone: Optional[str] = Query(None, description="Tone for draft"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(_require_token),
):
    """Create or update IG draft for a news item."""
    stmt = select(News).where(News.id == news_id)
    res = await db.execute(stmt)
    news = res.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    brand = "oxono" if news.domain == "tech" else "althara"
    t = tone or settings.IG_DEFAULT_TONE

    # Check for existing main draft (variant_of_id is null)
    stmt = select(IGDraft).where(
        and_(IGDraft.news_id == news_id, IGDraft.variant_of_id.is_(None))
    )
    res = await db.execute(stmt)
    existing = res.scalar_one_or_none()

    draft_data = generate_ig_draft(news, tone=t, brand=brand)

    if existing:
        for k, v in draft_data.items():
            setattr(existing, k, v)
        await db.commit()
        await db.refresh(existing)
        return existing

    draft = IGDraft(news_id=news_id, **draft_data)
    db.add(draft)
    await db.commit()
    await db.refresh(draft)
    return draft


@router.post("/news/{news_id}/variants")
async def create_variants(
    news_id: UUID,
    count: int = Query(3, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(_require_token),
):
    """Generate N variant drafts for a news item."""
    stmt = select(News).where(News.id == news_id)
    res = await db.execute(stmt)
    news = res.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    brand = "oxono" if news.domain == "tech" else "althara"
    variants_data = generate_variants(news, n=count, brand=brand)

    created = []
    for v in variants_data:
        draft = IGDraft(news_id=news_id, **v)
        db.add(draft)
        created.append(draft)

    await db.commit()
    for d in created:
        await db.refresh(d)

    return {
        "created": len(created),
        "drafts": [IGDraftRead.model_validate(d) for d in created],
    }


@router.get("/", response_model=list[IGDraftRead])
async def list_drafts(
    domain: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List IG drafts with filters."""
    query = select(IGDraft).join(News)
    if domain:
        query = query.where(News.domain == domain)
    if status:
        query = query.where(IGDraft.status == status)
    query = query.order_by(IGDraft.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    res = await db.execute(query)
    drafts = res.scalars().unique().all()
    return drafts


@router.get("/{draft_id}", response_model=IGDraftRead)
async def get_draft(draft_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get draft by ID."""
    stmt = select(IGDraft).where(IGDraft.id == draft_id)
    res = await db.execute(stmt)
    draft = res.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


@router.patch("/{draft_id}", response_model=IGDraftRead)
async def update_draft(
    draft_id: UUID,
    payload: IGDraftUpdate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(_require_token),
):
    """Update draft fields."""
    stmt = select(IGDraft).where(IGDraft.id == draft_id)
    res = await db.execute(stmt)
    draft = res.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(draft, k, v)
    await db.commit()
    await db.refresh(draft)
    return draft


@router.post("/{draft_id}/approve", response_model=IGDraftRead)
async def approve_draft(
    draft_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(_require_token),
):
    """Set draft status to APPROVED."""
    stmt = select(IGDraft).where(IGDraft.id == draft_id)
    res = await db.execute(stmt)
    draft = res.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    draft.status = "APPROVED"
    await db.commit()
    await db.refresh(draft)
    return draft


@router.post("/{draft_id}/publish", response_model=IGDraftRead)
async def publish_draft(
    draft_id: UUID,
    mark_news_used: bool = Query(True, description="Set news.used_in_social=true"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(_require_token),
):
    """Set draft status to PUBLISHED and optionally mark news as used."""
    stmt = select(IGDraft).where(IGDraft.id == draft_id)
    res = await db.execute(stmt)
    draft = res.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    draft.status = "PUBLISHED"
    if mark_news_used:
        stmt = select(News).where(News.id == draft.news_id)
        nres = await db.execute(stmt)
        news = nres.scalar_one_or_none()
        if news:
            news.used_in_social = True

    await db.commit()
    await db.refresh(draft)
    return draft
