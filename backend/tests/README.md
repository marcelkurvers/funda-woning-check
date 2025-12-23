# AI Testing Architecture

## Overview

This directory contains tests for the AI Woning Rapport application, following a **future-proof, provider-agnostic testing architecture**.

## Core Principle

> **AI availability is an execution concern, not a correctness concern.**

Tests validate:
- ✅ **Structure**: Interfaces, contracts, schemas
- ✅ **Routing**: Provider selection, fallback logic
- ✅ **State**: Intent recording, status transitions
- ❌ **NOT Runtime**: Service health, network reachability, process availability

## Test Organization

### Contract Tests (`test_ai_contracts.py`)
Verify all AI providers implement the `AIProvider` interface correctly.

**What they test:**
- Interface compliance
- Configuration handling
- Capability declaration
- Schema adherence

**What they DON'T test:**
- Whether services are running
- Network connectivity
- Model availability

### Routing Tests (`test_ai_routing.py`)
Verify provider selection and orchestration logic.

**What they test:**
- Factory creates correct providers
- Engine manages provider state
- Fallback mechanisms work
- State transitions are clean

**What they DON'T test:**
- Whether AI calls succeed
- Network timeouts
- Service health

### Schema Tests (`test_ai_schema.py`)
Verify narrative outputs conform to expected structure.

**What they test:**
- Output has required fields
- Data types are correct
- Content uses actual data
- Schema consistency across chapters

**What they DON'T test:**
- AI content quality
- Whether AI is available
- Real AI generation

### Integration Tests (`test_ollama_integration.py`)
Verify components work together through their interfaces.

**What they test:**
- Provider injection works
- Preferences integrate correctly
- Multi-chapter consistency
- Error handling

**What they DON'T test:**
- Real AI calls
- Service availability
- Network reachability

### Logic Tests (`test_intelligence.py`)
Verify business logic and data processing.

**What they test:**
- Helper functions work correctly
- Chapter-specific logic
- Data parsing
- Narrative structure

**What they DON'T test:**
- AI runtime availability
- Real AI generation

## Running Tests

### Run All AI Tests
```bash
cd backend
pytest tests/unit/test_ai_*.py tests/unit/test_intelligence.py -v
```

### Run Specific Test Suite
```bash
cd backend
pytest tests/unit/test_ai_contracts.py -v
pytest tests/unit/test_ai_routing.py -v
pytest tests/unit/test_ai_schema.py -v
```

### Run Single Test
```bash
cd backend
pytest tests/unit/test_ai_contracts.py::TestProviderContracts::test_ollama_implements_interface -v
```

## Key Features

### ✅ Deterministic
All tests produce the same results every time. No flaky tests.

### ✅ Fast
No network calls, no service dependencies. Tests run in milliseconds.

### ✅ Provider-Agnostic
Tests work with Ollama, OpenAI, Anthropic, Gemini, and future providers.

### ✅ No External Dependencies
Tests pass with **ALL AI services stopped**. No Ollama, no API keys required.

### ✅ Meaningful Failures
Test failures indicate actual bugs in code, not missing services.

## Test Failure Semantics

### ✅ Tests MAY Fail For:
- Invalid configuration
- Broken interface contracts
- Schema violations
- Incorrect routing logic
- State inconsistencies
- Type mismatches

### ❌ Tests MUST NEVER Fail For:
- Ollama not reachable
- Port unavailable
- Model not loaded
- Local service timing
- Network timeouts
- Service not running

## Architecture Documents

- **`ARCHITECTURE_AI_TESTING.md`** - Full architectural specification
- **`MIGRATION_SUMMARY.md`** - Migration from old to new architecture

## Adding New Tests

### DO: Test Contracts
```python
def test_new_provider_implements_interface(self):
    """Verify new provider implements AIProvider"""
    provider = NewProvider()
    assert isinstance(provider, AIProvider)
```

### DO: Test Configuration
```python
def test_new_provider_accepts_config(self):
    """Verify new provider accepts configuration"""
    provider = NewProvider(api_key="test", timeout=30)
    assert provider.timeout == 30
```

### DON'T: Test Availability
```python
# ❌ WRONG - Don't do this
async def test_new_provider_is_available(self):
    health = await provider.check_health()
    assert health == True  # Fails if service not running
```

### DON'T: Test Network Calls
```python
# ❌ WRONG - Don't do this
async def test_new_provider_generates_text(self):
    result = await provider.generate("test prompt")
    assert len(result) > 0  # Requires real API call
```

## CI/CD Integration

Tests are designed to run in CI/CD without any AI services:

```yaml
# .github/workflows/test.yml
- name: Run Tests
  run: |
    cd backend
    pytest tests/unit/test_ai_*.py -v
  # No need to start Ollama or configure API keys!
```

## Success Criteria

A test suite is correctly implemented if:

✅ All tests pass with Ollama stopped
✅ All tests pass with no AI runtime installed
✅ All tests pass with no API keys configured
✅ Tests are fast (< 1 second total)
✅ Tests are deterministic (same results every run)
✅ Test failures indicate real bugs

## Anti-Patterns

### ❌ Don't Test Service Health
```python
# WRONG
def test_ollama_is_running(self):
    response = requests.get("http://localhost:11434")
    assert response.status_code == 200
```

### ❌ Don't Test Network Reachability
```python
# WRONG
async def test_can_connect_to_api(self):
    try:
        await provider.check_health()
        assert True
    except:
        assert False, "Cannot connect"
```

### ❌ Don't Test Model Availability
```python
# WRONG
def test_model_is_downloaded(self):
    models = provider.list_models()
    assert "llama3" in models  # Fails if not downloaded
```

## Production vs. Test Behavior

### Production (Real AI Calls)
```python
# In production, with provider set
IntelligenceEngine.set_provider(OllamaProvider())
result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
# → Makes real AI call if Ollama available
# → Falls back to data-driven content if not
```

### Tests (Fallback Mode)
```python
# In tests, no provider set
IntelligenceEngine.set_provider(None)
result = IntelligenceEngine.generate_chapter_narrative(1, ctx)
# → Always uses fallback (deterministic)
# → No AI calls, no network dependencies
```

## Questions?

See:
- `ARCHITECTURE_AI_TESTING.md` for full architectural details
- `MIGRATION_SUMMARY.md` for migration history
- Individual test files for examples

## Final Note

**If any test concludes "Ollama is not running", the test is incorrect.**

Tests validate correctness, not availability. Runtime availability is an execution concern handled by production code, not tests.
