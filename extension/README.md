# Multi-Check Pro Link - Browser Extension

## Quick Installation

### Chrome / Edge / Brave

1. Open browser and navigate to:
   - **Chrome**: `chrome://extensions/`
   - **Edge**: `edge://extensions/`
   - **Brave**: `brave://extensions/`

2. **Enable Developer Mode** (toggle in top-right corner)

3. Click **"Load unpacked"**

4. Select this `extension/` folder

5. **Done!** Extension is installed ✅

---

## Configure Server (Required for Remote/NAS)

**For localhost (same computer):** No configuration needed! Works automatically.

**For Synology NAS or remote server:**

1. Right-click the extension icon → Select **"Options"**
2. Enter your server URL:
   - LAN: `http://192.168.1.100:8000`
   - Hostname: `http://nas.local:8000`
   - Domain: `https://funda.yourdomain.com`
3. Click **"Opslaan" (Save)**
4. Green checkmark = Success!

---

## Usage

1. Go to any Funda property page
2. Click the extension icon
3. Click "Start Analyse"
4. Wait for success message
5. Click message to open report!

---

## Files in This Extension

```
extension/
├── manifest.json       # Extension configuration
├── popup.html          # Main popup interface
├── popup.js            # Popup logic
├── settings.html       # Settings page (NEW!)
├── settings.js         # Settings logic (NEW!)
├── content.js          # Funda page data extraction
├── background.js       # Background service worker
└── icons/              # Extension icons
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

---

## Version

**v5.0.0** - Now with configurable server URL!

**New in v5.0.0:**
- ✅ Configurable API server URL
- ✅ Settings page with connection testing
- ✅ Support for remote servers (LAN/WAN)
- ✅ Works with Synology NAS deployments

---

## Troubleshooting

**Extension not working?**
- Ensure you're on a Funda property page
- Refresh the page
- Check settings (right-click extension → Options)

**Can't connect to server?**
- Verify server is running: `curl http://YOUR_SERVER:8000/health`
- Check firewall settings
- Verify URL in extension settings

---

## Full Documentation

📖 [Complete Extension Installation Guide](../docs/EXTENSION_INSTALLATION.md)
