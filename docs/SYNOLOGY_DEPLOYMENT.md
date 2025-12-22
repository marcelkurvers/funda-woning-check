# Synology NAS Deployment Guide

This guide explains how to deploy AI Woning Rapport on your Synology NAS using Docker/Container Manager.

## Prerequisites

- Synology NAS with **Container Manager** (DSM 7.2+) or **Docker** (DSM 6.x/7.0-7.1)
- At least **4GB RAM** available (8GB+ recommended for Ollama)
- SSH access to your NAS (optional, for command-line deployment)
- At least one AI provider API key (OpenAI, Anthropic, or Gemini)

## Quick Start (SSH)

If you have SSH access to your Synology, this is the fastest method:

```bash
# 1. SSH into your Synology
ssh admin@your-nas-ip

# 2. Navigate to your docker folder
cd /volume1/docker

# 3. Clone or copy the project
git clone https://github.com/your-repo/funda-app.git
cd funda-app

# 4. Create your environment file
cp docker/.env.synology .env

# 5. Edit .env with your API keys
vi .env   # or nano .env

# 6. Create the data directory
mkdir -p /volume1/docker/funda-app/data

# 7. Start the containers
docker compose -f docker/docker-compose.synology.yml up -d

# 8. View logs
docker compose -f docker/docker-compose.synology.yml logs -f
```

## Detailed Setup Guide

### Step 1: Prepare Shared Folders

Create the following folder structure on your Synology:

```
/volume1/docker/
└── funda-app/
    ├── data/           # Application database and uploads
    └── ollama/         # Ollama models (optional, if binding path)
```

You can create these via:
- **File Station**: Navigate to `docker` folder and create `funda-app/data`
- **SSH**: `mkdir -p /volume1/docker/funda-app/data`

### Step 2: Upload Project Files

**Option A - Git Clone (Recommended)**
```bash
cd /volume1/docker
git clone https://github.com/your-repo/funda-app.git
```

**Option B - File Upload**
1. Download the project as a ZIP file
2. Extract on your computer
3. Upload via File Station to `/volume1/docker/funda-app/`

### Step 3: Configure Environment

1. Copy the Synology environment template:
   ```bash
   cd /volume1/docker/funda-app
   cp docker/.env.synology .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   # Required: At least one AI provider key
   OPENAI_API_KEY=sk-your-openai-key-here
   
   # Optional: Additional providers
   ANTHROPIC_API_KEY=
   GEMINI_API_KEY=
   
   # Synology paths (adjust volume1 if needed)
   DATA_PATH=/volume1/docker/funda-app/data
   ```

### Step 4: Build and Deploy

**Via SSH (Recommended)**

```bash
cd /volume1/docker/funda-app

# Build the image (first time only, takes a few minutes)
docker compose -f docker/docker-compose.synology.yml build

# Start the containers
docker compose -f docker/docker-compose.synology.yml up -d
```

**Via Container Manager UI**

1. Open **Container Manager** in DSM
2. Go to **Project**
3. Click **Create**
4. Set:
   - **Project name**: `funda-woning-rapport`
   - **Path**: `/volume1/docker/funda-app`
   - **Source**: `docker/docker-compose.synology.yml`
5. Click **Next** and review settings
6. Click **Done** to deploy

### Step 5: First-Time Ollama Setup

The first time you start, you need to pull an Ollama model:

```bash
# Pull the recommended model (llama3.1:8b or smaller for NAS)
docker exec -it ollama ollama pull llama3.1:8b

# Verify it's downloaded
docker exec -it ollama ollama list
```

> **💡 Tip**: For NAS with limited RAM, use smaller models:
> - `llama3.2:3b` - 3B parameters, ~3GB RAM
> - `phi3:mini` - Good for 4GB systems
> - `gemma2:2b` - Lightweight but capable

### Step 6: Access the Application

Open your browser and navigate to:

```
http://your-nas-ip:8000
```

Or if you configured a different port in `.env`:
```
http://your-nas-ip:YOUR_APP_PORT
```

### Step 7: Install Browser Extension (Optional but Recommended)

The Chrome/Edge extension allows one-click data extraction from Funda.nl:

1. **Install the extension:**
   - Open Chrome/Edge and go to `chrome://extensions/`
   - Enable **"Developer mode"**
   - Click **"Load unpacked"**
   - Select the `extension/` folder from this project

