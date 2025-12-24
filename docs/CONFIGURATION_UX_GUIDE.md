# Explicit Configuration UX Guide

This guide explains how to configure the AI Woning Rapport Pro system with full visibility and control over all settings.

## Quick Start

1. Open the application at `localhost:8000`
2. Navigate to **Settings** (gear icon in the sidebar)
3. Select your AI provider and model
4. Choose an operating mode
5. Save your configuration

## Configuration Philosophy

### Explicit, Not Implicit

This system operates on the principle of **explicit configuration**:

- **No silent defaults**: The system will never silently switch to Ollama if your preferred provider fails
- **No hidden fallbacks**: If OpenAI is configured but the key is missing, you'll get a clear error - not a silent switch to another provider
- **Visible status**: All configuration states are visible in the UI

### Fail-Closed Behavior

The system follows fail-closed principles:

- If **FULL mode** is selected but AI is unavailable → **Error** (not silent degradation)
- If **FAST mode** is selected but provider times out → **Error with clear message**
- If provider key is missing → **Clear error message, not silent fallback**

## Operating Modes

### ⚡ FAST Mode
- Shortened narratives
- Speed-optimized analysis
- Still requires a working AI provider
- Best for: Quick property assessments

### 📊 FULL Mode
- Complete 4-plane analysis
- Full narrative generation (300+ words per chapter)
- All KPIs and metrics calculated
- Best for: Final property reports

### 🔧 DEBUG Mode
- **No AI calls made**
- Uses deterministic placeholders
- All structure rendered (planes, layout)
- "AI disabled by mode" shown in UI
- Best for: Testing and development

### 📴 OFFLINE Mode
- No network calls
- Local processing only
- Same as DEBUG - no AI
- Best for: Environments without internet

## Setting Up API Keys

### Security First

**CRITICAL**: API keys are NEVER:
- Displayed in the UI
- Returned in API responses
- Stored in the database
- Logged anywhere

The UI only shows:
- Whether a key is present (yes/no)
- The source (env/config/secret)
- Last updated timestamp
- Optionally: Last 4 characters (fingerprint) - only with explicit user action

### How to Set Keys

Keys must be set via **environment variables**:

```bash
# OpenAI
export OPENAI_API_KEY="sk-your-key-here"

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Google Gemini
export GEMINI_API_KEY="your-gemini-key-here"
```

For Docker deployments, add to your `.env` file:

```env
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GEMINI_API_KEY=your-gemini-key-here
```

### Verifying Key Configuration

1. Go to **Settings → API Keys & Security**
2. Each provider shows:
   - ✓ Geconfigureerd (if key present)
   - ✗ Ontbreekt (if key missing)
   - Source: `env` or `config`

3. Click **Test Provider** to verify the key works

## AI Provider Selection

### Available Providers

| Provider | Type | Key Required | Models |
|----------|------|--------------|--------|
| **Ollama** | Local | No | llama3, mistral, phi3 |
| **OpenAI** | Cloud | Yes | gpt-4o, gpt-4o-mini |
| **Anthropic** | Cloud | Yes | claude-3-5-sonnet |
| **Gemini** | Cloud | Yes | gemini-2.0-flash |

### Selecting a Provider

1. Go to **Settings → AI Provider Selection**
2. Click on a provider tile
3. Select a model from the dropdown
4. Click **Test Connection** to verify
5. Click **Save** to apply

### Model Selection

Models are provider-specific:

**Ollama (Local)**
- llama3, llama3.1, mistral, phi3, qwen2

**OpenAI**
- gpt-4o (recommended)
- gpt-4o-mini (faster, cheaper)
- gpt-4-turbo

**Anthropic**
- claude-3-5-sonnet-20241022 (recommended)
- claude-3-opus-20240229
- claude-3-haiku-20240307

**Google Gemini**
- gemini-2.0-flash-exp (fastest)
- gemini-1.5-pro
- gemini-1.5-flash

## Performance Settings

### Timeout

The timeout determines how long to wait for provider responses:

| Setting | Use Case |
|---------|----------|
| 5-20s | Fast responses, risk of timeouts |
| 30-60s | Balanced (recommended) |
| 120-180s | Long-form generation |

### Temperature

Controls output randomness:

- **0.0**: Deterministic, consistent
- **0.7**: Balanced (default)
- **1.0+**: Creative, varied

### Max Tokens

Maximum response length:

- **2048**: Short responses
- **4096**: Standard (default)
- **8192+**: Long-form content

## Real-Time Status Panel

During report generation, the UI shows:

### Pipeline Steps
1. **Scrape & Parse** - Extracting data from Funda
2. **Dynamic Extraction** - AI attribute discovery
3. **Registry Build** - Building canonical data registry
4. **4-Plane Generation** - Creating Planes A/B/C/D
5. **Validation Gate** - Checking output validity
6. **Render Output** - Final formatting

### Status Indicators
- 🔵 Running (with spinner)
- ✅ Done (with elapsed time)
- ❌ Error (with message)
- ⏭️ Skipped

### Current Activity
Shows which chapter and plane is being generated:
- "Hoofdstuk 3 - Vlak B"
- "Genereren van Narratief"

## Browser Extension Configuration

The browser extension can also configure the backend:

### Extension Settings

1. Click the extension icon
2. Select **Instellingen**

You can configure:
- **Server URL**: Backend address
- **Provider**: AI provider to use
- **Model**: Specific model
- **Mode**: Operating mode

### Syncing with Server

Changes made in the extension are synced to the server via `/api/config/update`.

The extension shows key status (present/missing) fetched from the server - without ever seeing the actual keys.

## API Endpoints

### Configuration Status
```
GET /api/config/status?show_fingerprint=false
```

Returns safe configuration status including:
- Current provider/model/mode
- Key status (present, source - never raw keys)
- Provider availability
- Health status

### Update Configuration
```
POST /api/config/update
{
  "provider": "openai",
  "model": "gpt-4o",
  "mode": "full",
  "timeout": 60
}
```

### Test Provider
```
POST /api/config/test-provider
{
  "provider": "openai",
  "model": "gpt-4o"
}
```

Returns test result with latency.

### Live Run Status
```
GET /api/runs/{run_id}/live-status
```

Real-time pipeline telemetry including:
- Current step
- Current plane being generated
- Progress percentage
- Warnings and errors

## Troubleshooting

### "API key ontbreekt"
**Problem**: Provider requires a key but none is configured.  
**Solution**: Set the environment variable for the provider.

### "Ollama niet beschikbaar"
**Problem**: Ollama is selected but not running.  
**Solution**: Start Ollama with `ollama serve`.

### "Test failed: Network error"
**Problem**: Cannot reach provider API.  
**Solution**: Check internet connection and firewall settings.

### "Validation failed"
**Problem**: Generated content failed validation.  
**Solution**: Check the warnings/errors in the run status panel.

## Security Checklist

✅ API keys set via environment variables only  
✅ Keys never in database or config files  
✅ UI never displays raw keys  
✅ API responses never include raw keys  
✅ Fingerprint shown only with explicit user action  
✅ Extension cannot access server's raw keys  
