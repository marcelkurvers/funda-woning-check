# HANDOVER – AI Woning Rapport (Local Web App) v2
Datum: 2025-12-14

## 1. Doel en scope
Deze codebase levert een **werkende local webapp** (single-user) die een woningrapport in de **browser** toont.

Belangrijkste flow:
- **POST /runs** → nieuwe `run_id` → **clean sheet**.
- Pipeline **test** Funda scraping (verwacht: geblokkeerd).
- Bij fail: **automatic fallback** naar **copy‑paste input** (`POST /runs/{id}/paste`).
- Verrijking met **openbare bronnen** (best-effort):
  - OpenStreetMap **Nominatim** (geocoding)
  - **OSRM** public routing (auto reistijd, best-effort)
- Live voortgang via **SSE** (`/runs/{id}/events`) + polling fallback.
- Rapportoverzicht vóór download: H1–H12, unknowns, sources.

Niet geïmplementeerd in v2:
- Volledige hoofdstukinhoud H1–H12 conform jouw uitgebreide templates (H1–H3 zijn deels gevuld; rest placeholders).
- PDF + signed URL download (UI aanwezig maar uitgeschakeld).
- Officiële WOZ/BAG/Kadaster connectors (nog niet gekoppeld).
- OV/e-bike reistijden (alleen auto via OSRM).

## 2. Repo structuur
- `docker-compose.yml` – 1 command runtime
- `backend/` – FastAPI app + pipeline + parsing + generators
- `backend/static/` – UI (HTML/CSS/JS) zonder build toolchain

## 3. API contract (current)
### Create run
`POST /runs` → `{"run_id":"uuid"}`

### Start pipeline
`POST /runs/{run_id}/start`  
- Start background pipeline thread.

### Paste input (primary path)
`POST /runs/{run_id}/paste`
Body:
```json
{"funda_html_or_text":"...","extra_facts":"optional"}
```

### Status
`GET /runs/{run_id}`  
- status: `queued|running|waiting_input|done|failed`
- steps: per stap `queued|running|done|failed|needs_input`

### SSE
`GET /runs/{run_id}/events`  
- UI ontvangt live updates.

### Report payload
`GET /runs/{run_id}/report`  
- overview (H1–H12)
- chapters (blocks)
- unknowns, sources, kpis

## 4. State machine
Stappen (pipeline.py):
1) scrape_funda (test)  
2) wait_for_paste (needs_input bij fail)  
3) parse_input  
4) fetch_public_sources  
5) compute_kpis  
6) generate_chapters  
7) render_pdf (no-op; stap “done”)

## 5. Public sources (best-effort)
- Nominatim: geocode op basis van `address_guess`
- OSRM: auto reistijd naar Eindhoven centrum (indicatief)

## 6. Starten (developer)
```bash
docker compose up --build
```
Open: http://localhost:8000

## 7. Known issues / limitations
- Regex parsing is beperkt; kwaliteit hangt af van pasted input.
- OSRM/Nominatim kunnen rate limits hebben; errors worden gemarkeerd als “onbekend / nader te onderzoeken”.
- Geen testsuite (nog).

## 8. Next dev actions (concreet)
1) **Parsing uitbreiden** (bouwjaar, type, kamers, staat, etc.) + unit tests.
2) **BAG (PDOK)** connector (adresvalidatie/objectkenmerken).
3) **CBS wijk/buurt** data voor omgeving.
4) H2 eisen-invoer (Marcel/Petra) als JSON-form.
5) Hoofdstukken vullen conform jouw templates (de txt/docx specs) en bronnen per hoofdstuk.
6) PDF engine + signed URL (optioneel).

## 9. Checksums (integrity)