2. **Configure server URL:**
   - Right-click the extension icon → **"Options"**
   - Enter your Synology URL: `http://your-nas-ip:8000`
   - Click **"Opslaan"** (Save)
   - Green checkmark = Connected! ✅

3. **Test it:**
   - Navigate to any Funda property listing
   - Click the extension icon
   - Click **"Start Analyse"**
   - Report opens automatically!

📖 **Full guide**: [Extension Installation](EXTENSION_INSTALLATION.md)


## Container Management

### View Logs

```bash
# All containers
docker compose -f docker/docker-compose.synology.yml logs -f

# Just the app
docker compose -f docker/docker-compose.synology.yml logs -f app
```

### Stop Containers

```bash
docker compose -f docker/docker-compose.synology.yml down
```

### Update to New Version

```bash
cd /volume1/docker/funda-app

# Pull latest changes
git pull

# Rebuild and restart
docker compose -f docker/docker-compose.synology.yml up -d --build
```

### View Container Status

```bash
docker compose -f docker/docker-compose.synology.yml ps
```

## Troubleshooting

### Container Won't Start

1. **Check logs**:
   ```bash
   docker compose -f docker/docker-compose.synology.yml logs app
   ```

2. **Verify ports aren't in use**:
   ```bash
   netstat -tlnp | grep 8000
   ```

3. **Check disk space**:
   ```bash
   df -h /volume1
   ```

### "Ollama connection refused" Error

1. Ensure Ollama container is running:
   ```bash
   docker ps | grep ollama
   ```

2. Check Ollama health:
   ```bash
   curl http://localhost:11434/
   ```

3. Verify network connectivity:
   ```bash
   docker network inspect funda-network
   ```

### Out of Memory (OOM) Errors

1. Use a smaller Ollama model
2. Increase memory limits in `docker/docker-compose.synology.yml`:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 4G  # Increase as needed
   ```

3. Stop other containers to free RAM

### Permission Denied on Data Directory

```bash
# Fix ownership
sudo chown -R 1000:1000 /volume1/docker/funda-app/data

# Or allow all access
sudo chmod -R 755 /volume1/docker/funda-app/data
```

### AI Not Working (No Responses)

1. **Verify API keys are set**:
   ```bash
   docker exec funda-woning-rapport printenv | grep API_KEY
   ```

2. **Check AI status**:
   ```bash
   curl http://localhost:8000/api/v1/config/ai-status
   ```

3. **Ensure at least one provider is configured** (OpenAI, Anthropic, Gemini, or Ollama)

## Resource Recommendations

| NAS RAM | Recommended Ollama Model | Notes |
|---------|--------------------------|-------|
| 4GB     | `gemma2:2b` or external API | Limited local AI capability |
| 8GB     | `llama3.2:3b` or `phi3:mini` | Good for basic analysis |
| 16GB+   | `llama3.1:8b` | Full local AI capability |

> **💡 Tip**: If your NAS has limited RAM, use OpenAI/Anthropic/Gemini APIs instead of local Ollama. Set the API keys in `.env` and the app will automatically use them.

## Backup

### Data Backup

Your important data is in the `data` directory:
```bash
# Backup
tar -czf funda-backup-$(date +%Y%m%d).tar.gz /volume1/docker/funda-app/data

# Restore
tar -xzf funda-backup-YYYYMMDD.tar.gz -C /
```

### Ollama Models Backup

If using a bound path for Ollama models:
```bash
tar -czf ollama-models-backup.tar.gz /volume1/docker/funda-app/ollama
```

## Accessing from Outside Your Network

### Option 1: Synology QuickConnect
Enable QuickConnect and access via `http://quickconnect.to/your-id:8000`

### Option 2: Synology DDNS + Port Forwarding
1. Set up DDNS in Control Panel
2. Forward port 8000 on your router
3. Access via `http://your-ddns-name:8000`

### Option 3: Reverse Proxy (Recommended)
1. Go to **Control Panel** → **Login Portal** → **Advanced** → **Reverse Proxy**
2. Create a new rule:
   - **Source**: `https://funda.your-domain.com`
   - **Destination**: `http://localhost:8000`
3. Set up SSL certificate in Certificate Manager

---

## Need Help?

If you encounter issues not covered here, check the container logs and ensure all prerequisites are met. The most common issues are related to memory limits and API key configuration.
