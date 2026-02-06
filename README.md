# althara-news-service

News microservice for Althara (real estate) and Oxono (tech/AI), with internal News Studio. Built with FastAPI, async SQLAlchemy and Alembic, connected to Neon PostgreSQL.

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Project Summary](#-project-summary)
- [What's Completed](#-whats-completed)
- [Requirements](#️-requirements)
- [Installation and Configuration](#-installation-and-configuration)
- [Current Status](#-current-status)
- [API Documentation](#-api-documentation)
- [Endpoints](#-endpoints)
- [News Ingestion](#-news-ingestion)
- [Althara Adapter](#-althara-adapter)
- [News Categories](#-news-categories)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Automation](#-automation)
- [Technologies](#️-technologies)
- [Resolved Issues](#-resolved-issues)
- [Next Steps](#-next-steps)
- [Troubleshooting](#-troubleshooting)
- [News Studio (UI)](#-news-studio-ui)
- ["Generate more" Endpoints](#-generate-more-endpoints)

---

## 📝 Project Summary

This microservice provides a REST API to manage real estate news. It allows creating, listing and querying news with predefined categories, connecting to a PostgreSQL database on Neon via async SQLAlchemy.

---

## ✅ What's Completed

### BLOCK 1: Alembic Configuration (Async Migrations) ✅

- ✅ `alembic.ini` configured without hardcoded URL (uses env variable)
- ✅ `alembic/env.py` configured for async mode with `async_engine_from_config`
- ✅ Initial migration: `001_initial_migration_create_news_table.py`
- ✅ Automatic database URL normalization

### BLOCK 2: SQLAlchemy `News` Model ✅

- ✅ Full `News` model with fields:
  - `id` (UUID, PK)
  - `title`, `source`, `url`, `published_at`, `category`
  - `raw_summary`, `althara_summary`, `tags`
  - `used_in_social` (Boolean)
  - `created_at`, `updated_at` (automatic timestamps)

### BLOCK 3: Pydantic Schemas ✅

- ✅ `NewsBase` – Base fields
- ✅ `NewsCreate` – For creating news (no id, timestamps)
- ✅ `NewsRead` – For reading news (includes all fields)

### BLOCK 4: Router ✅

- ✅ `GET /api/health` – Health check
- ✅ `POST /api/news` – Create news
- ✅ `GET /api/news` – List news (with filters)
- ✅ `GET /api/news/{id}` – Get news by ID

### BLOCK 5: Neon Connection and Tests ✅

- ✅ Neon PostgreSQL connection configured
- ✅ Migrations run correctly
- ✅ `news` table created in Neon
- ✅ FastAPI server running
- ✅ Endpoints tested and working

### EXTRAS: Defined Categories ✅

- ✅ 21 real estate categories in `app/constants.py`
- ✅ Constants available for use in code

### BLOCK 6: Ingestion System ✅

- ✅ Pydantic Settings (`app/config.py`)
- ✅ 8 real RSS sources (`app/ingestion/rss_ingestor.py`)
- ✅ Admin router (`app/routers/admin.py`)
- ✅ Endpoints to trigger ingestion (`/api/admin/ingest`)

### BLOCK 7: Althara Adapter ✅

- ✅ Adapter to transform news to Althara tone (`app/adapters/news_adapter.py`)
- ✅ `build_althara_summary()` with analytical tone by category
- ✅ Endpoint to adapt pending news (`POST /api/admin/adapt-pending`)
- ✅ Full pipeline: Ingest → Adapt → Query

### BLOCK 8: Automation and Volume Control ✅

- ✅ Limit: 5 news per source (max ~40 per run)
- ✅ All-in-one endpoint: `POST /api/admin/ingest-and-adapt`
- ✅ Automatic deduplication by URL
- ✅ Ready for external automation (cron, cloud services)

---

## ⚡ Quick Start

```bash
# 1. Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env with your DATABASE_URL (Neon, use -pooler endpoint)
# DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx-pooler.us-east-1.aws.neon.tech/neondb
# Optional: SQL_ECHO=true to see queries in logs (prod: false)

# 4. Run migrations
alembic upgrade head

# 5. Start the server
uvicorn app.main:app --reload
```

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **News Studio UI**: http://localhost:8000/ui

---

## 🛠️ Requirements

- Python 3.11+
- PostgreSQL (Neon)
- Neon account with project created

---

## 🚀 Installation and Configuration

### 1. Create virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install requirements

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

**Create a `.env` file in the project root** with your Neon URL:

```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:YOUR_PASSWORD@ep-xxx-xxx-pooler.us-east-1.aws.neon.tech/neondb
```

**Important:**

- ⚠️ **Must start with `postgresql+asyncpg://`** (not plain `postgresql://`) for async connections
- Get `DATABASE_URL` from the Neon dashboard
- `.env` is in `.gitignore`, so credentials stay private
- ⚡ **Automatic normalization**: The code converts:
  - `postgresql://` → `postgresql+asyncpg://`
  - Removes incompatible params (`sslmode`, `channel_binding`)
  - asyncpg handles SSL automatically

**Full format example:**

```
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

**Note:** If you copy the URL from Neon and it has `postgresql://` or SSL params, the code will normalize it automatically.

### 4. Run migrations

With the virtual environment active:

```bash
alembic upgrade head
```

This creates the `news` table in your Neon database.

**Expected output:**

```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial, Initial migration: create news table
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

Server will be available at `http://localhost:8000`

**Expected output:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

---

## ✅ Current Status

### Working:

- ✅ **Neon database** – Connected and working
- ✅ **Alembic migrations** – `news` table created
- ✅ **FastAPI server** – Running at `http://localhost:8000`
- ✅ **Async connection** – SQLAlchemy async working correctly
- ✅ **Health Check** – `GET /api/health` returns `{"status": "ok"}`
- ✅ **CRUD endpoints** – All basic endpoints working
- ✅ **URL normalization** – Automatic SSL param handling

### Full system:

- ✅ **RSS news ingestor** – 8 real sources configured
- ✅ **Althara adapter** – Automatic transformation to Althara tone
- ✅ **Volume control** – 5 news per source limit
- ✅ **Automation** – All-in-one endpoint ready for external services

---

## 📖 API Documentation

- **Swagger UI**: `http://localhost:8000/docs` – Interactive interface to test endpoints
- **ReDoc**: `http://localhost:8000/redoc` – Alternative docs

---

## 🔌 Endpoints

### Health Check

- `GET /api/health` – Service health check
  - Response: `{"status": "ok"}`

### News

- `POST /api/news` – Create a new news item

  - Body: `NewsCreate` (JSON)
  - Response: `NewsRead` (with id, timestamps)

- `GET /api/news` – List news

  - Optional query params:
    - `category` (str) – Filter by category
    - `q` (str) – Search in title
    - `from_date` (datetime) – Date from
    - `to_date` (datetime) – Date to
  - Response: Array of `NewsRead`

- `GET /api/news/{id}` – Get news by ID
  - Path param: `id` (UUID)
  - Response: `NewsRead` or 404

### Admin – Ingestion and Adaptation

- `POST /api/admin/ingest` – Ingest news from all RSS sources

  - Limit: 5 news per source (max ~40 per run)
  - Response: `{"Expansion Inmobiliario": <int>, ...}`

- `POST /api/admin/ingest/rss` – Alias of main endpoint (same result)

- `POST /api/admin/adapt-pending` – Adapt pending news to Althara tone

  - Finds news with `althara_summary = NULL` and adapts them
  - Response: `{"adapted": <int>, "message": "..."}`

- `POST /api/admin/ingest-and-adapt` – Full pipeline (all-in-one)

  - Runs ingest (5 per source) + adaptation in one call
  - Ideal for external automation (cron, cloud services)
  - Response: `{"ingested": <int>, "ingested_by_source": {...}, "adapted": <int>, "message": "..."}`

---

## 📥 News Ingestion

The microservice includes an ingestion system to fetch news automatically from external sources.

### Available Sources

⚠️ **IMPORTANT: Idealista has NO news API**

Idealista does not provide a public news API. Its API only includes property search and market data.

**Idealista newsletter note:** Although Idealista has a weekly email newsletter, automating it is not feasible because:

- It is only available by email (no RSS/API)
- Would require complex HTML email parsing
- Our RSS sources are better: automatic, legal and stable

**Configured RSS sources (8):**

1. **RSS – Expansion Inmobiliario** – Market, mortgages, investment news
2. **RSS – Cinco Días** – Real estate economy
3. **RSS – El Economista** – Housing and market
4. **RSS – BOE Subastas** – Real estate auctions
5. **RSS – BOE General** – Regulations and laws
6. **RSS – Observatorio Inmobiliario** – Sector analysis
7. **RSS – Interempresas Construcción** – Construction news
8. **RSS – ArchDaily** – Architecture and construction

### Admin Endpoints

#### Ingest News from RSS

```bash
POST /api/admin/ingest
# Or:
POST /api/admin/ingest/rss
```

**Response:**

```json
{
  "Expansion Inmobiliario": 10,
  "Cinco Días - Economía Inmobiliaria": 5,
  ...
}
```

**Description:** Ingests news from all configured RSS sources. The system avoids duplicates by comparing URLs.

**Configured limit:** Max 5 news per source per run (total max ~40). This controls volume and keeps only the most recent.

**Note:** Idealista has no news API, so we only use legal RSS sources.

### Usage Example

**Using curl:**

```bash
# Ingest news from all RSS sources
curl -X POST "http://localhost:8000/api/admin/ingest"

# Or using the alias
curl -X POST "http://localhost:8000/api/admin/ingest/rss"
```

**Using Swagger UI:**

1. Go to `http://localhost:8000/docs`
2. Find the `admin` section
3. Expand `POST /api/admin/ingest`
4. Click "Try it out" then "Execute"

### RSS Source Configuration

Sources are configured in `app/ingestion/rss_ingestor.py` in the `RSS_SOURCES` variable.

**Current RSS sources:**

- Expansion Inmobiliario, Cinco Días, El Economista, BOE Subastas, BOE General, Observatorio Inmobiliario, Interempresas Construcción, ArchDaily

See `FUENTES_RSS.md` for details on each source.

### Volume Control

- **Configured limit:** 5 news per source per run
- **Max per run:** ~40 news (8 sources × 5)
- **Automatic deduplication:** Duplicate URLs are skipped
- **Quality control:** Only the most recent news are processed

### Important Notes

- **Idealista has no news API** – Its API is for property search only, not news.
- **Idealista newsletter:** Exists but is not automatable (email only, no RSS/API). RSS sources are better.
- **Real RSS sources:** All news come from 8 legal, working RSS feeds.
- **Deduplication:** URLs are compared to avoid duplicates.
- **Configuration:** All RSS sources are ready; no extra setup needed.

---

## 🎨 Althara Adapter

The system includes an adapter to transform news to Althara tone, suitable for social media.

### Adaptation Endpoint

- `POST /api/admin/adapt-pending` – Adapts pending news to Althara tone

  - Finds all news with `althara_summary = NULL`
  - Transforms them using the Althara adapter
  - Saves result in `althara_summary`
  - Response: `{"adapted": <int>, "message": "..."}`

### How It Works

The adapter produces a structured summary:

1. **First line:** Neutral summary of the fact (title + trimmed summary)
2. **Next lines:** Analytical interpretation by category
3. **Source:** Added in the frontend

### Analytical Tone by Category

The adapter uses different analytical tones per category:

- **PRECIOS_VIVIENDA:** Market trend analysis
- **FONDOS_INVERSION:** Investment strategy evolution
- **GRANDES_INVERSIONES:** Sector dynamics
- **NOTICIAS_HIPOTECAS:** Market health indicators
- **NOTICIAS_BOE_SUBASTAS:** Opportunities requiring technical analysis
- **NORMATIVAS:** Impact on real estate ecosystem
- **CONSTRUCCION:** Demand trends and sector evolution

### Full Pipeline

**Option 1: Separate steps**

```
1. POST /api/admin/ingest          → Ingest news (raw_summary)
2. POST /api/admin/adapt-pending   → Adapt to Althara (althara_summary)
3. GET /api/news                   → News ready for social media
```

**Option 2: All-in-one (recommended for automation)**

```
1. POST /api/admin/ingest-and-adapt → Ingest + Adapt in one call
2. GET /api/news                    → News ready for social media
```

The `/ingest-and-adapt` endpoint is ideal for external automation (cron, cloud services) because it runs the full pipeline in one call.

---

## 📂 News Categories

The system uses 21 categories for real estate news. Constants are in `app/constants.py`.

### Funds and Investment

- `FONDOS_INVERSION_INMOBILIARIA`
- `GRANDES_INVERSIONES_INMOBILIARIAS`
- `MOVIMIENTOS_GRANDES_TENEDORES`
- `TOKENIZATION_ACTIVOS`

### General News

- `NOTICIAS_INMOBILIARIAS`, `NOTICIAS_HIPOTECAS`, `NOTICIAS_LEYES_OKUPAS`, `NOTICIAS_BOE_SUBASTAS`, `NOTICIAS_DESAHUCIOS`, `NOTICIAS_CONSTRUCCION`

### Prices and Market

- `PRECIOS_VIVIENDA`, `PRECIOS_MATERIALES`, `PRECIOS_SUELO`

### Analysis and Trends

- `FUTURO_SECTOR_INMOBILIARIO`, `BURBUJA_INMOBILIARIA`

### Rentals and Regulations

- `ALQUILER_VACACIONAL`, `NORMATIVAS_VIVIENDAS`, `FALTA_VIVIENDA`

### Construction and Urbanization

- `NOTICIAS_URBANIZACION`, `NOVEDADES_CONSTRUCCION`, `CONSTRUCCION_MODULAR`

---

## 🧪 Testing

### Run tests

```bash
python3 -m pytest tests/ -v --tb=short
```

### 1. Health Check

```bash
curl http://localhost:8000/api/health
```

Expected: `{"status": "ok"}`

### 2. Create news (POST /news)

**Option A: Swagger UI (recommended)**

1. Go to `http://localhost:8000/docs`
2. Expand `POST /api/news`
3. Click "Try it out"
4. Use this JSON:

```json
{
  "title": "Test Neon connection",
  "source": "Test Local",
  "url": "https://example.com/test",
  "published_at": "2025-12-05T10:30:00Z",
  "category": "PRECIOS_VIVIENDA",
  "raw_summary": "Raw summary for test",
  "althara_summary": "Althara reading for test",
  "tags": "test,neon",
  "used_in_social": false
}
```

5. Click "Execute"

**Option B: curl**

```bash
curl -X POST "http://localhost:8000/api/news" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Neon connection",
    "source": "Test Local",
    "url": "https://example.com/test",
    "published_at": "2025-12-05T10:30:00Z",
    "category": "PRECIOS_VIVIENDA",
    "raw_summary": "Raw summary for test",
    "althara_summary": "Althara reading for test",
    "tags": "test,neon",
    "used_in_social": false
}'
```

**Minimum required example:**

```json
{
  "title": "Example news",
  "source": "Example Source",
  "url": "https://example.com/news",
  "published_at": "2025-12-05T10:30:00Z",
  "category": "NOTICIAS_INMOBILIARIAS",
  "used_in_social": false
}
```

### 3. List news (GET /news)

```bash
# List all news
curl http://localhost:8000/api/news

# Filter by domain (tech | real_estate)
curl "http://localhost:8000/api/news?domain=tech"
curl "http://localhost:8000/api/news?domain=real_estate"

# Filter by category
curl "http://localhost:8000/api/news?category=PRECIOS_VIVIENDA"

# Only news with IG draft
curl "http://localhost:8000/api/news?only_with_draft=true"

# Order by relevance (tech)
curl "http://localhost:8000/api/news?domain=tech&order_by=relevance_score"

# Search in title
curl "http://localhost:8000/api/news?q=housing"

# Filter by date range
curl "http://localhost:8000/api/news?from_date=2025-12-01T00:00:00Z&to_date=2025-12-31T23:59:59Z"

# Combine filters
curl "http://localhost:8000/api/news?category=NOTICIAS_HIPOTECAS&q=mortgage&from_date=2025-12-01T00:00:00Z"
```

### 4. Get news by ID (GET /news/{id})

```bash
curl http://localhost:8000/api/news/{id}
```

Replace `{id}` with the news UUID from the POST response.

### 5. Test ingestion and adaptation (POST /admin/ingest-and-adapt)

```bash
# Full pipeline: ingest + adapt
curl -X POST "http://localhost:8000/api/admin/ingest-and-adapt" | python3 -m json.tool
```

**Expected response:**

```json
{
  "ingested": 15,
  "ingested_by_source": {
    "Expansion Inmobiliario": 5,
    "BOE Subastas": 3,
    ...
  },
  "adapted": 20,
  "message": "Full pipeline: 15 ingested, 20 adapted"
}
```

**Individual endpoints:**

```bash
# Ingest only
curl -X POST "http://localhost:8000/api/admin/ingest"

# Adapt only
curl -X POST "http://localhost:8000/api/admin/adapt-pending"
```

### Verify Neon works

After creating news with POST, run:

```bash
curl http://localhost:8000/api/news
```

If you get an array with the news you created:

- ✅ FastAPI works
- ✅ Alembic created the table in Neon
- ✅ Neon connection OK
- ✅ Basic endpoints OK

---

## 📁 Project Structure

```
althara-news-service/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   ├── constants.py
│   ├── routers/
│   │   ├── news.py
│   │   └── admin.py
│   ├── models/
│   │   └── news.py
│   ├── schemas/
│   │   └── news.py
│   ├── ingestion/
│   │   ├── rss_ingestor.py
│   │   └── idealista_client.py
│   ├── utils/
│   │   ├── html_utils.py
│   │   ├── rss_utils.py
│   │   ├── guardrails.py
│   │   └── text_compaction.py
│   └── adapters/
│       └── news_adapter.py
├── alembic/
├── scripts/
├── tests/
├── alembic.ini
├── requirements.txt
├── .env
├── README.md
└── REFACTOR_NOTES.md
```

---

## 🛠️ Technologies

- **FastAPI** – Modern web framework
- **SQLAlchemy** – Async ORM for Python
- **Alembic** – Database migrations
- **Pydantic** – Data validation and schemas
- **asyncpg** – Async PostgreSQL driver
- **Uvicorn** – ASGI server
- **Neon** – Serverless PostgreSQL
- **feedparser** – RSS/Atom feed parser for ingestion

---

## 🔧 Resolved Issues

### Issue 1: `psycopg2` error

**Error:** `ModuleNotFoundError: No module named 'psycopg2'`

**Cause:** URL used `postgresql://` instead of `postgresql+asyncpg://`

**Solution:** Code now converts `postgresql://` → `postgresql+asyncpg://` via `normalize_database_url()` in `app/database.py` and `alembic/env.py`

### Issue 2: `sslmode` parameter error

**Error:** `TypeError: connect() got an unexpected keyword argument 'sslmode'`

**Cause:** `asyncpg` does not accept `sslmode` in the URL

**Solution:** Code removes incompatible params (`sslmode`, `channel_binding`). asyncpg handles SSL automatically.

---

## 🔄 Automation

The system is ready for external automation. `POST /api/admin/ingest-and-adapt` runs the full pipeline in one call.

### Automation Options

#### Option 1: Online cron (recommended)

**cron-job.org** (free):

1. Go to [cron-job.org](https://cron-job.org)
2. Create account
3. Create a new cron job:
   - **URL:** `https://your-domain.com/api/admin/ingest-and-adapt`
   - **Method:** POST
   - **Schedule:** Once per week (e.g. Sundays 6 AM)
   - ✅ Done!

#### Option 2: Vercel Cron (if deploying on Vercel)

Create `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/admin/ingest-and-adapt",
      "schedule": "0 6 * * 0"
    }
  ]
}
```

#### Option 3: Local script + cron

Use `scripts/ingest_news.py`:

```bash
# In crontab (crontab -e)
0 6 * * 0 cd /path/to/project && source venv/bin/activate && python scripts/ingest_news.py
```

### Recommended frequency

- **Once per week** is enough to keep content updated without overloading the database
- With 5 per source limit, each run adds max ~40 new news items
- Deduplication avoids duplicates automatically

---

## 🎯 Next Steps (Optional)

The system is **fully functional**. Optional expansions:

1. 🔜 Connect with frontend to display news
2. 🔜 Add more RSS sources if needed
3. 🔜 Improve adapter with AI (GPT/Claude) for more personalized summaries
4. 🔜 Add advanced filters to the news endpoint
5. 🔜 More sophisticated tagging

---

## 🐛 Troubleshooting

### Error running `alembic upgrade head`

**Common issues:**

- **`DATABASE_URL` not found**
  - Ensure `.env` exists in the project root
  - Ensure it has exactly that name (with the leading dot)

- **Connection error**
  - Check your Neon URL
  - Check the Neon project is active in the dashboard
  - Use `postgresql+asyncpg://` (code converts automatically)

- **`ModuleNotFoundError: No module named 'psycopg2'`**
  - Ensure the URL starts with `postgresql+asyncpg://`

- **`TypeError: connect() got an unexpected keyword argument 'sslmode'`**
  - Code removes this param automatically
  - Ensure you are on the latest version

### Error starting uvicorn

- Ensure dependencies are installed: `pip install -r requirements.txt`
- Ensure the virtual environment is activated
- Ensure `DATABASE_URL` is in `.env`
- Check error logs for details

### 404 on endpoints

- Use `/api/health` and `/api/news` (with `/api` prefix)
- Endpoints are under `/api/` as defined in `app/main.py`
- `/` does not exist (404 is normal)

### Error: "Table already exists"

- Not critical; it means the table already exists
- You can continue testing normally

---

## 📝 Important Notes

- **Automatic normalization:** Code normalizes database URLs
- **Automatic SSL:** asyncpg handles SSL; no params needed
- **Reload mode:** Server runs with `--reload`; changes apply automatically
- **`/api` prefix:** All endpoints are under `/api/`
- **Volume limit:** 5 news per source (max ~40 per run)
- **Deduplication:** Duplicates avoided by comparing URLs
- **Idealista:** Has no news API; we only use legal RSS sources

---

## ✅ Final Summary

The microservice is **fully functional** and production-ready:

- ✅ Database connected (Neon PostgreSQL)
- ✅ 8 real RSS sources configured
- ✅ Automatic ingestion system
- ✅ Althara adapter for news transformation
- ✅ Volume control (5 per source)
- ✅ All-in-one endpoint for automation
- ✅ 21 real estate categories defined
- ✅ Full pipeline: Ingest → Adapt → Query

---

## 🎛 News Studio (UI)

Internal interface for Marketing: brand selector, inbox, IG drafts and editor.

### Access

- **URL**: `GET /ui`
- **Authentication**: BasicAuth when `UI_USER` and `UI_PASS` are set in `.env`:
  ```env
  UI_USER=admin
  UI_PASS=your_secure_password
  ```
- Without credentials configured, the UI is open (development only).

### Flow

1. **Brand selector**: Choose Althara (real_estate) or Oxono (tech)
2. **Portal**: Inbox | Drafts | Approved, with filters (date, query, category, only_without_draft)
3. **News detail**: View news + "Generate IG" / "Generate variants" buttons
4. **IG Editor**: Edit hook, carousel (5 slides), caption, hashtags, CTA. Copy caption/carousel/all. Approve / Mark published

### "Generate more news" button

- **Althara**: Calls `POST /api/admin/ingest-and-adapt?generate_ig=true`
- **Oxono**: Calls `POST /api/tech/admin/ingest-and-generate`

---

## 🔄 "Generate more" Endpoints

| Brand   | Endpoint                                           | Description                                      |
|---------|----------------------------------------------------|--------------------------------------------------|
| Althara | `POST /api/admin/ingest-and-adapt?generate_ig=true` | Ingest real estate RSS, adapt and generate drafts |
| Oxono   | `POST /api/tech/admin/ingest-and-generate`          | Ingest tech RSS and generate drafts for new news  |

For IG mutations (generate, variants, approve, publish) you can use `X-INGEST-TOKEN` if `INGEST_TOKEN` is set in `.env`.

---

## 🌐 Frontend Integration

### Althara web (real estate)

**No changes needed.** Existing `GET /api/news` calls work the same. By default, without `domain`, the API returns only `real_estate` news.

```http
GET /api/news?limit=20&offset=0&used_in_social=false
```

### Oxono web (tech) or other consumers

To show only tech news, add `domain=tech`:

```http
GET /api/news?domain=tech&limit=20&offset=0
```

### List all news (admin/studio)

```http
GET /api/news?domain=all&limit=50
```

### Response fields

Each news item may include:
- `domain`: `"real_estate"` | `"tech"`
- `relevance_score`: number or `null` (tech only)

---

## 📡 Adding new tech RSS feeds

Edit `app/constants_tech.py`, add to `TECH_RSS_SOURCES`:

```python
{"name": "Name", "url": "https://...", "source": "Source", "default_category": TechNewsCategory.OTHER_TECH},
```

---

## 📄 License

This project is private and owned by Althara.

---

**Last updated:** February 2026
