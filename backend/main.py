# backend/main.py - Triggering fresh Docker Build
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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys
import asyncio
import concurrent.futures
from pathlib import Path

# Ensure backend directory is in path for internal imports
BACKEND_DIR = Path(__file__).parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from scraper import Scraper
from parser import Parser
from consistency import ConsistencyChecker
from chapters.registry import get_chapter_class
from intelligence import IntelligenceEngine
from ai.provider_factory import ProviderFactory
from ai.dynamic_extractor import DynamicExtractor
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
    "dynamic_extraction",      # AI Attribute Discovery
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
    # Attribute Discovery (Dynamic Interpretation Pipeline)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attribute_discovery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            namespace TEXT, -- e.g., 'financial', 'energy', 'physical'
            key TEXT,
            display_name TEXT,
            value TEXT,
            confidence REAL,
            source_snippet TEXT,
            created_at TEXT,
            FOREIGN KEY (run_id) REFERENCES runs (id)
        )
    """)
    # Media Table (User-Mediated Browser Context)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id TEXT PRIMARY KEY,
            run_id TEXT,
            url TEXT,
            caption TEXT,
            ordering INTEGER,
            provenance TEXT, -- e.g., 'extension', 'paste'
            local_path TEXT,
            created_at TEXT,
            FOREIGN KEY (run_id) REFERENCES runs (id)
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
    
    provider_name = settings.ai.provider
    try:
        logger.info(f"Setting up AI Provider: {provider_name}")
        
        # Prepare configuration from settings
        kwargs = {
            "timeout": settings.ai.timeout,
            "model": settings.ai.model
        }
        
        if provider_name == 'openai':
            kwargs["api_key"] = settings.ai.openai_api_key
        elif provider_name == 'anthropic':
            kwargs["api_key"] = settings.ai.anthropic_api_key
        elif provider_name == 'gemini':
            kwargs["api_key"] = settings.ai.gemini_api_key
        elif provider_name == 'ollama':
            kwargs["base_url"] = settings.ai.ollama_base_url
            
        provider = ProviderFactory.create_provider(provider_name, **kwargs)
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev; can be restricted to extension IDs later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
init_db()

# Background task executor
executor = ThreadPoolExecutor(max_workers=10) # Higher capacity for always-on service

# Determine static directory
base_dir = Path(__file__).resolve().parent
static_dir_options = [
    base_dir / "frontend" / "dist",             # Inside backend/ (Docker/Prod)
    base_dir.parent / "frontend" / "dist",      # Sibling to backend/ (Local dev)
    Path("/app/backend/frontend/dist"),         # Absolute Docker path
    Path("/app/frontend/dist")                  # Alternative Docker path
]

static_dir = next((str(p) for p in static_dir_options if p.exists()), None)
if static_dir:
    logger.info(f"Serving static files from: {static_dir}")
else:
    logger.warning("No static directory found. Frontend will not be served.")

# --- MOUNTS ---
if static_dir:
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

if UPLOAD_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Mount static folder for styles and local assets
static_assets = BACKEND_DIR / "static"
if static_assets.exists():
    app.mount("/static", StaticFiles(directory=str(static_assets)), name="static")

# --- STARTUP ---
@app.on_event("startup")
def _startup():
    init_db()
    init_ai_provider()

@app.on_event("shutdown")
async def _shutdown():
    # Properly close AI Provider shared client (Risk 2 Mitigation)
    from intelligence import IntelligenceEngine
    provider = IntelligenceEngine._provider
    if provider and hasattr(provider, "close"):
        await provider.close()

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
    
    logger.info(f"Pipeline [{run_id}]: Starting. Status: {row['status']}")
    
    steps = json.loads(row["steps_json"]) if row["steps_json"] else {}
    core = json.loads(row["property_core_json"]) if row["property_core_json"] else {}
    funda_url = row["funda_url"]
    
    # 1. Scrape / Parse
    logger.info(f"Pipeline [{run_id}]: Starting Scrape/Parse")
    steps["scrape_funda"] = "running"
    update_run(run_id, steps_json=json.dumps(steps))
    
    if funda_url and "manual-paste" not in funda_url:
        try:
            scraper = Scraper()
            scraped = scraper.derive_property_core(funda_url)
            core.update({k: v for k, v in scraped.items() if v})
        except Exception as e:
            logger.error(f"Pipeline [{run_id}]: Scrape failed: {e}")
            core["scrape_error"] = str(e)
            
    if row["funda_html"]:
        try:
            p = Parser().parse_html(row["funda_html"])
            incoming_media = p.get("media_urls", [])
            # For a truly clean re-scan, we trust the newest data from the parser/extension
            # rather than indefinitely merging old state.
            core.update({k: v for k, v in p.items() if v})
            core["media_urls"] = list(dict.fromkeys(incoming_media))[:50] 
            
            # Sync to media table
            con = db()
            cur = con.cursor()
            for idx, m_url in enumerate(core["media_urls"]):
                cur.execute("SELECT 1 FROM media WHERE run_id = ? AND url = ?", (run_id, m_url))
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO media (id, run_id, url, caption, ordering, provenance, created_at) VALUES (?,?,?,?,?,?,?)",
                        (str(uuid.uuid4()), run_id, m_url, f"Foto {idx+1}", idx, "parser", now())
                    )
            con.commit()
            con.close()
        except Exception as e:
            logger.error(f"Pipeline [{run_id}]: Parse failed: {e}")
            
    steps["scrape_funda"] = "done"
    update_run(run_id, steps_json=json.dumps(steps), property_core_json=json.dumps(core))
    
    # 1b. Dynamic Extraction (if HTML present)
    if row["funda_html"]:
        logger.info(f"Pipeline [{run_id}]: Starting Dynamic Extraction")
        steps["dynamic_extraction"] = "running"
        update_run(run_id, steps_json=json.dumps(steps))
        try:
            # Use safe execution bridge (Risk 1 Mitigation)
            from ai.bridge import safe_execute_async
            safe_execute_async(run_dynamic_extraction(run_id, row["funda_html"]))
            steps["dynamic_extraction"] = "done"
            update_run(run_id, steps_json=json.dumps(steps))
        except Exception as e:
            logger.error(f"Pipeline [{run_id}]: Dynamic Extraction failed: {e}")
            update_run(run_id, status="error", steps_json=json.dumps(steps))
            return # Stop pipeline on failure

    # 2. KPIs
    logger.info(f"Pipeline [{run_id}]: Computing KPIs")
    steps["compute_kpis"] = "running"
    update_run(run_id, steps_json=json.dumps(steps))
    kpis = build_kpis(core)
    steps["compute_kpis"] = "done"
    update_run(run_id, steps_json=json.dumps(steps), kpis_json=json.dumps(kpis))
    
    # 3. Chapters
    logger.info(f"Pipeline [{run_id}]: Generating Chapters")
    steps["generate_chapters"] = "running"
    update_run(run_id, steps_json=json.dumps(steps))
    
    try:
        chapters = build_chapters(core)
        unknowns = build_unknowns(core)
    except Exception as e:
        logger.error(f"Pipeline [{run_id}]: Chapter generation failed: {e}")
        update_run(run_id, status="error", steps_json=json.dumps(steps))
        return # Stop pipeline as requested
    
    steps["generate_chapters"] = "done"
    logger.info(f"Pipeline [{run_id}]: Complete")
    update_run(run_id, steps_json=json.dumps(steps), chapters_json=json.dumps(chapters), unknowns_json=json.dumps(unknowns), status="done")

def build_chapters(core: Dict[str, Any]) -> Dict[str, Any]:
    chapters = {}
    
    # Check current preferences from KV store
    prefs = get_kv("preferences", {})
    # Ensure current AI settings are reflected in prefs for IntelligenceEngine
    if 'ai_model' not in prefs or not prefs['ai_model']:
        prefs['ai_model'] = settings.ai.model
    if 'ai_provider' not in prefs or not prefs['ai_provider']:
        prefs['ai_provider'] = settings.ai.provider
        
    core['_preferences'] = prefs
    
    for i in range(14):
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
        
        # Map provenance from output if available
        prov_dict = output.get('_provenance')
        from domain.models import AIProvenance
        prov = AIProvenance(**prov_dict) if prov_dict else None

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
            "property_core": output.get("property_core") if i == 0 else None,
            "provenance": prov_dict, # Pass raw dict for easier JSON serialization
            "missing_critical_data": output.get('metadata', {}).get('missing_vars', [])
        }
    return chapters

def build_kpis(core: Dict[str, Any]) -> Dict[str, Any]:
    fields = ["asking_price_eur", "living_area_m2", "plot_area_m2", "build_year", "energy_label"]
    present = sum(1 for f in fields if core.get(f))
    completeness = round(present / len(fields), 2)
    
    # Dynamic Score Logic based on preferences
    fit_score = IntelligenceEngine.calculate_fit_score(core)
    value_text = core.get("asking_price_eur", "€ N/B")
    
    cards = [
        {"id": "fit", "title": "Match Score", "value": f"{int(fit_score*100)}%", "trend": "up" if fit_score > 0.6 else "neutral", "desc": "Match Marcel & Petra"},
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
@app.get("/api/runs")
def list_runs():
    con = db()
    cur = con.cursor()
    cur.execute("SELECT id, funda_url, status, created_at FROM runs ORDER BY created_at DESC")
    rows = cur.fetchall()
    con.close()
    return [{"id": r[0], "funda_url": r[1], "status": r[2], "created_at": r[3]} for r in rows]

@app.get("/api/runs/active")
def get_active_run():
    con = db()
    cur = con.cursor()
    # Find the most recent run created in the last 15 minutes that is on the same URL
    cur.execute("SELECT id, funda_url FROM runs WHERE created_at > datetime('now', '-15 minutes') ORDER BY created_at DESC LIMIT 1")
    row = cur.fetchone()
    con.close()
    if row:
        return {"id": row[0], "funda_url": row[1]}
    return None

@app.post("/api/runs")
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

@app.post("/api/runs/{run_id}/start")
def start_run(run_id: str):
    executor.submit(simulate_pipeline, run_id)
    return {"ok": True, "status": "processing"}

@app.post("/api/runs/{run_id}/paste")
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

@app.get("/api/runs/{run_id}/status")
def get_run_status(run_id: str):
    row = get_run_row(run_id)
    if not row: raise HTTPException(404)
    return run_to_overview(row)

@app.get("/api/runs/{run_id}/report")
def get_run_report(run_id: str):
    row = get_run_row(run_id)
    if not row: raise HTTPException(404)
    
    # Fetch Discovery Attributes
    con = db()
    cur = con.cursor()
    cur.execute("SELECT namespace, key, display_name, value, confidence, source_snippet FROM attribute_discovery WHERE run_id = ?", (run_id,))
    discovery = [dict(r) for r in cur.fetchall()]
    
    # Fetch Media
    cur.execute("SELECT url, caption, ordering, provenance FROM media WHERE run_id = ? ORDER BY ordering ASC", (run_id,))
    media = [dict(r) for r in cur.fetchall()]
    con.close()

    return {
        "runId": row["id"],
        "address": (json.loads(row["property_core_json"]) if row["property_core_json"] else {}).get("address", "Onbekend"),
        "property_core": json.loads(row["property_core_json"]) if row["property_core_json"] else {},
        "chapters": json.loads(row["chapters_json"]) if row["chapters_json"] else {},
        "kpis": json.loads(row["kpis_json"]) if row["kpis_json"] else {},
        "discovery": discovery,
        "media_from_db": media
    }

def normalize_funda_url(url: str) -> str:
    """Extracts the base property ID or URL to ensure consistent matching"""
    if not url: return ""
    base = url.split('?')[0].split('#')[0]
    # Extract ID if present (e.g., /43185766/)
    id_match = re.search(r'/(\d{7,10})(/|$)', base)
    if id_match:
        return f"funda-id-{id_match.group(1)}"
    
    # Fallback to suffix removal
    for suffix in ['/fotos/', '/plattegrond/', '/video/', '/kenmerken/', '/omschrijving/', '/overzicht/']:
        if base.endswith(suffix): base = base[:-len(suffix)]
        elif suffix in base: base = base.split(suffix)[0]
    return base.rstrip('/')

@app.post("/api/extension/ingest")
def extension_ingest(data: Dict[str, Any]):
    funda_url = data.get("url")
    if not funda_url: raise HTTPException(400, "URL required")
    
    normalized = normalize_funda_url(funda_url)
    html = data.get("html", "")
    photos = data.get("photos", [])
    
    con = db()
    cur = con.cursor()
    
    # 1. Search for a recent existing run for this property (within last 6 hours)
    # Match by exact URL OR normalized ID
    cur.execute(
        "SELECT id, property_core_json, status, funda_url FROM runs WHERE (funda_url LIKE ? OR funda_url LIKE ?) AND created_at > datetime('now', '-6 hours') ORDER BY created_at DESC",
        (funda_url + '%', '%' + normalized + '%')
    )
    existing_list = cur.fetchall()
    
    # Precise match on normalized ID if it's an ID-based normalization
    existing = None
    if existing_list:
        if normalized.startswith("funda-id-"):
            for row in existing_list:
                if normalized in normalize_funda_url(row["funda_url"]):
                    existing = row
                    break
        else:
            existing = existing_list[0]

    if existing:
        run_id = existing["id"]
        
        if html:
            # 1. FULL RESET (Voll. Analyse Starten)
            logger.info(f"FULL RESET for existing run: {run_id}")
            core_data = {}
            try:
                core_data = Parser().parse_html(html)
            except Exception as e:
                logger.error(f"Reset parse failed: {e}")
            
            if photos:
                core_data["media_urls"] = [p["url"] for p in photos]

            # Wipe related tables completely
            cur.execute("DELETE FROM media WHERE run_id = ?", (run_id,))
            cur.execute("DELETE FROM attribute_discovery WHERE run_id = ?", (run_id,))
            
            # Clear photos from the run object too
            core_data["media_urls"] = []
            
            # Update the run: back to 'queued', clear chapters and KPIs
            cur.execute(
                "UPDATE runs SET status = 'queued', steps_json = ?, property_core_json = ?, chapters_json = '{}', kpis_json = '[]', funda_html = ?, updated_at = ? WHERE id = ?",
                (json.dumps(default_steps()), json.dumps(core_data), html, now(), run_id)
            )
        else:
            # 2. PHOTO ENRICHMENT (Alleen Foto's Inladen)
            core_data = json.loads(existing["property_core_json"]) if existing["property_core_json"] else {}
            logger.info(f"PHOTO OVERWRITE for existing run: {run_id}")
            
            if photos:
                core_data["media_urls"] = [p["url"] for p in photos]
                # Clear existing media in SQL to prevent orphans/duplicates
                cur.execute("DELETE FROM media WHERE run_id = ?", (run_id,))
            
            # Just update property core and timestamp
            cur.execute(
                "UPDATE runs SET property_core_json = ?, updated_at = ? WHERE id = ?",
                (json.dumps(core_data), now(), run_id)
            )
            # Important: return early to prevent the global photos loop from adding duplicates
            con.commit()
            con.close()
            executor.submit(simulate_pipeline, run_id)
            return {"run_id": run_id, "status": "processing"}
    else:
        # 3. Create NEW run
        run_id = str(uuid.uuid4())
        logger.info(f"Creating NEW run for {funda_url}. RunID: {run_id}")
        core_data = {}
        if html:
            try:
                core_data = Parser().parse_html(html)
            except Exception as e:
                logger.error(f"New parse failed: {e}")
        
        if photos:
            core_data["media_urls"] = [p["url"] for p in photos]
            
        cur.execute(
            "INSERT INTO runs (id, funda_url, funda_html, status, steps_json, property_core_json, chapters_json, kpis_json, unknowns_json, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (run_id, funda_url, html, "queued", json.dumps(default_steps()), json.dumps(core_data), "{}", "[]", "[]", now(), now())
        )

    # 2. Add incoming photos to media table
    for p in photos:
        url = p.get("url")
        m_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO media (id, run_id, url, caption, ordering, provenance, created_at) VALUES (?,?,?,?,?,?,?)",
            (m_id, run_id, url, p.get("caption"), p.get("order", 0), "extension", now())
        )
            
    con.commit()
    con.close()
    
    # 3. Always trigger/re-trigger pipeline to refresh analysis with new data
    executor.submit(simulate_pipeline, run_id)
        
    return {"run_id": run_id, "status": "processing"}

async def run_dynamic_extraction(run_id: str, html: str):
    try:
        init_ai_provider()
        provider = IntelligenceEngine._provider
        if not provider: 
            logger.warning("No AI Provider for dynamic extraction")
            return
            
        extractor = DynamicExtractor(provider)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        main = soup.find('main') or soup.find('article') or soup.body or soup
        text = main.get_text(separator="\n")
        
        # 100% Correct async call
        attributes = await extractor.extract_attributes(text)
        
        con = db()
        cur = con.cursor()
        for attr in attributes:
            cur.execute(
                "INSERT INTO attribute_discovery (run_id, namespace, key, display_name, value, confidence, source_snippet, created_at) VALUES (?,?,?,?,?,?,?,?)",
                (run_id, attr["namespace"], attr["key"], attr["display_name"], attr["value"], attr["confidence"], attr["source_snippet"], now())
            )
        con.commit()
        con.close()
    except Exception as e:
        logger.error(f"Background dynamic extraction failed: {e}")
        raise # Propagate to stop pipeline

@app.get("/api/health")
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
    
    # Sync AI selections back to core settings if present
    provider = prefs.get('ai_provider')
    model = prefs.get('ai_model')
    
    if provider or model:
        s = get_settings()
        if provider: s.ai.provider = provider.lower()
        if model: s.ai.model = model
        
        # Persist to DB using the config router's logic helper if available,
        # or just do it directly to kv_store
        from api.config import _persist_section
        _persist_section("ai", s.ai.model_dump())
        reset_settings()
        init_ai_provider()
        
    return {"ok": True}

@app.get("/api/ai/providers")
def list_providers():
    return ProviderFactory.list_providers()

@app.get("/api/ai/models")
def list_models(provider: Optional[str] = None):
    """Returns a flat list of all recommended models across all providers or 
    filters by provider if a query param is provided.
    """
    providers = ProviderFactory.list_providers()
    target_provider = provider or settings.ai.provider
    if target_provider in providers:
        return {"models": providers[target_provider]["models"]}
    
    # If provider unknown but its "all", return everything flat
    if target_provider == "all":
        all_models = []
        for p in providers.values():
            all_models.extend(p["models"])
        return {"models": list(set(all_models))}
        
    # Fallback
    return {"models": ["gpt-4o", "claude-3-5-sonnet-20240620", "gemini-1.5-flash", "llama3"]}

@app.get("/api/ai/status")
def check_ai_status():
    success = init_ai_provider()
    return {"healthy": success, "provider": settings.ai.provider}

@app.get("/api/runs/{run_id}/pdf")
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

# --- SPA CATCH-ALL ---
@app.get("/{full_path:path}", response_class=HTMLResponse)
def catch_all(full_path: str):
    # If it looks like an API call or a static file, we shouldn't handle it here
    if full_path.startswith("api/") or full_path.startswith("static/") or \
       full_path.startswith("assets/") or full_path.startswith("uploads/"):
        raise HTTPException(404)
        
    if os.path.exists(static_dir):
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return f.read()
    
    return "<html><body>Frontend not built or not found.</body></html>"
