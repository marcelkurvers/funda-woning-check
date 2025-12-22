# Docker Deployment

This directory contains Docker Compose configurations for deploying AI Woning Rapport.

## Available Configurations

### 🖥️ Local Development
**File:** `docker-compose.yml`

For local development on Mac/Windows/Linux:

```bash
# From project root
docker compose -f docker/docker-compose.yml up --build
```

Access at: http://localhost:8000

---

### 🏠 Synology NAS
**File:** `docker-compose.synology.yml`

Production-ready configuration for Synology NAS with Container Manager:

```bash
# SSH into your Synology NAS
cd /volume1/docker/funda-app

# Configure environment
cp docker/.env.synology .env
nano .env  # Add your API keys

# Deploy
docker compose -f docker/docker-compose.synology.yml up -d
```

**See:** [`docs/SYNOLOGY_DEPLOYMENT.md`](../docs/SYNOLOGY_DEPLOYMENT.md) for detailed instructions

---

## Environment Configuration

### Local Development
Copy `.env.example` (from project root) to `.env`

### Synology NAS
Copy `docker/.env.synology` to `.env` and configure:
- API keys (OpenAI, Anthropic, Gemini)
- Ports (if needed)
- Data paths (Synology shared folders)

---

## Quick Reference

| Configuration | File | Use Case |
|--------------|------|----------|
| Development | `docker-compose.yml` | Local Mac/Windows/Linux |
| Synology NAS | `docker-compose.synology.yml` | Production on NAS |

---

## Services

Both configurations include:
- **app** - FastAPI backend + React frontend
- **ollama** - Local LLM server (optional, can use external AI providers)

---

## Documentation

- **Synology Deployment**: [`docs/SYNOLOGY_DEPLOYMENT.md`](../docs/SYNOLOGY_DEPLOYMENT.md)
- **Architecture**: [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
- **Configuration**: [`docs/CONFIGURATION.md`](../docs/CONFIGURATION.md)
