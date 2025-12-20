# AI Woning Rapport - Backend

The backend of the AI Woning Rapport is a FastAPI application responsible for data ingestion, property analysis, and report generation.

## 🏗 Architecture

The backend is built with a modular structure:

- **`main.py`**: Entry point, defines FastAPI routes and SSE (Server-Sent Events) logic.
- **`intelligence.py`**: The core logic engine. It generates narratives and chapter blocks based on parsed property data.
- **`parser.py`**: Robust HTML/Text parser that extracts nearly 100 attributes from Funda listings using regex and BeautifulSoup.
- **`ollama_client.py`**: Interface for AI-driven narrative enhancement (if enabled).
- **`domain/`**: Pydantic models for data validation and consistency.
- **`chapters/`**: Specific logic for each of the 13 report chapters.

## 🧪 Intelligence Engine

The `IntelligenceEngine` processes property data through a series of heuristics:
1. **Physical Analysis**: Area, volume, and build year categorization.
2. **Safety & Risk**: Automatic detection of asbestos, lead pipes, and foundation risks based on construction periods.
3. **Preference Matching**: Scoring the property against persona-specific keywords (Marcel & Petra).
4. **Financial Modeling**: Price per square meter and renovation cost estimations.

## 🚀 API Endpoints

- `POST /runs`: Start a new analysis run. Accepts `url` or `raw_html`.
- `GET /runs/{id}`: Fetch the current state of a run.
- `GET /runs/{id}/events`: SSE stream for real-time progress updates.
- `GET /runs/{id}/pdf`: Generate and download the PDF report.
- `GET /preferences`: Retrieve user preferences for the Personal Match.

## 🛠 Setup & Development

### Requirements
- Python 3.11+
- Requirements listed in `requirements.txt`

### Local Execution
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Testing
We use `pytest` for all backend tests.

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# Coverage
pytest --cov=. tests/
```

**Note**: Ensure `backend/tests/integration/test_docker_sync.py` passes to verify that the environment matches the production container.

## 📄 Documentation Links
- [Parser Specifications](../docs/PARSER.md)
- [API Specification](../docs/API.md)
- [System Architecture](../docs/ARCHITECTURE.md)
