# AI Woning Rapport - Migration Guide

**Version**: 2.0
**Last Updated**: 2025-12-20

This document provides step-by-step instructions for migrating the codebase to the new architecture.

---

## 1. Migration Overview

### What's Changing

| Area | Current State | Target State |
|------|---------------|--------------|
| AI Backend | Single Ollama client | Multi-provider abstraction |
| Configuration | Hardcoded values | Centralized settings + UI |
| Landing Page | Custom LandingPage.tsx | New UI from zip file |
| Chapter Layouts | One-size-fits-all Bento Grid | Context-aware per-chapter layouts |
| Settings | Hidden preferences page | Full settings page at /settings |

### Migration Phases

1. **Phase 1:** Documentation (this document)
2. **Phase 2:** Backend configuration system
3. **Phase 3:** AI provider abstraction
4. **Phase 4:** Frontend settings page
5. **Phase 5:** New landing page
6. **Phase 6:** Context-aware chapter layouts
7. **Phase 7:** Code quality cleanup
8. **Phase 8:** Testing and Docker updates

---

## 2. Phase 2: Backend Configuration System

### Step 2.1: Create config directory

```bash
mkdir -p backend/config
touch backend/config/__init__.py
```

### Step 2.2: Create settings.py

Create `backend/config/settings.py` with `AppSettings` class (see CONFIGURATION.md for full spec).

### Step 2.3: Migrate hardcoded values

| File | Line | Old Code | New Code |
|------|------|----------|----------|
| `main.py` | 469 | `market_avg = 5200` | `market_avg = settings.market_avg_price_m2` |
| `main.py` | 445-450 | Hardcoded thresholds | `settings.fit_score_*` |
| `main.py` | 180 | `max_workers=2` | `settings.max_workers` |
| `parser.py` | Class vars | `MAX_BEDROOMS = 15` | `settings.max_bedrooms` |
| `ollama_client.py` | 92 | `timeout=30` | `settings.ai_timeout` |

### Step 2.4: Add config API endpoints

Add to `main.py`:

```python
from config.settings import get_settings, update_settings

@app.get("/api/config")
def get_config():
    return get_settings().dict()

@app.put("/api/config")
def update_config(updates: dict):
    return update_settings(updates)
```

### Step 2.5: Test configuration

```bash
cd backend
pytest tests/unit/test_config.py -v
```

---

## 3. Phase 3: AI Provider Abstraction

### Step 3.1: Create ai directory

```bash
mkdir -p backend/ai/providers
touch backend/ai/__init__.py
touch backend/ai/providers/__init__.py
```

### Step 3.2: Create provider interface

Create `backend/ai/provider_interface.py` (see AI_PROVIDERS.md for spec).

### Step 3.3: Refactor Ollama client

Move `backend/ollama_client.py` to `backend/ai/providers/ollama_provider.py`:

```python
# Old import
from ollama_client import OllamaClient

# New import
from ai.providers.ollama_provider import OllamaProvider
```

### Step 3.4: Implement new providers

Create in `backend/ai/providers/`:
- `openai_provider.py`
- `anthropic_provider.py`
- `gemini_provider.py`

### Step 3.5: Create provider factory

Create `backend/ai/provider_factory.py`:

```python
class ProviderFactory:
    @staticmethod
    def get_provider(settings) -> AIProvider:
        # Implementation
```

### Step 3.6: Update intelligence.py

```python
# Old
from ollama_client import OllamaClient
_client: Optional[OllamaClient] = None

# New
from ai.provider_interface import AIProvider
from ai.provider_factory import ProviderFactory
_provider: Optional[AIProvider] = None
```

### Step 3.7: Update requirements.txt

Add:
```
openai>=1.0.0
anthropic>=0.18.0
google-generativeai>=0.3.0
httpx>=0.24.0
pydantic-settings>=2.0.0
```

### Step 3.8: Test providers

```bash
pytest tests/unit/test_ai_providers.py -v
```

---

## 4. Phase 4: Frontend Settings Page

### Step 4.1: Install dependencies

```bash
cd frontend
npm install react-router-dom
```

### Step 4.2: Create pages directory

```bash
mkdir -p src/pages
mkdir -p src/contexts
mkdir -p src/services
mkdir -p src/components/settings
```

### Step 4.3: Create ConfigContext

Create `src/contexts/ConfigContext.tsx`:

```typescript
export const ConfigProvider: React.FC = ({ children }) => {
  // Load config from /api/config
  // Provide to children
};
```

### Step 4.4: Create Settings page

Create `src/pages/Settings.tsx` with sections:
- AI Provider Settings
- Market Settings
- Parser Settings
- Appearance Settings

### Step 4.5: Add routing

Update `src/App.tsx`:

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';

<BrowserRouter>
  <Routes>
    <Route path="/" element={<Landing />} />
    <Route path="/report/:id" element={<Report />} />
    <Route path="/settings" element={<Settings />} />
  </Routes>
