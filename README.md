# AI Woning Rapport

A powerful, data-driven real estate analysis tool that transforms Funda listings into comprehensive, personalized property reports.

## 🚀 Overview

The **AI Woning Rapport** is designed to provide potential homebuyers with deep, context-aware insights into real estate listings. It goes beyond standard data points, using an intelligent engine to analyze technical state, energy efficiency, personal preferences, and investment potential.

### Key Features

- **Multi-Source Ingestion**: Parse data via Funda URLs or direct HTML/Text paste. Robust handling of image pasting with automated upload.
- **AI Provider Factory**: Modular support for **Ollama** (Local), **OpenAI**, **Anthropic Claude**, and **Google Gemini**.
- **Advanced Parser**: High-accuracy extraction with multi-line support, logical validation, and cross-consistency checks.
- **Dynamic Bento Dashboard**: A premium, responsive interface optimized for any resolution, featuring interactive charts and real-time status tracking.
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
docker compose up --build
```

Access the application at:
- **Application**: [http://localhost:8000](http://localhost:8000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

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
