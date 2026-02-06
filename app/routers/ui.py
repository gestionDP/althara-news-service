"""
News Studio UI: Jinja2 templates, brand selector, inbox, drafts, IG editor.
"""
from pathlib import Path

from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, exists
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.config import settings
from app.models.news import News
from app.models.ig_draft import IGDraft
from app.brands import BRANDS, get_domain_for_brand, get_display_name
from app.constants import VALID_CATEGORIES
from app.constants_tech import TECH_CATEGORY_LABELS, TechNewsCategory
from app.auth import basic_auth_dependency

router = APIRouter(tags=["ui"])
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def _ensure_templates():
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)


@router.get("/ui", response_class=HTMLResponse)
async def ui_selector(request: Request, _=Depends(basic_auth_dependency)):
    """Brand selector: Althara / Oxono. Remember in cookie."""
    return templates.TemplateResponse(
        "selector.html", {"request": request, "brands": BRANDS}
    )


@router.get("/ui/{brand}", response_class=HTMLResponse)
async def ui_portal(
    request: Request,
    brand: str,
    tab: str = Query("inbox", description="inbox | drafts | approved"),
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    only_without_draft: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(basic_auth_dependency),
):
    """Portal for brand: Inbox | Drafts | Aprobados."""
    if brand not in BRANDS:
        return RedirectResponse("/ui", status_code=302)

    domain = get_domain_for_brand(brand)

    if tab == "drafts":
        query = select(News).join(IGDraft, News.id == IGDraft.news_id).where(News.domain == domain).where(IGDraft.status == "DRAFT")
    elif tab == "approved":
        query = select(News).join(IGDraft, News.id == IGDraft.news_id).where(News.domain == domain).where(IGDraft.status.in_(["APPROVED", "PUBLISHED"]))
    else:
        query = select(News).where(News.domain == domain)

    if q:
        query = query.where(News.title.ilike(f"%{q}%"))
    if category:
        query = query.where(News.category == category)
    if only_without_draft:
        has_draft = exists().where(IGDraft.news_id == News.id)
        query = query.where(~has_draft)

    query = query.order_by(News.published_at.desc()).limit(100)
    res = await db.execute(query)
    news_list = res.scalars().unique().all() if tab in ("drafts", "approved") else res.scalars().all()

    # For each news, get draft count and first draft id
    news_with_drafts = []
    for n in news_list:
        stmt = select(IGDraft).where(IGDraft.news_id == n.id).order_by(IGDraft.created_at.desc()).limit(1)
        first_draft = (await db.execute(stmt)).scalar_one_or_none()
        stmt = select(func.count()).select_from(IGDraft).where(IGDraft.news_id == n.id)
        dc = (await db.execute(stmt)).scalar_one()
        news_with_drafts.append({
            "news": n,
            "draft_count": dc,
            "first_draft_id": str(first_draft.id) if first_draft else None,
        })

    if domain == "tech":
        categories = [{"value": k, "label": v} for k, v in TECH_CATEGORY_LABELS.items()]
    else:
        from app.constants import CATEGORY_LABELS
        categories = [{"value": c, "label": CATEGORY_LABELS.get(c, c)} for c in VALID_CATEGORIES[:14]]
    return templates.TemplateResponse(
        "portal.html",
        {
            "request": request,
            "brand": brand,
            "brand_display": get_display_name(brand),
            "brands": BRANDS,
            "tab": tab,
            "news_with_drafts": news_with_drafts,
            "domain": domain,
            "categories": categories,
            "q": request.query_params.get("q", ""),
            "category_filter": request.query_params.get("category", ""),
            "only_without_draft": request.query_params.get("only_without_draft") == "true" or request.query_params.get("only_without_draft") == "1",
        },
    )


@router.get("/ui/{brand}/news/{news_id}", response_class=HTMLResponse)
async def ui_news_detail(
    request: Request,
    brand: str,
    news_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(basic_auth_dependency),
):
    """News detail with action buttons."""
    if brand not in BRANDS:
        return RedirectResponse("/ui", status_code=302)

    stmt = select(News).where(News.id == news_id)
    res = await db.execute(stmt)
    news = res.scalar_one_or_none()
    if not news:
        return RedirectResponse(f"/ui/{brand}", status_code=302)

    stmt = select(IGDraft).where(IGDraft.news_id == news_id).order_by(IGDraft.created_at.desc())
    res = await db.execute(stmt)
    drafts = res.scalars().all()

    return templates.TemplateResponse(
        "news_detail.html",
        {"request": request, "brand": brand, "brand_display": get_display_name(brand), "brands": BRANDS, "news": news, "drafts": drafts},
    )


@router.get("/ui/{brand}/draft/{draft_id}", response_class=HTMLResponse)
async def ui_draft_editor(
    request: Request,
    brand: str,
    draft_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(basic_auth_dependency),
):
    """IG draft editor: preview, edit, copy, approve, publish."""
    if brand not in BRANDS:
        return RedirectResponse("/ui", status_code=302)

    stmt = select(IGDraft).where(IGDraft.id == draft_id)
    res = await db.execute(stmt)
    draft = res.scalar_one_or_none()
    if not draft:
        return RedirectResponse(f"/ui/{brand}", status_code=302)

    stmt = select(News).where(News.id == draft.news_id)
    res = await db.execute(stmt)
    news = res.scalar_one_or_none()

    return templates.TemplateResponse(
        "draft_editor.html",
        {
            "request": request,
            "brand": brand,
            "brand_display": get_display_name(brand),
            "brands": BRANDS,
            "draft": draft,
            "news": news,
        },
    )
