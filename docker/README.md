# Docker Deployment

This directory contains Docker Compose configurations for deploying AI Woning Rapport.

## Available Configurations

### 🖥️ Local Development
**File:** `docker-compose.yml`

For local development on Mac/Windows/Linux with local build:

```bash
# From project root
docker compose -f docker/docker-compose.yml up --build
```

Access at: http://localhost:8000

---

### 🏠 Synology NAS (Pre-built Image - Recommended)
**File:** `docker-compose.synology.yml`

Production-ready configuration using **pre-built image from GitHub Container Registry**:

```bash
# SSH into your Synology NAS
cd /volume1/docker/funda-app

# Configure environment
cp docker/.env.synology .env
nano .env  # Add your API keys

# Deploy (downloads pre-built image)
docker compose -f docker/docker-compose.synology.yml up -d
```

**Benefits:**
- ✅ Fast deployment (no build time)
- ✅ Multi-architecture support (amd64/arm64)
- ✅ Automatically updated with each release
- ✅ No build dependencies needed

---

### 🔧 Local Build Version
**File:** `docker-compose.build.yml`

For users who want to build from source:

```bash
# Use this if you want to build locally instead of downloading
docker compose -f docker/docker-compose.build.yml up -d --build
```

**When to use:**
- You've modified the source code
- You want to verify the build process
- GHCR is unavailable in your region


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
