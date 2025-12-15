#!/bin/bash
# Wrapper script to run ingestion from cron
# This script activates the virtual environment and runs the ingestion script

cd /Users/caterinaaracil/althara-news-service
source venv/bin/activate
python3 scripts/ingest_news.py >> /tmp/althara_ingest.log 2>&1





