#!/usr/bin/env bash

echo "🧹 CLEAN RUN INITIALISATIE"

echo "1️⃣ Stop uvicorn indien actief"
pkill -f uvicorn || true
sleep 1

echo "2️⃣ Reset zombie runs in database"
sqlite3 data/local_app.db <<'SQL'
UPDATE runs
SET
  status = 'error',
  steps_json = json_set(
    coalesce(steps_json, '{}'),
    '$.compute_kpis', 'failed',
    '$.generate_chapters', 'skipped',
    '$.render_pdf', 'skipped'
  ),
  updated_at = datetime('now')
WHERE status = 'running';
SQL

echo "3️⃣ Start backend in volledig schone runtime"
export LOG_LEVEL=INFO
export PYTHONUNBUFFERED=1
export PIPELINE_TEST_MODE=false

uvicorn backend.main:app --reload
