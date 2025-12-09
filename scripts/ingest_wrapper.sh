#!/bin/bash
# Wrapper script para ejecutar la ingestión desde cron
# Este script activa el entorno virtual y ejecuta el script de ingestión

cd /Users/caterinaaracil/althara-news-service
source venv/bin/activate
python3 scripts/ingest_news.py >> /tmp/althara_ingest.log 2>&1