</BrowserRouter>
```

### Step 4.6: Test settings page

```bash
npm run dev
# Navigate to http://localhost:5173/settings
```

---

## 5. Phase 5: New Landing Page

### Step 5.1: Extract from zip file

```bash
unzip funda.nl-huis-analyse.zip -d /tmp/new-ui
```

### Step 5.2: Create landing components

Copy and adapt:
- `/tmp/new-ui/components/Header.tsx` → `src/components/layout/Header.tsx`
- `/tmp/new-ui/components/Hero.tsx` → `src/components/landing/Hero.tsx`
- `/tmp/new-ui/components/MediaZone.tsx` → `src/components/landing/MediaZone.tsx`
- `/tmp/new-ui/components/DeepDive.tsx` → `src/components/landing/DeepDive.tsx`
- `/tmp/new-ui/components/Footer.tsx` → `src/components/layout/Footer.tsx`

### Step 5.3: Update Tailwind config

Add to `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: "#137fec",
      "background-light": "#f6f7f8",
      "background-dark": "#101922",
      "surface-dark": "#192633",
      "border-dark": "#233648"
    }
  }
}
```

### Step 5.4: Create Landing page

Create `src/pages/Landing.tsx` combining Hero + MediaZone with existing paste/URL logic.

### Step 5.5: Remove old LandingPage

```bash
rm src/components/LandingPage.tsx
```

---

## 6. Phase 6: Context-Aware Chapter Layouts

### Step 6.1: Create chapters directory

```bash
mkdir -p src/components/chapters
```

### Step 6.2: Create ChapterRenderer

Create `src/components/chapters/ChapterRenderer.tsx`:

```typescript
const ChapterRenderer: React.FC<{ chapter: Chapter }> = ({ chapter }) => {
  switch (chapter.id) {
    case "0": return <DashboardLayout data={chapter} />;
    case "1": case "5": case "8": return <MetricsLayout data={chapter} />;
    case "2": return <MatchLayout data={chapter} />;
    case "3": case "9": return <RiskLayout data={chapter} />;
    case "4": return <GaugeLayout data={chapter} />;
    case "6": case "7": return <ComparisonLayout data={chapter} />;
    case "10": case "11": return <FinancialLayout data={chapter} />;
    case "12": return <ConclusionLayout data={chapter} />;
    default: return <MetricsLayout data={chapter} />;
  }
};
```

### Step 6.3: Create layout components

Create each layout with unique visual design:

| Layout | Key Visual Elements |
|--------|---------------------|
| `DashboardLayout.tsx` | Hero stats bar, metrics grid, summary card |
| `MetricsLayout.tsx` | Left panel metrics, right panel narrative |
| `MatchLayout.tsx` | Split view: Marcel (left) vs Petra (right) |
| `RiskLayout.tsx` | Risk matrix visual, warning cards |
| `GaugeLayout.tsx` | Energy gauge/dial, improvement checklist |
| `ComparisonLayout.tsx` | Before/after or side-by-side comparison |
| `FinancialLayout.tsx` | Bar charts, waterfall, cost breakdown |
| `ConclusionLayout.tsx` | Large recommendation card, final score |

### Step 6.4: Update Report page

Replace inline chapter rendering with ChapterRenderer:

```typescript
// Old
{content && <BentoGrid>...</BentoGrid>}

// New
{currentChapter && <ChapterRenderer chapter={currentChapter} />}
```

---

## 7. Phase 7: Code Quality Cleanup

### Step 7.1: Fix audit issues

| File | Issue | Fix |
|------|-------|-----|
| `parser.py:94,134` | Duplicate `_extract_address()` | Remove duplicate |
| `intelligence.py:856` | Mock score logic | Real calculation |
| `chapter_0.py:87` | Print debugging | Use logger |
| `chapter_4.py:103` | Mock data | Config default |
| `domain/models.py:39` | `grid_layout: Any` | Proper type |

### Step 7.2: Remove deprecated files

```bash
rm backend/ollama_client.py  # Moved to ai/providers/
```

### Step 7.3: Update imports throughout codebase

Search and replace old imports with new ones.

---

## 8. Phase 8: Testing and Docker

### Step 8.1: Run existing tests

```bash
cd backend && pytest tests/ -v
cd frontend && npm test
```

### Step 8.2: Add new tests

- `backend/tests/unit/test_ai_providers.py`
- `backend/tests/unit/test_config.py`
- `frontend/src/test/Settings.test.tsx`

### Step 8.3: Update Docker environment

Add to `docker-compose.yml`:

```yaml
environment:
  - AI_PROVIDER=${AI_PROVIDER:-ollama}
  - OPENAI_API_KEY=${OPENAI_API_KEY:-}
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
  - GEMINI_API_KEY=${GEMINI_API_KEY:-}
```

### Step 8.4: Test full stack

```bash
docker-compose down
docker-compose up --build
```

---

## 9. Rollback Plan

If issues arise, rollback steps:

1. **Git reset:** `git checkout main`
2. **Restore database:** Backup `data/local_app.db` before migration
3. **Restart Docker:** `docker-compose down && docker-compose up --build`

---

## 10. Post-Migration Checklist

- [ ] All tests pass
- [ ] Settings page functional
- [ ] All AI providers working
- [ ] Landing page displays correctly
- [ ] All 13 chapters render with unique layouts
- [ ] PDF export still works
- [ ] Docker deployment successful
- [ ] Documentation updated
