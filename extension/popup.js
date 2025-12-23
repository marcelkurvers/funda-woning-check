document.addEventListener('DOMContentLoaded', () => {
    const btnAnalyze = document.getElementById('btn-analyze');
    const statusType = document.getElementById('page-type');
    const msg = document.getElementById('msg');
    const statusDot = document.createElement('span'); // Create a dot for visual indicator 

    // Insert the dot before the status text
    statusDot.style.display = 'inline-block';
    statusDot.style.width = '8px';
    statusDot.style.height = '8px';
    statusDot.style.borderRadius = '50%';
    statusDot.style.marginRight = '8px';
    statusType.parentNode.insertBefore(statusDot, statusType);

    const colors = {
        red: '#ef4444',    // Error / No Funda
        yellow: '#eab308', // Funda found (general)
        blue: '#3b82f6',   // Property found / Processing
        green: '#22c55e',  // Success
        white: '#f8fafc'
    };

    function setStatus(text, colorKey) {
        statusType.textContent = text;
        statusType.style.color = colors[colorKey];
        statusDot.style.backgroundColor = colors[colorKey];
        statusDot.style.boxShadow = `0 0 8px ${colors[colorKey]}`;
    }

    // 1. Initial check: are we on Funda?
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const url = tabs[0].url;
        if (url && url.includes('funda.nl')) {
            if (url.includes('/koop/') || url.includes('/huur/') || url.includes('/foto/') || url.includes('/media/') || url.includes('/overzicht/')) {
                setStatus("Woning Gevonden", 'blue');
                btnAnalyze.disabled = false;
            } else {
                setStatus("Funda Gevonden", 'yellow');
                btnAnalyze.disabled = true; // Still require listing page for full analysis
            }
        } else {
            setStatus("Geen Funda Pagina", 'red');
            btnAnalyze.disabled = true;
        }
    });

    btnAnalyze.addEventListener('click', () => {
        processAction('extract_all');
    });

    function processAction(action) {
        msg.textContent = "Verbinding maken...";
        msg.style.display = "block";
        msg.style.color = colors.blue;

        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const activeTab = tabs[0];
            if (!activeTab) return;

            // Ensure content script is ready
            chrome.tabs.sendMessage(activeTab.id, { action: "ping" }, (pingResp) => {
                if (chrome.runtime.lastError) {
                    msg.textContent = "Fout: Vernieuw de Funda pagina.";
                    msg.style.color = colors.red;
                    return;
                }

                msg.textContent = "Data verzamelen...";
                chrome.tabs.sendMessage(activeTab.id, { action }, (response) => {
                    if (chrome.runtime.lastError || !response) {
                        msg.textContent = "Fout bij extraheren.";
                        msg.style.color = colors.red;
                        return;
                    }
                    sendToBackend(response);
                });
            });
        });
    }

    async function sendToBackend(data) {
        if (data.logs) {
            displayLogs(data.logs);
        }

        msg.textContent = "Verzenden naar Multi-Check Pro...";

        // Get API URL from settings (default to localhost)
        const settings = await chrome.storage.sync.get(['apiUrl']);
        const apiUrl = (settings.apiUrl || 'http://localhost:8000').replace(/\/$/, '');

        try {
            const resp = await fetch(`${apiUrl}/api/extension/ingest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (resp.ok) {
                const result = await resp.json();
                msg.textContent = "Succes! Rapport wordt geopend...";
                msg.style.color = colors.green;
                setStatus("Analyse Voltooid", 'green');

                // Auto-open in new tab
                setTimeout(() => {
                    chrome.tabs.create({ url: `${apiUrl}/runs/${result.run_id}/status` });
                }, 800);
            } else {
                const errData = await resp.json().catch(() => ({}));
                msg.textContent = "Fout: " + (errData.detail || resp.status);
                msg.style.color = colors.red;
            }
        } catch (e) {
            msg.textContent = "Verbinding mislukt: Check instellingen";
            msg.style.color = colors.red;
        }
    }

    function displayLogs(logs) {
        const logBox = document.getElementById('log-box');
        if (!logBox) return;
        logBox.style.display = 'block';
        logBox.innerHTML = '<div style="font-weight:bold; border-bottom:1px solid #475569; margin-bottom:4px; padding-bottom:2px;">Activiteitslog:</div>';

        logs.forEach(msg => {
            const div = document.createElement('div');
            div.textContent = msg;
            div.style.padding = '1px 0';
            logBox.appendChild(div);
        });
    }
});
