# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Woning Rapport** - A real estate analysis tool that transforms Funda (Dutch real estate platform) listings into comprehensive, AI-enriched property reports with 13 analysis chapters.

**Core workflow**: User pastes Funda HTML → Parser extracts data → Intelligence Engine enriches with AI → 13 chapter modules generate analysis → Frontend displays Bento Grid dashboard.

## Essential Commands

### Docker (Recommended)
```bash
# Start entire stack (app + Ollama)
docker-compose up --build

# Access points:
# - Frontend/Backend: http://localhost:8001
# - Ollama API: http://localhost:11435
# - API Docs: http://localhost:8001/docs

# Pull Ollama models (required for AI enrichment)
docker-compose exec ollama ollama pull qwen2.5-coder:7b
docker-compose exec ollama ollama pull llama3.1
```

### Backend (Local Development)
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --port 8000

# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_async_pipeline.py

# Run tests with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Frontend (Local Development)
```bash
cd frontend

# Install dependencies
npm install

# Development server (hot reload)
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Lint
npm run lint
```

## Architecture Overview

### Backend Pipeline (main.py)

**Critical**: The pipeline runs asynchronously in a background thread (ThreadPoolExecutor) to avoid blocking the API for 26+ minutes during chapter generation.

**Flow**:
1. **POST /runs** - Create run (stores in SQLite)
2. **POST /runs/{run_id}/start** - Starts background processing, returns immediately
3. **GET /runs/{run_id}/status** - Poll endpoint (frontend polls every 2s)
4. **GET /runs/{run_id}/report** - Fetch final report when status='done'

**Pipeline steps** (`simulate_pipeline()` function):
- `scrape_funda` - Fetch HTML (if URL provided)
- `fetch_external_sources` - Additional data sources
- `compute_kpis` - Calculate metrics
- `generate_chapters` - Process all 13 chapters (SLOWEST: 13 × 30s Ollama timeout)
- `render_pdf` - WeasyPrint PDF generation

### Chapter System

**Location**: `backend/chapters/`

Each chapter (0-12) inherits from `BaseChapter` and implements:
- `generate()` - Returns `ChapterOutput` with title, content, metadata
- Context building with property data normalization

**Chapter registry**: `chapters/registry.py` - Maps chapter IDs to classes
**Intelligence**: `intelligence.py` - `IntelligenceEngine.generate_chapter_narrative()` uses Ollama for AI-enriched content

**Key chapters**:
- **Chapter 0**: Executive Summary (AI-generated overview)
- **Chapter 2**: Preferences Match (Marcel & Petra persona matching)
- **Chapter 12**: Final Recommendation (AI advice)

### Parser (parser.py)

`Parser.parse_html()` extracts ~40 fields from Funda HTML using BeautifulSoup:
- Price, address, living area, plot area
- Build year, energy label, rooms, bedrooms, bathrooms
- Construction type, garage, garden, balcony, roof type
- Heating, insulation, service costs

**Validation**: Min/max thresholds prevent illogical values (e.g., MAX_BEDROOMS=15, MAX_LIVING_AREA=2000)

### Ollama Integration (ollama_client.py)

`OllamaClient` with smart URL detection:
1. Check `OLLAMA_BASE_URL` environment variable
2. Detect Docker environment (`/.dockerenv` file) → use `http://ollama:11434`
3. Fallback to `http://localhost:11434`

**Timeout**: 30 seconds per request (reduced from 120s to prevent long hangs)

### Frontend (React + TypeScript)

**Key components**:
- `App.tsx` - Main orchestration with status polling loop
- `LandingPage.tsx` - Input UI with clipboard image paste support
- `BentoLayout.tsx` - Responsive grid dashboard for chapter display

**Status polling pattern** (App.tsx line 75-96):
```typescript
const pollStatus = async () => {
  const { status } = await fetch(`/runs/${run_id}/status`).then(r => r.json());
  if (status === 'done') { /* fetch report */ }
  else if (status === 'failed') { /* show error */ }
  else { setTimeout(pollStatus, 2000); } // poll again
};
```

