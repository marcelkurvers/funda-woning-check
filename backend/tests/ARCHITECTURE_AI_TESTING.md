# Future-Proof AI Testing Architecture

## Executive Summary

This document defines the **structural separation** between AI capability validation (testable) and AI runtime availability (execution concern). Tests **MUST NOT** check whether AI services are running, reachable, or healthy.

## Core Principle

> **AI availability is an execution concern, not a correctness concern.**

Tests validate:
- ✅ **Structure**: Interfaces, contracts, schemas
- ✅ **Routing**: Provider selection, fallback logic
- ✅ **State**: Intent recording, status transitions
- ❌ **NOT Runtime**: Service health, network reachability, process availability

## Three-Layer Architecture

### 1️⃣ Capability & Contract Layer (STATIC - Tests operate here)

**Responsibility:**
- Provider registration and discovery
- Supported features and capabilities
- Input/output schema validation
- Configuration correctness
- Interface contracts

**Characteristics:**
- No network access
- No runtime checks
- Fully deterministic
- Provider-agnostic
- **✅ Tests live here**

**Example Tests:**
```python
def test_provider_contract_compliance():
    """Verify provider implements required interface"""
    provider = OllamaProvider()
    assert hasattr(provider, 'generate')
    assert hasattr(provider, 'check_health')
    assert hasattr(provider, 'list_models')
    assert provider.name == "ollama"

def test_provider_configuration_validation():
    """Verify provider accepts valid configuration"""
    # Should not raise
    provider = OllamaProvider(base_url="http://localhost:11434", timeout=30)
    assert provider.base_url == "http://localhost:11434"
    assert provider.timeout == 30
```

### 2️⃣ Execution Readiness Layer (DYNAMIC - Tests never touch)

**Responsibility:**
- Runtime reachability checks
- Model availability verification
- Resource constraint detection
- Service health monitoring

**Characteristics:**
- Network-dependent
- Non-deterministic
- Provider-specific
- **❌ Tests MUST NOT touch this**

**Failure Semantics:**
- Failures are **non-fatal**
- Reported as execution outcomes
- Never invalidate correctness
- Trigger graceful degradation

### 3️⃣ Execution & Outcome Layer (RUNTIME - Production only)

**Responsibility:**
- Real inference execution
- Timeout handling
- Partial result management
- Retry logic
- Graceful degradation

**Characteristics:**
- Real AI calls
- Runtime errors are events
- Never cause test failures
- **Production behavior only**

## Mandated Test Categories

### ✅ Contract Tests

**Purpose:** Verify provider conforms to interface

```python
def test_provider_interface_contract():
    """All providers must implement AIProvider interface"""
    from ai.provider_interface import AIProvider
    from ai.providers.ollama_provider import OllamaProvider
    
    provider = OllamaProvider()
    assert isinstance(provider, AIProvider)
    
def test_generate_signature():
    """Verify generate method signature matches contract"""
    import inspect
    from ai.providers.ollama_provider import OllamaProvider
    
    sig = inspect.signature(OllamaProvider.generate)
    params = list(sig.parameters.keys())
    
    assert 'prompt' in params
    assert 'model' in params
    assert 'system' in params
    assert 'temperature' in params
```

### ✅ Routing & Orchestration Tests

**Purpose:** Verify correct provider selection and fallback

```python
def test_provider_selection_logic():
    """Verify factory selects correct provider based on config"""
    from ai.provider_factory import ProviderFactory
    
    provider = ProviderFactory.create_provider("ollama")
    assert provider.name == "ollama"
    
    provider = ProviderFactory.create_provider("openai", api_key="test")
    assert provider.name == "openai"

def test_fallback_when_no_provider():
    """Verify system uses fallback when no provider set"""
    from intelligence import IntelligenceEngine
    
    IntelligenceEngine.set_provider(None)
    result = IntelligenceEngine.generate_chapter_narrative(1, {"address": "Test"})
    
    # Should return fallback structure
    assert isinstance(result, dict)
    assert 'title' in result
    assert 'intro' in result
```

### ✅ State & Persistence Tests

**Purpose:** Verify AI invocation intent is recorded correctly

```python
def test_ai_invocation_state_tracking():
    """Verify system records AI invocation attempts"""
    from intelligence import IntelligenceEngine
    from ai.providers.ollama_provider import OllamaProvider
    
    provider = OllamaProvider()
    IntelligenceEngine.set_provider(provider)
    
    # Verify provider is set (state change)
    assert IntelligenceEngine._provider is not None
    assert IntelligenceEngine._provider.name == "ollama"

def test_provider_configuration_persistence():
    """Verify provider configuration is stored correctly"""
    from ai.providers.ollama_provider import OllamaProvider
    
    provider = OllamaProvider(base_url="http://custom:11434", timeout=60)
    
    assert provider.base_url == "http://custom:11434"
    assert provider.timeout == 60
```

