# Browser Extension Installation Guide

The **Multi-Check Pro Link** Chrome/Edge extension allows you to extract property data directly from Funda.nl with one click and send it to your AI Woning Rapport server (local or Synology NAS).

## Features

✅ **One-Click Data Extraction** from Funda property pages  
✅ **Photo Gallery Export** - Automatic extraction of all property images  
✅ **Configurable Server URL** - Works with localhost, LAN servers, or remote Synology NAS  
✅ **Connection Testing** - Built-in health check for your API server  

---

## Quick Installation

### Step 1: Load Extension in Chrome/Edge

1. **Download the Extension**
   - Clone this repository or download as ZIP
   - Navigate to the `extension/` folder

2. **Open Extensions Page**
   - **Chrome**: Go to `chrome://extensions/`
   - **Edge**: Go to `edge://extensions/`

3. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in the top-right corner

4. **Load the Extension**
   - Click **"Load unpacked"**
   - Select the `/extension/` folder from this project
   - The extension icon should appear in your browser toolbar

### Step 2: Configure Server URL

#### For Local Development (Same Computer)

**Default setting works automatically:**  
`http://localhost:8000`

No configuration needed! ✅

---

#### For Synology NAS or Remote Server

1. **Click the extension icon** in your browser toolbar
2. **Right-click the extension** → Select **"Options"** (or **"Settings"**)
3. **Enter your server URL**:

   **Examples:**
   ```
   http://192.168.1.100:8000        # LAN IP address
   http://nas.local:8000             # mDNS hostname
   http://synology:8000              # Network name
   https://funda.yourdomain.com      # Domain with reverse proxy
   ```

4. **Click "Opslaan" (Save)**
   - The extension will test the connection
   - Green checkmark = Success! ✅
   - Red error = Check your URL or server status

---

## Finding Your Server URL

### Option 1: Using Synology IP Address

1. Open **DSM** (Synology web interface)
2. Go to **Control Panel** → **Network** → **Network Interface**
3. Note your **LAN IP** (e.g., `192.168.1.100`)
4. Use: `http://YOUR_IP:8000`

### Option 2: Using Hostname

If your Synology has a hostname:
```
http://your-nas-name.local:8000
```

### Option 3: Using QuickConnect (Not Recommended)

QuickConnect URLs work but may be slower:
```
http://quickconnect.to/your-id:8000
```

### Option 4: Using Custom Domain (Recommended for External Access)

If you've set up a reverse proxy with SSL:
```
https://funda.yourdomain.com
```

---

## Network Requirements

### Same Network (LAN)
✅ **Nothing to configure** - Extension can reach Synology directly

### Different Network (External Access)
You need ONE of these:

1. **Port Forwarding** on your router (port 8000 → Synology IP)
2. **VPN** to your home network (most secure)
3. **Reverse Proxy** with SSL certificate (recommended)

