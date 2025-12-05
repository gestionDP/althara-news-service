# althara-news-service

Microservicio de noticias desarrollado con FastAPI, SQLAlchemy async y Alembic.

## Requisitos

- Python 3.11+
- PostgreSQL

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/gestionDP/althara-news-service.git
cd althara-news-service
```

2. Crear un entorno virtual:
```bash
python3.11 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env y configurar DATABASE_URL
```

5. Ejecutar migraciones:
```bash
alembic upgrade head
```

## Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

## Documentación

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

- `GET /api/health` - Health check
- `POST /api/news` - Crear noticia
- `GET /api/news` - Listar noticias (con filtros: category, from, to, q)
- `GET /api/news/{id}` - Obtener noticia por ID

## Estructura del proyecto

```
althara-news-service/
├── app/
│   ├── main.py          # Aplicación FastAPI
│   ├── database.py      # Configuración de base de datos
│   ├── routers/
│   │   └── news.py      # Endpoints de noticias
│   ├── models/
│   │   └── news.py      # Modelo SQLAlchemy
│   └── schemas/
│       └── news.py      # Schemas Pydantic
├── alembic/             # Migraciones
├── alembic.ini          # Configuración Alembic
├── requirements.txt     # Dependencias
└── .env.example         # Ejemplo de variables de entorno

```