### ✅ Schema Validation Tests

**Purpose:** Verify output structure matches expected schema

```python
def test_narrative_output_schema():
    """Verify narrative output has required fields"""
    from intelligence import IntelligenceEngine
    
    IntelligenceEngine.set_provider(None)  # Use fallback
    result = IntelligenceEngine.generate_chapter_narrative(1, {
        "address": "Test",
        "price": 500000
    })
    
    # Required schema fields
    required_fields = ['title', 'intro', 'main_analysis', 'interpretation', 
                      'conclusion', 'strengths', 'advice']
    
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
    
    # Type validation
    assert isinstance(result['title'], str)
    assert isinstance(result['strengths'], list)
```

## Strict Failure Semantics

### ✅ Tests MAY fail for:
- Invalid configuration
- Broken interface contracts
- Schema violations
- Incorrect routing logic
- State inconsistencies
- Type mismatches

### ❌ Tests MUST NEVER fail for:
- Ollama not reachable
- Port unavailable
- Model not loaded
- Local service timing
- Network timeouts
- Service not running

## Provider-Agnostic Guarantee

All tests must:
1. **No provider-specific assumptions** in correctness checks
2. **No Ollama-specific logic** in test assertions
3. **No future provider requires test rewrites**
4. **Capability checks replace availability checks**

## Migration Strategy

For every existing AI test:

### Step 1: Identify Runtime Coupling
```python
# ❌ WRONG - Tests runtime availability
async def test_ollama_health_check(self):
    health = await self.ollama_provider.check_health()
    self.assertTrue(health)  # Fails if Ollama not running
```

### Step 2: Remove Runtime Dependency
```python
# ✅ CORRECT - Tests contract compliance
def test_provider_has_health_check_method(self):
    """Verify provider implements health check interface"""
    assert hasattr(self.ollama_provider, 'check_health')
    assert callable(self.ollama_provider.check_health)
```

### Step 3: Move to Contract Validation
```python
# ✅ CORRECT - Tests capability declaration
def test_provider_declares_capabilities(self):
    """Verify provider declares its capabilities"""
    provider = OllamaProvider()
    
    # Provider should declare what it supports
    assert provider.name == "ollama"
    assert isinstance(provider.list_models(), list)
    assert len(provider.list_models()) > 0  # Fallback list always present
```

### Step 4: Document What Changed
```markdown
## Test: test_ollama_health_check

**What was wrong:**
- Test checked if Ollama service was running
- Failed when Ollama unavailable
- Coupled correctness to runtime availability

**Why it was architecturally incorrect:**
- Service availability is an execution concern
- Tests should validate contracts, not runtime state
- Made tests non-deterministic

**How new test enforces correctness:**
- Validates health check method exists
- Verifies method signature matches contract
- Tests capability declaration, not execution
```

## Success Criteria

✅ **All tests pass with Ollama stopped**
✅ **All tests pass with no AI runtime installed**
✅ **Production inference still requires real runtime**
✅ **No mocked providers in tests**
✅ **No hard-coded environment paths**
✅ **No test-mode flags**
✅ **No false negatives**

## Implementation Checklist

- [ ] Create contract test suite for all providers
- [ ] Create routing test suite for provider selection
- [ ] Create schema validation test suite
- [ ] Remove all runtime health checks from tests
- [ ] Remove all network reachability tests
- [ ] Remove all service availability assertions
- [ ] Verify tests pass with all AI services stopped
- [ ] Document architectural decisions
- [ ] Update CI/CD to run tests without AI services

## Anti-Patterns to Avoid

### ❌ Testing Service Availability
```python
# WRONG
def test_ollama_is_running(self):
    response = requests.get("http://localhost:11434")
    assert response.status_code == 200
```

### ❌ Testing Network Reachability
```python
# WRONG
async def test_can_connect_to_ollama(self):
    try:
        await self.provider.check_health()
        assert True
    except:
        assert False, "Cannot connect to Ollama"
```

### ❌ Testing Model Availability
```python
# WRONG
def test_llama3_is_available(self):
    models = self.provider.list_models()
    assert "llama3" in models  # Fails if model not downloaded
```

### ✅ Testing Capability Declaration
```python
# CORRECT
def test_provider_declares_supported_models(self):
    """Provider should declare what models it supports"""
    models = self.provider.list_models()
    assert isinstance(models, list)
    assert len(models) > 0  # Fallback list always present
```

## Conclusion

This architecture ensures:
1. **Tests are deterministic** - Pass/fail based on code correctness only
2. **Tests are fast** - No network calls, no service dependencies
3. **Tests are future-proof** - New providers don't require test rewrites
4. **Production is unchanged** - Real AI calls still happen in production
5. **Failures are meaningful** - Test failures indicate actual bugs

**If any test concludes "Ollama is not running", the redesign has failed.**