See: [Synology Deployment Guide - External Access](SYNOLOGY_DEPLOYMENT.md#accessing-from-outside-your-network)

---

## Usage

1. **Navigate to a Funda property page**  
   Example: `https://www.funda.nl/koop/amsterdam/...`

2. **Click the extension icon**  
   The popup shows "Woning Gevonden" ✅

3. **Choose action:**
   - **"Start Analyse"** - Extract all data and create a full report
   - **"Foto's Exporteren"** - Export photo gallery only

4. **Wait for "Succes!"**  
   Click the success message to open the report dashboard

---

## Troubleshooting

### Extension Not Working on Funda Page

**Problem:** Extension shows "Geen Funda Pagina"

**Solution:** 
- You're not on a Funda property page
- Navigate to an actual property listing
- Refresh the page and try again

---

### "Verbinding mislukt: Check instellingen"

**Problem:** Extension can't connect to server

**Solutions:**

1. **Verify server is running:**
   ```bash
   curl http://YOUR_SERVER_URL:8000/health
   ```
   Should return: `{"status":"ok"}`

2. **Check firewall:**
   - Synology: **Control Panel** → **Security** → **Firewall**
   - Add rule to allow port 8000

3. **Verify URL in settings:**
   - Right-click extension → Options
   - Test connection (green checkmark = good)

4. **Check CORS settings** (if using custom domain):
   - Server must allow browser requests
   - Our default config allows all origins (`*`)

---

### Extension Permissions Warning

**Question:** Why does it need "access to data on all websites"?

**Answer:** 
- The extension needs to connect to **your custom server URL**
- Since this could be any IP/domain, we request broad permissions
- The extension **only** runs on `funda.nl` and your configured server
- Code is open source - you can inspect `extension/` folder

---

## Version Compatibility

### Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 88+ | ✅ Fully Supported |
| Edge | 88+ | ✅ Fully Supported |
| Brave | 1.20+ | ✅ Fully Supported |
| Opera | 74+ | ⚠️ Not Tested |
| Firefox | - | ❌ Not Supported (Manifest V3) |

### API Server Compatibility

| Server Type | Status |
|------------|--------|
| Local (localhost) | ✅ Default |
| LAN Server (192.168.x.x) | ✅ Supported |
| Synology NAS | ✅ Supported |
| Docker Container | ✅ Supported |
| Reverse Proxy (HTTPS) | ✅ Supported |

---

## Security Best Practices

### For External Access (Internet)

1. **Use HTTPS** (reverse proxy with SSL certificate)
2. **Add authentication** (Synology reverse proxy supports this)
3. **Use VPN** instead of port forwarding
4. **Whitelist your IP** if using port forwarding

### For LAN Access

1. **Keep Synology DSM updated**
2. **Use strong passwords** for DSM accounts
3. **Enable 2FA** on Synology

---

## Updating the Extension

When you pull new code from GitHub:

1. Go to `chrome://extensions/`
2. Find "Multi-Check Pro Link"
3. Click **🔄 Reload** button
4. Done! Extension is updated

---

## Development Mode

To modify the extension:

1. Edit files in `extension/` folder
2. Go to `chrome://extensions/`
3. Click **🔄 Reload** on the extension
4. Test your changes

---

## Common Issues

### "Extension is not available on the Chrome Web Store"

**This is normal!** This is a private extension. You must:
- Keep "Developer mode" enabled
- We don't publish to Chrome Web Store (it's for personal use)

### Extension Disabled After Browser Restart

**Chrome sometimes disables unpacked extensions.**

**Solutions:**
1. Re-enable it in `chrome://extensions/`
2. OR: Package as `.crx` file for permanent installation
3. OR: Load from source each time (keeps DEV features)

### Settings Not Saving

**Clear storage and try again:**
```javascript
// In browser console (F12):
chrome.storage.sync.clear(() => console.log("Cleared"));
```

Then reconfigure settings.

---

## Advanced: Custom Domain Setup

If you want to use the extension from anywhere with HTTPS:

### 1. Set Up DDNS
- Synology: **Control Panel** → **External Access** → **DDNS**

### 2. Configure Reverse Proxy
- **Control Panel** → **Login Portal** → **Advanced** → **Reverse Proxy**
- Source: `https://funda.yourdomain.com`
- Destination: `http://localhost:8000`

### 3. Add SSL Certificate
- **Control Panel** → **Security** → **Certificate**
- Use Let's Encrypt (free)

### 4. Configure Extension
- Extension settings: `https://funda.yourdomain.com`

### 5. Port Forwarding (Router)
- Forward port `443` → Synology IP port `443`

---

## Need Help?

- **Server issues**: See [Synology Deployment Guide](SYNOLOGY_DEPLOYMENT.md)
- **API errors**: Check server logs with `docker compose logs app`
- **Network issues**: Test with `curl http://YOUR_SERVER:8000/health`

---

## Privacy & Data

**What data does the extension collect?**
- Nothing! All data goes directly from Funda → Your server
- No analytics, no tracking, no external services
- Everything stays in your control

**Where is data stored?**
- On your server/NAS only
- Chrome storage: Only API URL setting
- No cloud services involved
