# backend/main.py (New Version)
from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
import re
import logging
from typing import Any, Dict, List, Literal, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

from fastapi import FastAPI, HTTPException, UploadFile, File, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from scraper import Scraper
from parser import Parser
from consistency import ConsistencyChecker
from chapters.registry import get_chapter_class
from intelligence import IntelligenceEngine
from ai.provider_factory import ProviderFactory
from config.settings import get_settings, reset_settings, AppSettings
from jinja2 import Environment, FileSystemLoader
try:
    from weasyprint import HTML
except (ImportError, OSError):
    HTML = None

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get settings singleton
settings = get_settings()

# --- CONFIGURATION ---
BACKEND_DIR = Path(__file__).parent
BASE_DIR = BACKEND_DIR.parent # Project root

# Data paths (stay in project root or as specified by env)
DEFAULT_DB_PATH = BASE_DIR / "data" / "local_app.db"
DB_PATH = Path(os.environ.get("APP_DB", str(DEFAULT_DB_PATH)))
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Ensure DB directory exists
if not DB_PATH.parent.exists():
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create DB directory: {e}")

CHAPTER_TITLES = settings.chapters.titles

STEPS = (
    "scrape_funda",           # Chapter 0, Chapter 1
    "fetch_external_sources",  # Kadaster, bag, mapit
    "compute_kpis",           # Calculations
    "generate_chapters",      # Intelligence Engine
    "render_pdf"              # Template & PDF
)

