# backend/main.py (New Version)
from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from scraper import Scraper
from parser import Parser
from chapters.registry import get_chapter_class
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
DB_PATH = os.environ.get("APP_DB", "/data/app.db")
if DB_PATH.startswith("/data") and not os.path.exists("/data"):
    DB_PATH = "local_app.db"

StepState = Literal["queued","running","done","failed"]

STEPS = [
    ("scrape_funda", "Scrape Funda"),
    ("fetch_external_sources", "Bronnen ophalen"),
    ("compute_kpis", "KPI’s berekenen"),
    ("generate_chapters", "Hoofdstukken genereren"),
    ("render_pdf", "PDF renderen"),
]

# Explicitly include 0
CHAPTER_TITLES = {
  0: "Executive Summary",
  1: "Algemene woningkenmerken",
  2: "Persoonlijke eisen & matchanalyse",
  3: "Waarde-inschatting & afwijkingsanalyse",
  4: "Tijdsduur op de markt & prijsgedrag",
  5: "Onderhandelingspunten & strategie",
  6: "Kosten & Total Cost of Ownership (TCO)",
  7: "Omgevingsanalyse",
  8: "Eindbeoordeling & advies",
  9: "Bodstrategie & haalbaarheid",
  10:"KPI-samenvatting & benchmark",
  11:"Renovatie- & aanpassingsplan",
  12:"Marktgevoel & aanvullend perspectief",
}

