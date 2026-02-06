# Refactor Notes

This document summarizes the cleanup and refactor performed on althara-news-service.

## Key Changes

### 1. Utilities Extraction

- **`app/utils/html_utils.py`**: `strip_html_tags(text)` – strips HTML tags, decodes entities, normalizes whitespace
- **`app/utils/rss_utils.py`**: `parse_published_date(entry)` – extracts `datetime` from feedparser entry (`published_parsed` or `updated_parsed`)
- **`app/utils/guardrails.py`**: `passes_guardrails(title, deny_keywords, allow_keywords, strict_require_allow, summary?, url?)` – keyword-based filtering for relevance

### 2. Deduplication in Ingestion / Adapters

- **`rss_ingestor.py`**, **`tech_rss_ingestor.py`**: removed local `_clean_html`, `_parse_published_date`, `_passes_guardrails`; use shared utils
- **`idealista_ingestor.py`**: uses `passes_guardrails` from utils instead of `_is_relevant_to_real_estate`
- **`news_adapter.py`**: `_clean_html` delegates base stripping to `strip_html_tags`, keeps metadata/accent logic
- **`routers/news.py`**: uses `passes_guardrails` from utils

### 3. Text Truncation

- **`app/utils/text_compaction.py`**: already provides `truncate_at_sentence` and `truncate_at_word_boundary`. No new truncation logic added; existing truncation uses sentence/word boundaries where applicable.

### 4. English Standardization (code/docs only)

- **Templates**: UI kept in Spanish (selector, portal, news_detail, draft_editor, base)
- **Router error messages**: `routers/news.py` – error strings translated to English
- **README**: translated to English (see README.md)

### 5. Tests

- **`tests/test_utils.py`**: tests for `strip_html_tags`, `parse_published_date`, `passes_guardrails`
- **`tests/test_text_compaction.py`**: existing tests for truncation at sentence/word boundaries

## Renamed / New Modules

| Before | After |
|--------|-------|
| (inline helpers in ingestors) | `app/utils/html_utils.py`, `app/utils/rss_utils.py`, `app/utils/guardrails.py` |

No public module or class names were renamed. Internal function names in ingestors/adapters remain snake_case.

## How to Run

### Project

```bash
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create .env with DATABASE_URL
alembic upgrade head
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- News Studio UI: http://localhost:8000/ui

### Tests

```bash
python3 -m pytest tests/ -v --tb=short
```

- 29 tests pass
- API tests use `httpx.AsyncClient` + session-scoped event loop (`asyncio_default_test_loop_scope=session`) to avoid "Future attached to different loop" with async SQLAlchemy

## Assumptions

1. **Endpoint paths unchanged** – all URLs (e.g. `/api/news`, `/api/admin/ingest`) remain the same
2. **Migrations preserved** – no migrations modified; only additive changes allowed
3. **API compatibility** – request/response shapes and behavior kept
4. **Brand / category constants** – Althara, Oxono, category names like `PRECIOS_VIVIENDA` kept as-is
5. **Caption labels** – adapter output strings like "Fuente:" in captions kept for now; user-facing content in templates is in English
6. **No new app/core or app/services** – structure left as-is to avoid unnecessary churn; utilities consolidated in `app/utils/`
7. **Network-free tests** – tests use mocks/fixtures; no live RSS or API calls
8. **UI in Spanish** – templates (selector, portal, news_detail, draft_editor) use Spanish for all user-facing text