### Image Upload

**Backend**: `POST /api/upload/image` endpoint
- Validates image type and size (max 10MB)
- Generates unique UUID filename
- Saves to `/data/uploads/` directory
- Returns URL: `/uploads/{filename}`

**Frontend**: Clipboard paste handler in `LandingPage.tsx`
- Intercepts paste events with images
- Uploads via FormData
- Displays preview grid with delete buttons

## Database

**SQLite**: `data/local_app.db`

**Tables**:
- `runs` - Stores run metadata, status, steps_json, report_json
- Uses JSON columns for flexible data storage

**Environment variable**: `APP_DB` (defaults to `data/local_app.db`, use `:memory:` for tests)

## Testing

### Backend Tests
- **Location**: `backend/tests/`
- **Config**: `pytest.ini` (sets `pythonpath = backend`)
- **Fixtures**: `backend/conftest.py` (session-level test setup)
- **Key test files**:
  - `test_async_pipeline.py` - Background processing tests
  - `test_image_upload.py` - Image upload validation tests

### Frontend Tests
- **Location**: `frontend/src/test/`
- **Config**: `vitest.config.ts`
- **Setup**: `frontend/src/test/setup.ts`
- **Key test files**:
  - `App.test.tsx` - Polling logic tests
  - `LandingPage.test.tsx` - Clipboard paste and UI tests

**Note**: Some frontend tests fail in jsdom due to ClipboardEvent limitations (environment issue, not code bug)

## Docker Build

**Multi-stage Dockerfile** (`backend/Dockerfile`):
1. **Stage 1**: Node.js builder - Builds frontend with `npm run build`
2. **Stage 2**: Python runtime - Installs WeasyPrint dependencies, copies backend + built frontend

**Key dependencies**:
- WeasyPrint requires: `libcairo2`, `libpango-1.0-0`, `fonts-liberation`
- Frontend dist copied to `/app/frontend/dist` and mounted as StaticFiles

## Important Patterns

### Error Handling
- **Never use**: `except: pass` (silent failures)
- **Always**: Log errors with `logger.error(f"...", exc_info=True)`
- **Pattern**: Decide whether to re-raise, return default, or continue

### Static File Mounting
The app conditionally mounts static files to support test environments:
```python
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")
else:
    # Test mode - provide simple root endpoint
    @app.get("/", response_class=HTMLResponse)
    def root():
        return "<html><body>Test Mode</body></html>"
```

### Ollama Timeout Management
- Default timeout: 30 seconds (configurable)
- Chapter generation is the slowest operation (13 chapters × 30s = 390s worst case)
- Background processing ensures UI responsiveness

## Configuration

### Environment Variables
- `APP_DB` - Database path (default: `data/local_app.db`)
- `OLLAMA_BASE_URL` - Ollama API URL (auto-detected if not set)

### Docker Compose Networking
- Service name `ollama` resolves to Ollama container within Docker network
- Port mappings: App (8001→8000), Ollama (11435→11434)

## Known Issues

1. **ClipboardEvent in tests**: jsdom doesn't support ClipboardEvent constructor - this is expected
2. **Old directory conflicts**: `ai-woning-rapport-WERKEND-local/` excluded in .gitignore and pytest.ini
3. **Frontend dist in tests**: Static mounting is conditional - tests work without built frontend

## Development Workflow

1. **Start Docker stack**: `docker-compose up --build`
2. **Pull Ollama model**: `docker-compose exec ollama ollama pull qwen2.5-coder:7b`
3. **Paste Funda data**: Copy HTML source (Ctrl-A from browser source view)
4. **Optional**: Paste images from clipboard (Cmd+V in textarea)
5. **Generate report**: Click "Start Analyse", wait for polling to complete (<60s)
6. **Run tests**: `pytest tests/` (backend), `npm test` (frontend)
7. **Commit changes**: Include tests for new features

## Performance Targets

- Full report generation: <60 seconds (not 26 minutes!)
- Status polling interval: 2 seconds
- Ollama per-chapter timeout: 30 seconds
- Image upload max size: 10MB
