# AI Woning Rapport

A powerful, data-driven real estate analysis tool that transforms Funda listings into comprehensive, personalized property reports.

## 🚀 Overview

The **AI Woning Rapport** is designed to provide potential homebuyers (specifically tailored for "Marcel & Petra") with deep, context-aware insights into real estate listings. It goes beyond standard data points, using an intelligent engine to analyze technical state, energy efficiency, personal preferences, and investment potential.

### Key Features

- **Multi-Source Ingestion**: Parse data via Funda URLs or direct HTML/Text paste (bypassing scrapers).
- **Intelligence Engine**: 13 unique analysis chapters including Technical State, Energy, Maintenance, and Personal Match.
- **Bento Grid Dashboard**: A modern, responsive React interface optimized for 4K displays.
- **Personalized Logic**: Weighted matching system based on specific user personas (Marcel & Petra).
- **High-Quality PDF**: Professional magazine-style PDF generation via WeasyPrint.
- **Live Processing**: Real-time analysis status updates via SSE (Server-Sent Events).

## 🛠 Tech Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS v3.
- **Backend**: Python 3.11+, FastAPI, SQLite.
- **Analysis**: Custom `IntelligenceEngine` with rule-based heuristics and AI-simulated narratives.
- **PDF Generation**: WeasyPrint with custom CSS styling.
- **Containerization**: Docker & Docker Compose.

## 🚦 Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Recommended)
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start (Docker)

The easiest way to run the entire stack is using Docker:

```bash
docker compose up --build
```

Access the application at:
- **Frontend**: [http://localhost:8000](http://localhost:8000) (Served by Backend)
- **Direct Frontend Dev**: [http://localhost:5173](http://localhost:5173) (if running Vite separately)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📁 Project Structure

```text
.
├── backend/            # FastAPI Backend & Intelligence Engine
├── frontend/           # React TypeScript Frontend
├── docs/               # Technical documentation & PRD
├── data/               # Persistent SQLite database
├── test-data/          # Example HTML files for parsing tests
└── docker-compose.yml  # Orchestration for the full stack
```

## 📖 Documentation

- [**PRD**](docs/PRODUCT_REQUIREMENTS_DOCUMENT.md): Full product requirements and chapter specifications.
- [**Mandatory Guidelines**](GUIDELINES_MANDATORY.md): Enforced development and design standards.
- [**Backend Docs**](backend/README.md): API details and Intelligence Engine logic.
- [**Frontend Docs**](frontend/README.md): UI component library and Bento layout guide.
- [**Color System**](docs/design/COLOR_CODING_SYSTEM.md): Semantic color coding and visualization rules.

## 🧪 Testing

We follow a **Zero Regression Policy**. All changes must pass the full test suite.

```bash
# Run all backend tests
cd backend
pytest tests/
```

For more details on testing, see [docs/technical/TEST_COVERAGE_SUMMARY.md](docs/technical/TEST_COVERAGE_SUMMARY.md).

## ⚖️ License

Internal/Private Project.
