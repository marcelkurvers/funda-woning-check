# AI Woning Rapport

[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue?logo=docker)](https://ghcr.io/marcelkurvers/funda-app)
[![Build Status](https://github.com/marcelkurvers/funda-app/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/marcelkurvers/funda-app/actions/workflows/docker-publish.yml)
[![License](https://img.shields.io/badge/license-Private-red)](LICENSE)

A powerful, data-driven real estate analysis tool that transforms Funda listings into comprehensive, personalized property reports.


## 🚀 Overview

The **AI Woning Rapport** is designed to provide potential homebuyers with deep, context-aware insights into real estate listings. It goes beyond standard data points, using an intelligent engine to analyze technical state, energy efficiency, personal preferences, and investment potential.

### Key Features

- **AI Trust & Transparency Architecture**: Every insight is labeled as **Fact** (from data) or **Inferred** (AI analysis), complete with **AI Provenance** (model/provider tracking) and **Proof of Reasoning**.
- **Domain Variable Authority**: Strict adherence to a domain-specific set of 14 variables per chapter, ensuring "Onbekend" states are explicitly detected and surfaced.
- **Multi-Check Pro Link**: Chrome/Edge extension for one-click ingestion from any Funda listing, bypassing CAPTCHAs and anti-bot measures.
- **Dynamic Interpretation Pipeline**: AI-driven attribute discovery that automatically extracts and classifies property facts with confidence scoring.
- **Multi-Source Ingestion**: Parse data via Funda URLs or direct HTML/Text paste. Robust handling of image pasting with automated upload.
- **AI Provider Factory**: Modular support for **Ollama** (Local), **OpenAI**, **Anthropic Claude**, and **Google Gemini**.
- **Advanced Parser**: High-accuracy extraction with multi-line support, logical validation, and cross-consistency checks.
- **Modern Magazine v2 Dashboard**: A premium, responsive interface featuring interactive charts, AI provenance headers, and a detailed domain variable grid.
- **Intelligent Pipeline**: Asynchronous processing with data persistence and automated PDF generation.
- **Runtime Configuration**: Granular control over AI models, market data, and user preferences via a dedicated Settings API.

## 🛠 Tech Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS v3, Recharts.
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLite.
- **AI Engine**: LangChain-style provider abstraction with robust fallback logic.
- **PDF Generation**: WeasyPrint with custom CSS styling.
- **Containerization**: Docker & Docker Compose.

## 🚦 Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start (Docker)

```bash
docker compose -f docker/docker-compose.yml up --build
```

Access the application at:
- **Application**: [http://localhost:8000](http://localhost:8000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Synology NAS Deployment

Deploy on Synology NAS using **pre-built Docker image** (no build required):

```bash
# SSH into your Synology NAS
cd /volume1/docker/funda-app

# Configure environment
cp docker/.env.synology .env
nano .env  # Add your API keys

# Deploy (downloads pre-built image from GitHub)
docker compose -f docker/docker-compose.synology.yml up -d
```

**Pre-built image benefits:**
- ✅ No build time (deploys in seconds)
- ✅ Multi-architecture (works on Intel & ARM)
- ✅ Auto-updated with each release

📖 **See [Synology Deployment Guide](docs/SYNOLOGY_DEPLOYMENT.md) for detailed instructions**


### Browser Extension

Install the Chrome/Edge extension for one-click data extraction from Funda.nl:

```bash
# 1. Load extension in browser
# Chrome: chrome://extensions/ → Enable Developer mode → Load unpacked
# Select: extension/ folder

# 2. Configure server (for remote/NAS)
# Right-click extension → Options → Enter your server URL
```

📖 **See [Extension Installation Guide](docs/EXTENSION_INSTALLATION.md) for detailed setup**



## 📁 Project Structure

```text
.
├── backend/            # FastAPI Backend, Intelligence Engine & AI Providers
├── frontend/           # React TypeScript Frontend & Bento Components
├── docs/               # Technical documentation & API Specs
├── data/               # Persistent SQLite database & Uploads
├── test-data/          # Example HTML fixtures for parser validation
└── docker-compose.yml  # Orchestration for the full stack
```

## 📖 Documentation

- [**API Specification**](docs/API.md): Full documentation of all REST endpoints.
- [**Architecture**](docs/ARCHITECTURE.md): Detailed system design and data flow diagrams.
- [**Configuration**](docs/CONFIGURATION.md): Environment variables and runtime settings guide.
- [**Parser Guide**](docs/PARSER.md): Field mapping, validation rules, and extraction logic.
- [**AI Providers**](docs/AI_PROVIDERS.md): Setup guide for different AI backends.
- [**Roadmap**](docs/ROADMAP.md): Future AI innovations and feature plan.
- [**Mandatory Guidelines**](GUIDELINES_MANDATORY.md): Enforced development and design standards.

## 🧪 Testing

We follow a **Zero Regression Policy**.

```bash
# Run all backend tests
cd backend && pytest

# Run frontend tests
cd frontend && npm test
```

## ⚖️ License

Internal/Private Project.