# --- DATABASE ---
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    con = db()
    cur = con.cursor()
    # Runs table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            funda_url TEXT,
            funda_html TEXT,
            status TEXT, -- queued, running, done, error
            steps_json TEXT,
            property_core_json TEXT, -- All relevant raw fields from scraper
            chapters_json TEXT,      -- Final generated contents
            kpis_json TEXT,          -- Computed KPIs
            sources_json TEXT,       -- Info about used external sources
            unknowns_json TEXT,      -- Missing data fields
            artifacts_json TEXT,     -- references to PDF path, etc.
            created_at TEXT,
            updated_at TEXT
        )
    """)
    # KV Store for preferences and configuration
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kv_store (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    con.commit()
    con.close()

def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def default_steps():
    return {s: "pending" for s in STEPS}

def update_run(run_id, **kwargs):
    con = db()
    cur = con.cursor()
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(now())
    values.append(run_id)
    cur.execute(f"UPDATE runs SET {', '.join(fields)}, updated_at = ? WHERE id = ?", tuple(values))
    con.commit()
    con.close()

def get_run_row(run_id):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM runs WHERE id=?", (run_id,))
    row = cur.fetchone()
    con.close()
    return row

def run_to_overview(row) -> Dict[str, Any]:
    if not row:
        raise HTTPException(404, "run not found")
    steps = json.loads(row["steps_json"]) if row["steps_json"] else {}
    # Calculate progress %
    total = len(steps)
    done = sum(1 for s in steps.values() if s == "done")
    percent = int((done / total) * 100) if total > 0 else 0
    
    return {
        "run_id": row["id"],
        "status": row["status"],
        "steps": steps,
        "progress": {
            "current": done,
            "total": total,
            "percent": percent
        },
        "unknowns": json.loads(row["unknowns_json"]) if row["unknowns_json"] else [],
        "artifacts": json.loads(row["artifacts_json"]) if row["artifacts_json"] else [],
        "updated_at": row["updated_at"],
    }

# --- AI INITIALIZATION ---
def init_ai_provider():
    """Initialize AI Provider based on current settings."""
    global settings
    settings = get_settings() # Refresh settings from DB if needed
    
    from ai.provider_factory import register_providers
    register_providers()
    provider_name = settings.ai.provider
    try:
        logger.info(f"Setting up AI Provider: {provider_name}")
        api_key = None
        base_url = None
        
        if provider_name == 'openai':
            api_key = settings.ai.openai_api_key or os.environ.get("OPENAI_API_KEY")
        elif provider_name == 'anthropic':
            api_key = settings.ai.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        elif provider_name == 'gemini':
            api_key = settings.ai.gemini_api_key or os.environ.get("GEMINI_API_KEY")
        elif provider_name == 'ollama':
            base_url = settings.ai.ollama_base_url
            
        provider = ProviderFactory.create_provider(
            provider_name,
            api_key=api_key,
            base_url=base_url,
            timeout=settings.ai.timeout
        )
        IntelligenceEngine.set_provider(provider)
        logger.info(f"✓ AI Provider initialized: {provider_name}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to initialize AI Provider ({provider_name}): {e}")
        return False

# --- MODELS ---
class RunInput(BaseModel):
    funda_url: str
    funda_html: Optional[str] = None
    media_urls: Optional[List[str]] = []
    extra_facts: Optional[str] = None

class PasteIn(BaseModel):
    funda_html: str
    extra_facts: Optional[str] = None
    media_urls: Optional[List[str]] = []

# --- FASTAPI APP ---
app = FastAPI(title="AI Woning Rapport Pro v4")
init_db()

# Background task executor
executor = ThreadPoolExecutor(max_workers=settings.pipeline.max_workers)

# Determine static directory
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "frontend", "dist")

if not os.path.exists(static_dir):
    static_dir = "/app/frontend/dist"
    if not os.path.exists(static_dir):
        static_dir = os.path.join(os.path.dirname(base_dir), "frontend", "dist")

# Mount static files
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

    @app.get("/", response_class=HTMLResponse)
    def root():
        with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
            return f.read()

    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
else:
    @app.get("/", response_class=HTMLResponse)
    def root():
        return "<html><body>Development Mode - Static assets not found.</body></html>"

if UPLOAD_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

@app.on_event("startup")
def _startup():
    init_db()
    init_ai_provider()

# Include configuration router
from api import config as config_router
app.include_router(config_router.router)

# --- PIPELINE ---
def simulate_pipeline(run_id):
    logger.info(f"Pipeline: Starting run {run_id}")
    # Refresh AI at start of pipeline to ensure latest settings are used
    init_ai_provider()
    
    row = get_run_row(run_id)
    if not row: return
    
    steps = json.loads(row["steps_json"]) if row["steps_json"] else {}
    core = json.loads(row["property_core_json"]) if row["property_core_json"] else {}
    funda_url = row["funda_url"]
    
    # 1. Scrape / Parse
    steps["scrape_funda"] = "running"
    update_run(run_id, steps_json=json.dumps(steps))
    
    if funda_url and "manual-paste" not in funda_url:
        try:
            scraper = Scraper()
            scraped = scraper.derive_property_core(funda_url)
            core.update({k: v for k, v in scraped.items() if v})
        except Exception as e:
            logger.error(f"Scrape failed: {e}")
            core["scrape_error"] = str(e)
            
    if row["funda_html"]:
        try:
            p = Parser().parse_html(row["funda_html"])
            # Merge missing fields, but keep media_urls from the paste if present
            incoming_media = p.get("media_urls", [])
            initial_media = core.get("media_urls", [])
            
            core.update({k: v for k, v in p.items() if v})
            
            # Smart merge media: prioritize user-uploaded if present
            core["media_urls"] = list(dict.fromkeys(initial_media + incoming_media))
        except Exception as e:
            logger.error(f"Parse failed: {e}")
            
    steps["scrape_funda"] = "done"
    update_run(run_id, steps_json=json.dumps(steps), property_core_json=json.dumps(core))
    
    # 2. KPIs
    steps["compute_kpis"] = "done"
    kpis = build_kpis(core)
    update_run(run_id, kpis_json=json.dumps(kpis))
    
    # 3. Chapters
    steps["generate_chapters"] = "running"
    update_run(run_id, steps_json=json.dumps(steps))
    
    chapters = build_chapters(core)
    unknowns = build_unknowns(core)
    
    steps["generate_chapters"] = "done"
    update_run(run_id, steps_json=json.dumps(steps), chapters_json=json.dumps(chapters), unknowns_json=json.dumps(unknowns), status="done")

def build_chapters(core: Dict[str, Any]) -> Dict[str, Any]:
    chapters = {}
    
    # Check current preferences from KV store
    prefs = get_kv("preferences", {})
    # Inject current AI model into prefs for IntelligenceEngine
    prefs['ai_model'] = settings.ai.model
    core['_preferences'] = prefs
    
    for i in range(13):
        # 1. Try Rich Chapter Generation via Chapter Classes
        cls = get_chapter_class(i)
        if cls:
            try:
                obj = cls(core)
                output = obj.generate()
                # Bridge: Ensure Chapter 0 contains property_core and metrics for frontend dashboard
                if i == 0:
                    if output.chapter_data is None: output.chapter_data = {}
                    output.chapter_data["property_core"] = core
                    # Bridge metrics for dashboard
                    if output.grid_layout and isinstance(output.grid_layout, dict):
                         output.chapter_data["metrics"] = output.grid_layout.get("metrics", [])
                
                output.id = str(i)
                data_dict = output.dict()
                # Bridge: make sure chapter_data has metrics/sidebar for frontend
                if data_dict["chapter_data"] is None: data_dict["chapter_data"] = {}
                if data_dict["grid_layout"] and isinstance(data_dict["grid_layout"], dict):
                    data_dict["chapter_data"]["metrics"] = data_dict["grid_layout"].get("metrics", [])
                    data_dict["chapter_data"]["sidebar_items"] = data_dict["grid_layout"].get("sidebar", [])
                
                chapters[str(i)] = data_dict
                logger.debug(f" - Generated Rich Chapter {i}")
                continue
            except Exception as e:
                logger.error(f"Failed to generate Rich Chapter {i}: {e}")

        # 2. Fallback: Direct IntelligenceEngine call
        output = IntelligenceEngine.generate_chapter_narrative(i, core)
        chapter_id = str(i)
        title = output.get("title", CHAPTER_TITLES.get(str(i), f"Hoofdstuk {i}"))
        
        # Ensure chapter_data has required fields for frontend bridging test
        output["sidebar_items"] = output.get("sidebar_items", [])
        output["metrics"] = output.get("metrics", [])
        
        # Construct a backward-compatible dictionary matching ChapterOutput structure
        chapters[chapter_id] = {
            "id": chapter_id,
            "title": title,
            "grid_layout": {
                "main": {"title": title, "content": output.get("main_analysis")},
                "metrics": [{"id": "fallback", "label": "Status", "value": "AI Generated"}]
            },
            "blocks": [],
            "chapter_data": output,
            "property_core": output.get("property_core") if i == 0 else None
        }
    return chapters

def build_kpis(core: Dict[str, Any]) -> Dict[str, Any]:
    fields = ["asking_price_eur", "living_area_m2", "plot_area_m2", "build_year", "energy_label"]
    present = sum(1 for f in fields if core.get(f))
    completeness = round(present / len(fields), 2)
    
    # Basic Score Logic
    fit_score = 0.75
    value_text = core.get("asking_price_eur", "€ N/B")
    
    cards = [
        {"id": "fit", "title": "Match Score", "value": f"{int(fit_score*100)}%", "trend": "neutral", "desc": "Match Marcel & Petra"},
        {"id": "completeness", "title": "Data Kwaliteit", "value": f"{int(completeness*100)}%", "trend": "up" if completeness > 0.8 else "neutral", "desc": "Extrahering"},
        {"id": "value", "title": "Vraagprijs", "value": value_text, "trend": "neutral", "desc": "Per direct"},
        {"id": "energy", "title": "Energielabel", "value": core.get("energy_label") or "?", "trend": "neutral", "desc": "Duurzaamheid"}
    ]
    
    return {
        "dashboard_cards": cards,
        "completeness": completeness,
        "fit_score": fit_score
    }

def build_unknowns(core: Dict[str, Any]) -> List[str]:
    fields = ["asking_price_eur", "living_area_m2", "plot_area_m2", "build_year", "energy_label", "rooms", "bedrooms"]
    return [f for f in fields if not core.get(f)]

# --- API ROUTES ---
@app.get("/runs")
def list_runs():
    con = db()
    cur = con.cursor()
    cur.execute("SELECT id, funda_url, status, created_at FROM runs ORDER BY created_at DESC")
    rows = cur.fetchall()
    con.close()
    return [{"id": r[0], "funda_url": r[1], "status": r[2], "created_at": r[3]} for r in rows]

@app.post("/runs")
def create_run(inp: RunInput):
    run_id = str(uuid.uuid4())
    con = db()
    cur = con.cursor()
    funda_url = None if inp.funda_url.lower() in ["manual-paste", ""] else inp.funda_url
    core_data = {
        "media_urls": inp.media_urls or [],
        "extra_facts": inp.extra_facts or ""
    }
    cur.execute(
        "INSERT INTO runs (id, funda_url, funda_html, status, steps_json, property_core_json, chapters_json, kpis_json, unknowns_json, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (run_id, funda_url, inp.funda_html, "queued", json.dumps(default_steps()), json.dumps(core_data), "{}", "[]", "[]", now(), now())
    )
    con.commit()
    con.close()
    return {"run_id": run_id, "status": "queued"}

@app.post("/runs/{run_id}/start")
def start_run(run_id: str):
    executor.submit(simulate_pipeline, run_id)
    return {"ok": True, "status": "processing"}

@app.post("/runs/{run_id}/paste")
def paste_funda_html(run_id: str, inp: Dict[str, Any]):
    html = inp.get("funda_html")
    if not html: raise HTTPException(400, "funda_html required")
    row = get_run_row(run_id)
    if not row: raise HTTPException(404)
    
    # Update DB
    update_run(run_id, funda_html=html)
    
    # Immediately parse and update core data so frontend/tests see it
    try:
        p = Parser().parse_html(html)
        core = json.loads(row["property_core_json"]) if row["property_core_json"] else {}
        core.update({k: v for k, v in p.items() if v})
        update_run(run_id, property_core_json=json.dumps(core))
    except Exception as e:
        logger.error(f"Paste-parse failed: {e}")
        
    return {"ok": True}

@app.get("/runs/{run_id}/status")
def get_run_status(run_id: str):
    row = get_run_row(run_id)
    if not row: raise HTTPException(404)
    return run_to_overview(row)

@app.get("/runs/{run_id}/report")
def get_run_report(run_id: str):
    row = get_run_row(run_id)
    if not row: raise HTTPException(404)
    return {
        "runId": row["id"],
        "address": (json.loads(row["property_core_json"]) if row["property_core_json"] else {}).get("address", "Onbekend"),
        "property_core": json.loads(row["property_core_json"]) if row["property_core_json"] else {},
        "chapters": json.loads(row["chapters_json"]) if row["chapters_json"] else {},
        "kpis": json.loads(row["kpis_json"]) if row["kpis_json"] else {}
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "backend": "ok", "db": "ok"}

@app.post("/api/upload/image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    content = await file.read()
    
    # Try to preserve extension
    ext = ".png"
    if file.filename:
        _, original_ext = os.path.splitext(file.filename)
        if original_ext.lower() in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
            ext = original_ext.lower()
            
    filename = f"{uuid.uuid4()}{ext}"
    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as f:
        f.write(content)
    return {"ok": True, "url": f"/uploads/{filename}", "size": len(content)}

def get_kv(key: str, default: Any = None) -> Any:
    con = db()
    cur = con.cursor()
    cur.execute("SELECT value FROM kv_store WHERE key=?", (key,))
    row = cur.fetchone()
    con.close()
    if row: return json.loads(row[0])
    return default

def set_kv(key: str, value: Any):
    con = db()
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    con.commit()
    con.close()

@app.get("/api/preferences")
def get_preferences():
    return get_kv("preferences", {})

@app.post("/api/preferences")
def save_preferences(prefs: Dict[str, Any]):
    set_kv("preferences", prefs)
    return {"ok": True}

@app.get("/api/ai/providers")
def list_providers():
    return ProviderFactory.list_providers()

@app.get("/api/ai/status")
def check_ai_status():
    success = init_ai_provider()
    return {"healthy": success, "provider": settings.ai.provider}

@app.get("/runs/{run_id}/pdf")
async def get_run_pdf(run_id: str):
    if not HTML:
        logger.error("PDF: WeasyPrint not installed.")
        raise HTTPException(500, "PDF generation capability not installed (WeasyPrint missing)")
        
    row = get_run_row(run_id)
    if not row: raise HTTPException(404)
    
    # Prepare data for template
    core = json.loads(row["property_core_json"]) if row["property_core_json"] else {}
    # Backend DB stores chapters as JSON dict. template expects list of objects or dict values.
    # The template uses {% for ch in chapters %}, so we yield values.
    chapters_raw = json.loads(row["chapters_json"]) if row["chapters_json"] else {}
    # Sort by ID as string int
    sorted_keys = sorted(chapters_raw.keys(), key=lambda x: int(x))
    chapters = [chapters_raw[k] for k in sorted_keys]
    
    # Setup Jinja2
    template_dir = BACKEND_DIR / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    try:
        template = env.get_template("report_pdf.html")
    except Exception as e:
        logger.error(f"PDF Template error: {e}")
        raise HTTPException(500, f"Template error: {e}")
    
    # Render HTML
    html_content = template.render(
        property_core=core,
        chapters=chapters,
        date=now(),
        run_id=run_id
    )
    
    # Generate PDF
    try:
        pdf_bytes = HTML(string=html_content, base_url=str(UPLOAD_DIR)).write_pdf()
    except Exception as e:
        logger.error(f"PDF Generation error: {e}")
        raise HTTPException(500, f"PDF engine error: {e}")
        
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Funda_Rapport_{run_id[:8]}.pdf"}
    )
