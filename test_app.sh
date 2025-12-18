#!/usr/bin/env bash
set -e
# Start backend in background
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!
# Give it a moment to start
sleep 3
# Create a new run (manual paste mode)
RUN_RESPONSE=$(curl -s -X POST http://localhost:8000/runs -H "Content-Type: application/json" -d '{"funda_url":"manual-paste"}')
RUN_ID=$(echo "$RUN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['run_id'])")
echo "Created run $RUN_ID"
# Read test HTML content and escape for JSON
HTML_CONTENT=$(python3 - <<'PY'
import json, sys
content = sys.stdin.read()
print(json.dumps(content))
PY < /Users/marcelkurvers/Development/funda-app/ai-woning-rapport-WERKEND-local/test-data/test-html)
# Paste the content into the run
curl -s -X POST http://localhost:8000/runs/${RUN_ID}/paste -H "Content-Type: application/json" -d "{\"funda_html\":${HTML_CONTENT},\"media_urls\":[],\"extra_facts\":\"\"}"
# Retrieve the report
REPORT=$(curl -s http://localhost:8000/runs/${RUN_ID}/report)
echo "Report JSON:"
echo "$REPORT"
# Stop the server
kill $SERVER_PID
