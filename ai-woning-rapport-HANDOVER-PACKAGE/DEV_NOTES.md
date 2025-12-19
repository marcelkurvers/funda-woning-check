# DEV_NOTES

## Extend parsing
- `backend/parsers.py` gebruikt regex + simpele HTML strip.
- Voeg extractors toe en schrijf unit tests (aan te maken).

## Add sources
- `backend/sources.py`: best-effort calls; errors mogen pipeline niet stoppen.
- Voeg nieuwe sources toe + registreer in `sources_json`.

## Chapter rendering
- Blocks: paragraph / table / callout
- Frontend rendert blocks in `app.js`.

## Production hardening (later)
- Input limits + sanitization
- Auth (indien ooit remote)
- Rate limiting + caching
