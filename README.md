# althara-news-service

Microservicio de noticias inmobiliarias desarrollado con FastAPI, SQLAlchemy async y Alembic, conectado a Neon PostgreSQL.

---

## 📋 Índice

- [Resumen del Proyecto](#resumen-del-proyecto)
- [Lo que se Completó](#lo-que-se-completó)
- [Requisitos](#requisitos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Estado Actual](#estado-actual)
- [Documentación de la API](#documentación-de-la-api)
- [Endpoints](#endpoints)
- [Ingestión de Noticias](#ingestión-de-noticias)
- [Adapter Althara](#adapter-althara)
- [Categorías de Noticias](#categorías-de-noticias)
- [Pruebas del Microservicio](#pruebas-del-microservicio)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Automatización](#automatización)
- [Tecnologías](#tecnologías)
- [Problemas Resueltos](#problemas-resueltos)
- [Próximos Pasos](#próximos-pasos)
- [Troubleshooting](#troubleshooting)

---

## 📝 Resumen del Proyecto

Este microservicio proporciona una API REST para gestionar noticias inmobiliarias. Permite crear, listar y consultar noticias con diferentes categorías predefinidas, conectándose a una base de datos PostgreSQL en Neon mediante SQLAlchemy async.

---

## ✅ Lo que se Completó

### BLOQUE 1: Configuración de Alembic (Migraciones Async) ✅

- ✅ `alembic.ini` configurado sin URL fija (usa variable de entorno)
- ✅ `alembic/env.py` configurado para modo async con `async_engine_from_config`
- ✅ Migración inicial creada: `001_initial_migration_create_news_table.py`
- ✅ Normalización automática de URLs de base de datos

### BLOQUE 2: Modelo SQLAlchemy `News` ✅

- ✅ Modelo `News` completo con todos los campos:
  - `id` (UUID, PK)
  - `title`, `source`, `url`, `published_at`, `category`
  - `raw_summary`, `althara_summary`, `tags`
  - `used_in_social` (Boolean)
  - `created_at`, `updated_at` (timestamps automáticos)

### BLOQUE 3: Schemas Pydantic ✅

- ✅ `NewsBase` - Campos base
- ✅ `NewsCreate` - Para crear noticias (sin id, timestamps)
- ✅ `NewsRead` - Para leer noticias (incluye todos los campos)

### BLOQUE 4: Router Completo ✅

- ✅ `GET /api/health` - Health check
- ✅ `POST /api/news` - Crear noticia
- ✅ `GET /api/news` - Listar noticias (con filtros)
- ✅ `GET /api/news/{id}` - Obtener noticia por ID

### BLOQUE 5: Conexión a Neon y Pruebas ✅

- ✅ Conexión a Neon PostgreSQL configurada
- ✅ Migraciones ejecutadas correctamente
- ✅ Tabla `news` creada en Neon
- ✅ Servidor FastAPI funcionando
- ✅ Endpoints probados y funcionando

### EXTRAS: Categorías Definidas ✅

- ✅ 21 categorías inmobiliarias documentadas en `app/constants.py`
- ✅ Constantes disponibles para uso en el código

### BLOQUE 6: Sistema de Ingestión ✅

- ✅ Configuración con Pydantic Settings (`app/config.py`)
- ✅ 8 fuentes RSS reales configuradas (`app/ingestion/rss_ingestor.py`)
- ✅ Router de administración (`app/routers/admin.py`)
- ✅ Endpoints para disparar ingestión (`/api/admin/ingest`)

### BLOQUE 7: Adapter Althara ✅

- ✅ Adapter para transformar noticias al tono Althara (`app/adapters/news_adapter.py`)
- ✅ Función `build_althara_summary()` con tono analítico por categoría
- ✅ Endpoint para adaptar noticias pendientes (`POST /api/admin/adapt-pending`)
- ✅ Pipeline completo: Ingesta → Adaptación → Consulta

### BLOQUE 8: Automatización y Control de Volumen ✅

- ✅ Límite configurado: 5 noticias por fuente (máximo ~40 por ejecución)
- ✅ Endpoint todo-en-uno: `POST /api/admin/ingest-and-adapt` (pipeline completo)
- ✅ Sistema de deduplicación automática por URL
- ✅ Listo para automatización con servicios externos (cron-jobs, servicios cloud)

---

## 🛠️ Requisitos

- Python 3.11+
- PostgreSQL (Neon)
- Cuenta en Neon con proyecto creado

---

## 🚀 Instalación y Configuración

### 1. Crear ambiente virtual

```bash
python3.11 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar requirements

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

**Crear un archivo `.env` en la raíz del proyecto** con tu URL de Neon:

```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:TU_PASSWORD@ep-xxx-xxx-pooler.us-east-1.aws.neon.tech/neondb
```

**Puntos importantes:**

- ⚠️ **Debe empezar por `postgresql+asyncpg://`** (no solo `postgresql://`) para conexiones async
- Obtén tu `DATABASE_URL` desde el dashboard de Neon
- El archivo `.env` ya está en `.gitignore`, así que tus credenciales están seguras
- ⚡ **Normalización automática**: El código convierte automáticamente:
  - `postgresql://` → `postgresql+asyncpg://`
  - Elimina parámetros incompatibles (`sslmode`, `channel_binding`)
  - asyncpg maneja SSL automáticamente

**Ejemplo de formato completo:**

```
DATABASE_URL=postgresql+asyncpg://usuario:password@host:puerto/database
```

**Nota:** Si copias la URL directamente de Neon y tiene `postgresql://` o parámetros SSL, el código los normalizará automáticamente.

### 4. Ejecutar migraciones

Con el entorno virtual activado, ejecutar:

```bash
alembic upgrade head
```

Esto creará la tabla `news` en tu base de datos Neon.

**Salida esperada:**

```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial, Initial migration: create news table
```

### 5. Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

**Salida esperada:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

---

## ✅ Estado Actual

### Completado y Funcionando:

- ✅ **Base de datos Neon** - Conectada y funcionando
- ✅ **Migraciones Alembic** - Tabla `news` creada
- ✅ **Servidor FastAPI** - Corriendo en `http://localhost:8000`
- ✅ **Conexión async** - SQLAlchemy async funcionando correctamente
- ✅ **Health Check** - `GET /api/health` responde `{"status": "ok"}`
- ✅ **Endpoints CRUD** - Todos los endpoints básicos funcionando
- ✅ **Normalización de URLs** - Manejo automático de parámetros SSL

### Sistema Completo y Funcionando:

- ✅ **Ingestor de noticias RSS** - 8 fuentes reales configuradas
- ✅ **Adapter Althara** - Transformación automática al tono Althara
- ✅ **Control de volumen** - Límite de 5 noticias por fuente
- ✅ **Automatización** - Endpoint todo-en-uno listo para servicios externos

---

## 📖 Documentación de la API

- **Swagger UI**: `http://localhost:8000/docs` → Interfaz interactiva para probar endpoints
- **ReDoc**: `http://localhost:8000/redoc` → Documentación alternativa

---

## 🔌 Endpoints

### Health Check

- `GET /api/health` - Health check del servicio
  - Respuesta: `{"status": "ok"}`

### Noticias

- `POST /api/news` - Crear una nueva noticia

  - Body: `NewsCreate` (JSON)
  - Respuesta: `NewsRead` (con id, timestamps)

- `GET /api/news` - Listar noticias

  - Query params opcionales:
    - `category` (str) - Filtrar por categoría
    - `q` (str) - Buscar en título
    - `from_date` (datetime) - Fecha desde
    - `to_date` (datetime) - Fecha hasta
  - Respuesta: Array de `NewsRead`

- `GET /api/news/{id}` - Obtener noticia por ID
  - Path param: `id` (UUID)
  - Respuesta: `NewsRead` o 404

### Administración - Ingestión y Adaptación

- `POST /api/admin/ingest` - Ingestar noticias desde todas las fuentes RSS

  - Límite: 5 noticias por fuente (máximo ~40 por ejecución)
  - Respuesta: `{"Expansion Inmobiliario": <int>, "Cinco Días - Economía Inmobiliaria": <int>, ...}`

- `POST /api/admin/ingest/rss` - Alias del endpoint principal (mismo resultado)

- `POST /api/admin/adapt-pending` - Adaptar noticias pendientes al tono Althara

  - Busca noticias con `althara_summary = NULL` y las adapta
  - Respuesta: `{"adapted": <int>, "message": "..."}`

- `POST /api/admin/ingest-and-adapt` - Pipeline completo (todo-en-uno)

  - Ejecuta ingesta (5 por fuente) + adaptación en una sola llamada
  - Ideal para automatización externa (cron-jobs, servicios cloud)
  - Respuesta: `{"ingested": <int>, "ingested_by_source": {...}, "adapted": <int>, "message": "..."}`

---

## 📥 Ingestión de Noticias

El microservicio incluye un sistema de ingestión para obtener noticias automáticamente desde fuentes externas.

### Fuentes Disponibles

⚠️ **IMPORTANTE: Idealista NO tiene API de noticias**

Idealista NO ofrece una API pública para obtener noticias. Su API solo incluye búsqueda de propiedades y datos de mercado.

**Nota sobre Newsletter de Idealista:** Aunque Idealista tiene una newsletter semanal por email, no es viable automatizarla porque:

- Solo está disponible por email (no RSS/API)
- Requeriría parsing complejo de emails HTML
- Las fuentes RSS que tenemos son mejores: automáticas, legales y estables

**Fuentes reales configuradas (8 fuentes RSS):**

1. **RSS - Expansion Inmobiliario** - Noticias de mercado, hipotecas, inversión
2. **RSS - Cinco Días** - Economía inmobiliaria
3. **RSS - El Economista** - Vivienda y mercado
4. **RSS - BOE Subastas** - Subastas inmobiliarias
5. **RSS - BOE General** - Normativas y leyes
6. **RSS - Observatorio Inmobiliario** - Análisis del sector
7. **RSS - Interempresas Construcción** - Noticias de construcción
8. **RSS - ArchDaily** - Arquitectura y construcción

### Endpoints de Administración

#### Ingestar Noticias desde Fuentes RSS

```bash
POST /api/admin/ingest
# O también:
POST /api/admin/ingest/rss
```

**Respuesta:**

```json
{
  "Expansion Inmobiliario": 10,
  "Cinco Días - Economía Inmobiliaria": 5,
  "El Economista - Vivienda": 8,
  "BOE Subastas": 3,
  "BOE General": 2,
  "Observatorio Inmobiliario": 4,
  "Interempresas Construcción": 6,
  "Plataforma Arquitectura": 3
}
```

**Descripción:** Ingesta noticias desde todas las fuentes RSS configuradas (8 fuentes reales). El sistema evita duplicados comparando las URLs.

**Límite configurado:** Máximo 5 noticias por fuente por ejecución (total máximo ~40 noticias). Esto controla el volumen y mantiene solo las más recientes.

**Nota:** Idealista NO tiene API de noticias, por eso solo usamos fuentes RSS legales.

### Ejemplo de Uso

**Usando curl:**

```bash
# Ingestar noticias desde todas las fuentes RSS
curl -X POST "http://localhost:8000/api/admin/ingest"

# O usando el alias
curl -X POST "http://localhost:8000/api/admin/ingest/rss"
```

**Usando Swagger UI:**

1. Ve a `http://localhost:8000/docs`
2. Busca la sección `admin`
3. Expande `POST /api/admin/ingest`
4. Haz clic en "Try it out" y luego "Execute"

### Configuración de Fuentes RSS

Las fuentes RSS están configuradas en `app/ingestion/rss_ingestor.py` en la variable `RSS_SOURCES`.

**Fuentes RSS actuales (reales y funcionales):**

- Expansion Inmobiliario: `https://e00-expansion.uecdn.es/rss/inmobiliario.xml`
- Cinco Días: `https://cincodias.elpais.com/rss/act/economia_inmobiliaria/`
- El Economista: `https://www.eleconomista.es/rss/rss-vivienda.php`
- BOE Subastas: `https://subastas.boe.es/rss.php`
- BOE General: `https://www.boe.es/diario_boe/xml.php?id=BOE-S`
- Observatorio Inmobiliario: `https://www.observatorioinmobiliario.es/rss/`
- Interempresas Construcción: `https://www.interempresas.net/construccion/RSS/`
- ArchDaily: `https://www.archdaily.mx/mx/rss`

Ver `FUENTES_RSS.md` para más detalles sobre cada fuente.

### Control de Volumen

- **Límite configurado:** 5 noticias por fuente por ejecución
- **Máximo por ejecución:** ~40 noticias (8 fuentes × 5)
- **Deduplicación automática:** El sistema evita insertar noticias duplicadas comparando la URL
- **Control de calidad:** Solo las noticias más recientes se procesan

### Notas Importantes

- **Idealista NO tiene API de noticias:** Su API solo incluye búsqueda de propiedades, no noticias. Por eso no tenemos endpoint de Idealista.
- **Newsletter de Idealista:** Aunque existe, no es viable automatizarla (solo email, no RSS/API). Las fuentes RSS son mejores.
- **Fuentes RSS reales:** Todas las noticias vienen de 8 fuentes RSS legales y funcionando (Expansion, BOE, Cinco Días, etc.)
- **Deduplicación:** El sistema evita insertar noticias duplicadas comparando la URL
- **Configuración:** Todas las fuentes RSS están listas y funcionando. No se requiere configuración adicional.

---

## 🎨 Adapter Althara

El sistema incluye un adapter para transformar noticias al tono Althara, ideal para redes sociales.

### Endpoint de Adaptación

- `POST /api/admin/adapt-pending` - Adapta noticias pendientes al tono Althara

  - Busca todas las noticias con `althara_summary = NULL`
  - Las transforma usando el adapter Althara
  - Guarda el resultado en `althara_summary`
  - Respuesta: `{"adapted": <número>, "message": "..."}`

### Cómo Funciona

El adapter genera un resumen estructurado:

1. **Primera línea:** Resumen frío del hecho (título + resumen recortado)
2. **Líneas siguientes:** Interpretación analítica según la categoría
3. **Sin fuente:** La fuente se añadirá en el frontend

### Tono Analítico por Categoría

El adapter usa diferentes tonos analíticos según la categoría:

- **PRECIOS_VIVIENDA:** Análisis de tendencias de mercado
- **FONDOS_INVERSION:** Evolución de estrategias de inversión
- **GRANDES_INVERSIONES:** Dinámicas sectoriales
- **NOTICIAS_HIPOTECAS:** Indicadores de salud del mercado
- **NOTICIAS_BOE_SUBASTAS:** Oportunidades que requieren análisis técnico
- **NORMATIVAS:** Impacto en el ecosistema inmobiliario
- **CONSTRUCCION:** Tendencias de demanda y evolución del sector

### Pipeline Completo

**Opción 1: Pasos separados**

```
1. POST /api/admin/ingest          → Ingesta noticias (raw_summary)
2. POST /api/admin/adapt-pending   → Adapta al tono Althara (althara_summary)
3. GET /api/news                   → Noticias listas para redes sociales
```

**Opción 2: Todo-en-uno (recomendado para automatización)**

```
1. POST /api/admin/ingest-and-adapt → Ingesta + Adapta en una sola llamada
2. GET /api/news                    → Noticias listas para redes sociales
```

El endpoint `/ingest-and-adapt` es ideal para automatización externa (cron-jobs, servicios cloud) porque ejecuta todo el pipeline de una vez.

---

## 📂 Categorías de Noticias

El sistema utiliza 21 categorías definidas para noticias inmobiliarias. Todas las constantes están en `app/constants.py`.

### Fondos e Inversión

- `FONDOS_INVERSION_INMOBILIARIA` - Fondos de inversión inmobiliaria
- `GRANDES_INVERSIONES_INMOBILIARIAS` - Noticias grandes inversiones inmobiliarias
- `MOVIMIENTOS_GRANDES_TENEDORES` - Movimientos de grandes tenedores
- `TOKENIZATION_ACTIVOS` - Tokenization activos

### Noticias Generales

- `NOTICIAS_INMOBILIARIAS` - Noticias inmobiliarias
- `NOTICIAS_HIPOTECAS` - Noticias hipotecas
- `NOTICIAS_LEYES_OKUPAS` - Noticias leyes okupas
- `NOTICIAS_BOE_SUBASTAS` - Noticias BOE subastas inmobiliarias
- `NOTICIAS_DESAHUCIOS` - Noticias desahucios
- `NOTICIAS_CONSTRUCCION` - Noticias sobre construcción

### Precios y Mercado

- `PRECIOS_VIVIENDA` - Precios de vivienda
- `PRECIOS_MATERIALES` - Precios materiales
- `PRECIOS_SUELO` - Precios del suelo

### Análisis y Tendencias

- `FUTURO_SECTOR_INMOBILIARIO` - Futuro sector inmobiliario
- `BURBUJA_INMOBILIARIA` - Burbuja inmobiliaria

### Alquiler y Normativas

- `ALQUILER_VACACIONAL` - Alquiler vacacional
- `NORMATIVAS_VIVIENDAS` - Normativas de viviendas
- `FALTA_VIVIENDA` - Falta de vivienda

### Construcción y Urbanización

- `NOTICIAS_URBANIZACION` - Noticias sobre urbanización
- `NOVEDADES_CONSTRUCCION` - Novedades de construcción
- `CONSTRUCCION_MODULAR` - Construcción modular

---

## 🧪 Pruebas del Microservicio

### 1. Health Check

```bash
curl http://localhost:8000/api/health
```

Respuesta esperada:

```json
{
  "status": "ok"
}
```

### 2. Crear una noticia (POST /news)

**Opción A: Usando Swagger UI (Recomendado)**

1. Ve a `http://localhost:8000/docs`
2. Expande `POST /api/news`
3. Haz clic en "Try it out"
4. Usa este JSON:

```json
{
  "title": "Prueba conexión Neon",
  "source": "Test Local",
  "url": "https://example.com/test",
  "published_at": "2025-12-05T10:30:00Z",
  "category": "PRECIOS_VIVIENDA",
  "raw_summary": "Resumen bruto de prueba",
  "althara_summary": "Lectura Althara de prueba",
  "tags": "test,neon",
  "used_in_social": false
}
```

5. Haz clic en "Execute"

**Opción B: Usando curl**

```bash
curl -X POST "http://localhost:8000/api/news" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Prueba conexión Neon",
    "source": "Test Local",
    "url": "https://example.com/test",
    "published_at": "2025-12-05T10:30:00Z",
    "category": "PRECIOS_VIVIENDA",
    "raw_summary": "Resumen bruto de prueba",
    "althara_summary": "Lectura Althara de prueba",
    "tags": "test,neon",
    "used_in_social": false
}'
```

**Ejemplo mínimo requerido:**

```json
{
  "title": "Nueva noticia de ejemplo",
  "source": "Ejemplo Source",
  "url": "https://example.com/noticia",
  "published_at": "2025-12-05T10:30:00Z",
  "category": "NOTICIAS_INMOBILIARIAS",
  "used_in_social": false
}
```

### 3. Listar noticias (GET /news)

```bash
# Listar todas las noticias
curl http://localhost:8000/api/news

# Filtrar por categoría
curl "http://localhost:8000/api/news?category=PRECIOS_VIVIENDA"

# Buscar por texto en título
curl "http://localhost:8000/api/news?q=vivienda"

# Filtrar por rango de fechas
curl "http://localhost:8000/api/news?from_date=2025-12-01T00:00:00Z&to_date=2025-12-31T23:59:59Z"

# Combinar filtros
curl "http://localhost:8000/api/news?category=NOTICIAS_HIPOTECAS&q=hipoteca&from_date=2025-12-01T00:00:00Z"
```

### 4. Obtener una noticia por ID (GET /news/{id})

```bash
curl http://localhost:8000/api/news/{id}
```

Reemplaza `{id}` con el UUID de la noticia obtenido en el POST anterior.

### 5. Probar ingesta y adaptación (POST /admin/ingest-and-adapt)

```bash
# Pipeline completo: ingesta + adaptación
curl -X POST "http://localhost:8000/api/admin/ingest-and-adapt" | python3 -m json.tool
```

**Respuesta esperada:**

```json
{
  "ingested": 15,
  "ingested_by_source": {
    "Expansion Inmobiliario": 5,
    "BOE Subastas": 3,
    "Cinco Días - Economía Inmobiliaria": 2,
    ...
  },
  "adapted": 20,
  "message": "Pipeline completo: 15 noticias ingeridas, 20 adaptadas"
}
```

**También puedes probar los endpoints individuales:**

```bash
# Solo ingesta
curl -X POST "http://localhost:8000/api/admin/ingest"

# Solo adaptación
curl -X POST "http://localhost:8000/api/admin/adapt-pending"
```

### Verificar que funciona con Neon

Después de crear una noticia con POST, ejecuta:

```bash
curl http://localhost:8000/api/news
```

Si te devuelve un array con la noticia que acabas de crear, significa:

- ✅ FastAPI funciona
- ✅ Alembic creó la tabla en Neon
- ✅ Conexión con Neon OK
- ✅ Endpoints básicos OK

---

## 📁 Estructura del proyecto

```
althara-news-service/
├── app/
│   ├── main.py              # Aplicación FastAPI
│   ├── database.py          # Configuración de base de datos async (con normalización de URLs)
│   ├── config.py            # Configuración con Pydantic Settings
│   ├── constants.py         # Constantes y categorías
│   ├── routers/
│   │   ├── news.py          # Endpoints de noticias
│   │   └── admin.py         # Endpoints de administración (ingestión y adaptación)
│   ├── models/
│   │   └── news.py          # Modelo SQLAlchemy async
│   ├── schemas/
│   │   └── news.py          # Schemas Pydantic (NewsBase, NewsCreate, NewsRead)
│   ├── ingestion/
│   │   ├── rss_ingestor.py  # Ingestor de fuentes RSS
│   │   └── idealista_client.py  # Cliente mock para Idealista (no usado para noticias)
│   └── adapters/
│       └── news_adapter.py  # Adapter para transformar noticias al tono Althara
├── alembic/                 # Migraciones
│   ├── env.py               # Configuración async de Alembic (con normalización de URLs)
│   └── versions/
│       └── 001_initial_migration_create_news_table.py
├── scripts/
│   └── ingest_news.py       # Script standalone para ingestión (cron jobs)
├── alembic.ini              # Configuración Alembic (sin URL fija)
├── requirements.txt         # Dependencias
├── .env                     # Variables de entorno (crear manualmente)
└── README.md                # Este archivo
```

---

## 🛠️ Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM async para Python
- **Alembic**: Herramienta de migraciones de base de datos
- **Pydantic**: Validación de datos y schemas
- **asyncpg**: Driver async para PostgreSQL
- **Uvicorn**: Servidor ASGI
- **Neon**: PostgreSQL serverless
- **feedparser**: Parser de feeds RSS/Atom para ingestión de noticias

---

## 🔧 Problemas Resueltos

### Problema 1: Error con `psycopg2`

**Error:** `ModuleNotFoundError: No module named 'psycopg2'`

**Causa:** La URL usaba `postgresql://` en lugar de `postgresql+asyncpg://`

**Solución:**

- Código actualizado para convertir automáticamente `postgresql://` → `postgresql+asyncpg://`
- Función `normalize_database_url()` en `app/database.py` y `alembic/env.py`

### Problema 2: Error con parámetro `sslmode`

**Error:** `TypeError: connect() got an unexpected keyword argument 'sslmode'`

**Causa:** `asyncpg` no acepta `sslmode` como parámetro de URL

**Solución:**

- Código actualizado para eliminar automáticamente parámetros incompatibles (`sslmode`, `channel_binding`)
- asyncpg maneja SSL automáticamente

---

## 🔄 Automatización

El sistema está listo para automatización externa. El endpoint `POST /api/admin/ingest-and-adapt` ejecuta todo el pipeline de una vez.

### Opciones de Automatización

#### Opción 1: Servicios de Cron Online (Recomendado)

**cron-job.org** (gratis):

1. Ve a [cron-job.org](https://cron-job.org)
2. Crea cuenta
3. Crea un nuevo cron job:
   - **URL:** `https://tu-dominio.com/api/admin/ingest-and-adapt`
   - **Método:** POST
   - **Schedule:** Una vez por semana (ej: domingos 6 AM)
   - ✅ Listo!

#### Opción 2: Vercel Cron (Si despliegas en Vercel)

Crea `vercel.json`:

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

#### Opción 3: Script Local + Cron

Si prefieres usar cron local, puedes usar el script `scripts/ingest_news.py`:

```bash
# En crontab (crontab -e)
0 6 * * 0 cd /ruta/al/proyecto && source venv/bin/activate && python scripts/ingest_news.py
```

### Frecuencia Recomendada

- **Una vez por semana** es suficiente para mantener el contenido actualizado sin saturar la base de datos
- Con el límite de 5 por fuente, cada ejecución añadirá máximo ~40 noticias nuevas
- La deduplicación evita duplicados automáticamente

---

## 🎯 Próximos Pasos (Opcional)

El sistema está **100% funcional**. Opciones para expandir:

1. 🔜 **Conectar con frontend** para visualizar noticias
2. 🔜 **Añadir más fuentes RSS** si se necesitan
3. 🔜 **Mejorar el adapter** con IA (GPT/Claude) para resúmenes más personalizados
4. 🔜 **Añadir filtros avanzados** en el endpoint de noticias
5. 🔜 **Sistema de tags** más sofisticado

---

## 🐛 Troubleshooting

### Error al ejecutar `alembic upgrade head`

**Problemas comunes:**

- **`DATABASE_URL` no encontrada**

  - Verifica que el archivo `.env` existe en la raíz del proyecto
  - Verifica que tiene exactamente ese nombre (con el punto al inicio)

- **Error de conexión**

  - Verifica que tu URL de Neon sea correcta
  - Verifica que el proyecto Neon esté activo en el dashboard
  - Verifica que uses `postgresql+asyncpg://` (el código lo convierte automáticamente)

- **`ModuleNotFoundError: No module named 'psycopg2'`**

  - Asegúrate de que la URL empiece con `postgresql+asyncpg://`
  - El código debería convertirla automáticamente, pero verifica tu `.env`

- **`TypeError: connect() got an unexpected keyword argument 'sslmode'`**
  - El código elimina automáticamente este parámetro
  - Verifica que estés usando la última versión del código

### Error al iniciar uvicorn

- Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`
- Verifica que el entorno virtual esté activado
- Verifica que `DATABASE_URL` esté en el archivo `.env`
- Revisa los logs de error para más detalles

### Error 404 en endpoints

- Verifica que uses `/api/health` y `/api/news` (con el prefijo `/api`)
- Los endpoints están bajo el prefijo `/api/` definido en `app/main.py`
- El endpoint `/` no existe (los 404 son normales)

### Error: "Table already exists"

- No es un error grave, significa que la tabla ya existe
- Puedes continuar con las pruebas normalmente

---

## 📝 Notas Importantes

- **Normalización automática**: El código normaliza automáticamente las URLs de base de datos
- **SSL automático**: asyncpg maneja SSL automáticamente, no necesita parámetros
- **Modo reload**: El servidor está en modo `--reload`, los cambios se aplican automáticamente
- **Prefijo `/api`**: Todos los endpoints están bajo el prefijo `/api/`
- **Límite de volumen**: 5 noticias por fuente (máximo ~40 por ejecución)
- **Deduplicación**: El sistema evita duplicados automáticamente comparando URLs
- **Idealista**: NO tiene API de noticias, solo usamos fuentes RSS legales

---

## ✅ Resumen Final

El microservicio está **100% funcional** y listo para producción:

- ✅ Base de datos conectada (Neon PostgreSQL)
- ✅ 8 fuentes RSS reales configuradas
- ✅ Sistema de ingestión automática
- ✅ Adapter Althara para transformar noticias
- ✅ Control de volumen (5 por fuente)
- ✅ Endpoint todo-en-uno para automatización
- ✅ 21 categorías inmobiliarias definidas
- ✅ Pipeline completo: Ingesta → Adaptación → Consulta

**Sistema completo y listo para usar! 🚀**

---

## 📄 Licencia

Este proyecto es privado y propiedad de Althara.

---

**Última actualización:** Diciembre 2025