# --- DATABASE ---
def db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS runs (
          id TEXT PRIMARY KEY,
          funda_url TEXT,
          funda_html TEXT,
          status TEXT,
          steps_json TEXT,
          property_core_json TEXT,
          chapters_json TEXT,
          kpis_json TEXT,
          sources_json TEXT,
          unknowns_json TEXT,
          artifacts_json TEXT,
          created_at TEXT,
          updated_at TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kv_store (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """)
    con.commit()
    con.close()

def now() -> str:
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"

def default_steps() -> Dict[str, StepState]:
    return {k: "queued" for k,_ in STEPS}

def update_run(run_id: str, **fields):
    con = db()
    cur = con.cursor()
    sets = []
    vals = []
    for k,v in fields.items():
        sets.append(f"{k}=?")
        vals.append(v)
    sets.append("updated_at=?")
    vals.append(now())
    vals.append(run_id)
    cur.execute(f"UPDATE runs SET {', '.join(sets)} WHERE id=?", vals)
    con.commit()
    con.close()

def get_run_row(run_id: str):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM runs WHERE id=?", (run_id,))
    row = cur.fetchone()
    con.close()
    return row

def run_to_overview(row) -> Dict[str, Any]:
    if not row:
        raise HTTPException(404, "run not found")
    return {
        "run_id": row["id"],
        "status": row["status"],
        "steps": json.loads(row["steps_json"]),
        "unknowns": json.loads(row["unknowns_json"]),
        "artifacts": json.loads(row["artifacts_json"]),
        "updated_at": row["updated_at"],
    }

# --- MODELS ---
class RunInput(BaseModel):
    funda_url: str
    funda_html: Optional[str] = None

class PasteIn(BaseModel):
    funda_html: str
    extra_facts: Optional[str] = None

# --- FASTAPI APP ---
app = FastAPI(title="AI Woning Rapport (Local) v2")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def root():
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/preferences", response_class=HTMLResponse)
def preferences_page():
    with open(os.path.join(static_dir, "preferences.html"), "r", encoding="utf-8") as f:
        return f.read()

# --- PREFERENCES ---
def get_kv(key: str, default: Any = None) -> Any:
    con = db()
    cur = con.cursor()
    cur.execute("SELECT value FROM kv_store WHERE key=?", (key,))
    row = cur.fetchone()
    con.close()
    if row:
        return json.loads(row["value"])
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

# --- CORE LOGIC ---

def derive_property_core(funda_url: str) -> Dict[str, Any]:
    try:
        scraper = Scraper()
        html = scraper.fetch_page(funda_url)
        parser = Parser()
        data = parser.parse_html(html)
        data["funda_url"] = funda_url
        return data
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        # Return minimal core data with default values
        return {
            "address": "Onbekend (handmatig te vullen)",
            "funda_url": funda_url,
            "scrape_error": str(e)
        }
def build_chapters(property_core: Dict[str, Any]) -> Dict[str, Any]:
    chapters = {}
    logger.info(f"Building chapters for property: {property_core.get('address')}")
    # Iterate through ALL chapters 0-12 defined in the registry
    for i in range(13):
        cls = get_chapter_class(i)
        if cls:
            try:
                instance = cls(property_core)
                output = instance.generate()
                # Ensure modern layout compliance for each chapter
                if isinstance(output.grid_layout, dict):
                    layout = output.grid_layout
                    layout.setdefault("layout_type", "modern_dashboard")
                    layout.setdefault("metrics", [{"id": "default_metric", "label": "Info", "value": "N/A", "icon": "info"}])
                    layout.setdefault("main", {"title": "Overview", "content": "No detailed content provided."})
                    layout.setdefault("sidebar", [{"type": "advisor_card", "title": "Tip", "content": "No advice available."}])
                    output.grid_layout = layout
                chapters[str(i)] = output.dict()
                logger.debug(f" - Generated Chapter {i}: {output.title}")
            except Exception as e:
                logger.error(f"Error generating chapter {i}: {e}")
                chapters[str(i)] = {
                    "title": CHAPTER_TITLES.get(i, f"Hoofdstuk {i}"),
                    "blocks": [{
                        "type": "compliance",
                        "level": "error",
                        "message": f"Kon hoofdstuk {i} niet genereren: {e}",
                        "details": "Controleer de ingevoerde gegevens of probeer het later opnieuw."
                    }]
                }
        else:
            logger.warning(f"Warning: No class found for Chapter {i}")
            chapters[str(i)] = {
                "title": CHAPTER_TITLES.get(i, f"Hoofdstuk {i}"),
                "blocks": [{
                    "type": "compliance",
                    "level": "warning",
                    "message": f"Hoofdstuk {i} is nog niet beschikbaar.",
                    "details": "Dit hoofdstuk wordt in een toekomstige update toegevoegd."
                }]
            }
    return chapters
def build_kpis(property_core: Dict[str, Any]) -> Dict[str, Any]:
    fields = ["asking_price_eur", "living_area_m2", "plot_area_m2", "build_year", "energy_label"]
    present = sum(1 for f in fields if property_core.get(f))
    completeness = round(present / len(fields), 2)
    
    # Fit Score
    fit_score = 0.50
    if completeness > 0.8: fit_score += 0.20
    elif completeness > 0.5: fit_score += 0.10
    label = (property_core.get("energy_label") or "").upper()
    if label.startswith("A"): fit_score += 0.15
    elif label == "B": fit_score += 0.10
    
    # Value Trend
    value_text = "€ TBD"
    value_trend = "neutral"
    price = property_core.get("asking_price_eur")
    area = property_core.get("living_area_m2")
    
    if price and area:
        try:
            p_val = int("".join(filter(str.isdigit, str(price))))
            a_val = int("".join(filter(str.isdigit, str(area))))
            if a_val > 0:
                sqm_price = p_val / a_val
                if sqm_price < 4500: value_trend = "up"
                elif sqm_price > 6000: value_trend = "down"
                value_text = f"€ {int(sqm_price)}/m²"
        except: pass
        
    dashboard_cards = [
        {"id": "fit", "title": "Match Score", "value": f"{int(fit_score*100)}%", "trend": "neutral", "desc": "Gebaseerd op jouw eisenprofiel"},
        {"id": "completeness", "title": "Data Kwaliteit", "value": f"{int(completeness*100)}%", "trend": "up" if completeness > 0.8 else "neutral", "desc": "Beschikbare kerngegevens"},
        {"id": "value", "title": "Waarde Indicatie", "value": value_text, "trend": value_trend, "desc": "Schatting o.b.v. m² prijs"},
        {"id": "energy", "title": "Duurzaamheid", "value": property_core.get("energy_label") or "?", "trend": "up" if "A" in label else "neutral", "desc": "Energielabel"}
    ]
    
    advisor_feedback = []
    if completeness < 0.6:
        advisor_feedback.append({"type": "warning", "title": "Beperkte Data", "message": "Er ontbreken essentiële gegevens. Plak de HTML."})
    else:
        advisor_feedback.append({"type": "success", "title": "Goede Basis", "message": "We hebben voldoende data."})
        
    return {"dashboard_cards": dashboard_cards, "advisor_feedback": advisor_feedback}

def build_unknowns(property_core: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Simplified logic for unknowns reuse
    unknowns = []
    if not property_core.get("asking_price_eur"):
        unknowns.append({"chapter": 1, "topic": "Vraagprijs", "severity": "high", "action": "Invullen", "reason": "Missing"})
    return unknowns

def chapter_overview(chapters: Dict[str, Any], sources: List[Any], kpis: Dict[str,Any], unknowns: List[Any]) -> List[Dict[str,Any]]:
    src_count = {} # simplified
    out = []
    
    # CRITICAL: Loop from 0 to 12 inclusive
    for i in range(0, 13):
        cid = str(i)
        
        # Use generated title if available, else static map
        if cid in chapters and chapters[cid].get("title"):
             title = chapters[cid]["title"]
        else:
             title = CHAPTER_TITLES.get(i, f"Hoofdstuk {i}")
             
        comp = "compleet" if cid in chapters else "onbekend"
        
        out.append({
            "id": i,
            "title": title,
            "completeness": comp,
            "kpiCount": 0,
            "sourceCount": 0,
        })
    return out

def simulate_pipeline(run_id: str):
    row = get_run_row(run_id)
    if not row: return
    
    funda_url = row["funda_url"]
    steps = json.loads(row["steps_json"])
    update_run(run_id, status="running")
    
    # 1. Scrape
    steps["scrape_funda"] = "running"; update_run(run_id, steps_json=json.dumps(steps))
    core = derive_property_core(funda_url)
    
    # Merge pasted
    if row["funda_html"]:
        try:
             p = Parser().parse_html(row["funda_html"])
             core.update({k:v for k,v in p.items() if v})
        except: pass
        
    steps["scrape_funda"] = "done"; update_run(run_id, steps_json=json.dumps(steps), property_core_json=json.dumps(core))
    
    # 2. Others (Fast)
    steps["fetch_external_sources"] = "done"
    
    # 3. KPIs
    steps["compute_kpis"] = "done"
    kpis = build_kpis(core)
    update_run(run_id, kpis_json=json.dumps(kpis))
    
    # 4. Chapters
    steps["generate_chapters"] = "running"; update_run(run_id, steps_json=json.dumps(steps))
    
    logger.info(f"Pipeline: generating chapters for run {run_id}...")
    chapters = build_chapters(core)
    unknowns = build_unknowns(core)
    
    # Verifying Chapter 0
    if "0" not in chapters:
        logger.critical("CRITICAL WARNING: Chapter 0 was not generated in pipeline!")
    else:
        logger.info("Pipeline: Chapter 0 generated successfully.")
        
    steps["generate_chapters"] = "done"
    update_run(run_id, steps_json=json.dumps(steps), chapters_json=json.dumps(chapters), unknowns_json=json.dumps(unknowns), status="done")


# --- API ROUTES ---

@app.post("/runs")
def create_run(inp: RunInput):
    run_id = str(uuid.uuid4())
    con = db()
    cur = con.cursor()
    created = now()
    cur.execute(
        "INSERT INTO runs (id,funda_url,funda_html,status,steps_json,property_core_json,chapters_json,kpis_json,sources_json,unknowns_json,artifacts_json,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (run_id, str(inp.funda_url), inp.funda_html, "queued", json.dumps(default_steps()), "{}", "{}", "{}", "[]", "[]", "{}", created, created)
    )
    con.commit()
    con.close()
    return {"run_id": run_id, "status": "queued"}

@app.post("/runs/{run_id}/start")
def start_run(run_id: str):
    # Synchronous for local
    simulate_pipeline(run_id)
    return {"ok": True}

@app.get("/runs/{run_id}/report")
def get_report(run_id: str):
    row = get_run_row(run_id)
    if not row: raise HTTPException(404)
    
    chapters = json.loads(row["chapters_json"] or "{}")
    core = json.loads(row["property_core_json"] or "{}")
    kpis = json.loads(row["kpis_json"] or "{}")
    unknowns = json.loads(row["unknowns_json"] or "[]")
    
    # AUTO-FIX: If we have core data but no chapters (or missing 0), force regen
    if (not chapters or "0" not in chapters) and core:
        logger.info(f"Auto-Regen triggered for run {run_id}")
        chapters = build_chapters(core)
        kpis = build_kpis(core)
        update_run(run_id, chapters_json=json.dumps(chapters), kpis_json=json.dumps(kpis))
    
    overview = chapter_overview(chapters, [], kpis, unknowns)
    
    return {
        "run_id": run_id,
        "property_core": core,
        "chapters": chapters,
        "kpis": kpis,
        "overview": overview
    }

@app.post("/runs/{run_id}/paste")
def paste_content(run_id: str, inp: PasteIn):
    row = get_run_row(run_id)
    if not row: raise HTTPException(404)
    
    core = json.loads(row["property_core_json"] or "{}")
    if inp.funda_html:
        try:
             core.update(Parser().parse_html(inp.funda_html))
        except: pass
    
    # Always regen after paste
    new_chapters = build_chapters(core)
    new_kpis = build_kpis(core)
    unknowns = build_unknowns(core)
    
    update_run(run_id, property_core_json=json.dumps(core), chapters_json=json.dumps(new_chapters), kpis_json=json.dumps(new_kpis), unknowns_json=json.dumps(unknowns))

    # Return structure matching get_report() because frontend expects it immediately
    overview = chapter_overview(new_chapters, [], new_kpis, unknowns)
    
    return {
        "ok": True,
        "run_id": run_id,
        "property_core": core,
        "chapters": new_chapters,
        "kpis": new_kpis,
        "overview": overview
    }

# --- PDF Generation (Simplified) ---
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except:
    WEASYPRINT_AVAILABLE = False

@app.get("/runs/{run_id}/pdf")
def generate_pdf(run_id: str):
    if not WEASYPRINT_AVAILABLE: raise HTTPException(501, "PDF tools missing")
    row = get_run_row(run_id)
    chapters = json.loads(row["chapters_json"] or "{}")
    core = json.loads(row["property_core_json"] or "{}")
    
    md = f"# Rapport {core.get('address')}\n\n"
    for i in range(13):
        if str(i) in chapters:
            md += f"## {chapters[str(i)]['title']}\n\n"
            # Extract text from blocks
            for b in chapters[str(i)].get("blocks", []):
                md += b["data"]["text"] + "\n\n"
            md += "\\pagebreak\n"
            
    import markdown
    html = markdown.markdown(md)
    pdf = HTML(string=html).write_pdf()
    return StreamingResponse(iter([pdf]), media_type="application/pdf")
