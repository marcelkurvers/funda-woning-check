document.addEventListener('DOMContentLoaded', () => {
    const btnAnalyze = document.getElementById('btn-analyze');
    const btnPhotos = document.getElementById('btn-photos');
    const statusType = document.getElementById('page-type');
    const msg = document.getElementById('msg');

    // 1. Initial check: are we on Funda?
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const url = tabs[0].url;
        if (url && url.includes('funda.nl')) {
            statusType.textContent = "Funda Gevonden";
            if (url.includes('/koop/') || url.includes('/huur/') || url.includes('/foto/') || url.includes('/media/') || url.includes('/overzicht/')) {
                statusType.textContent = "Woning Gevonden";
                btnAnalyze.disabled = false;
                btnPhotos.disabled = false;
                btnPhotos.style.opacity = "1";
            } else {
                btnPhotos.disabled = true;
                btnPhotos.title = "Alleen beschikbaar op een woning-pagina";
            }
        } else {
            statusType.textContent = "Geen Funda Pagina";
            btnAnalyze.disabled = true;
            btnPhotos.disabled = true;
        }
    });

    btnAnalyze.addEventListener('click', () => {
        processAction('extract_all');
    });

    btnPhotos.addEventListener('click', () => {
        processAction('get_photos');
    });

    function processAction(action) {
        msg.textContent = "Verbinding maken...";
        msg.style.display = "block";
        msg.style.color = "#f8fafc";

        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const activeTab = tabs[0];
            if (!activeTab) return;

            // Ensure content script is ready
            chrome.tabs.sendMessage(activeTab.id, { action: "ping" }, (pingResp) => {
                if (chrome.runtime.lastError) {
                    msg.textContent = "Fout: Vernieuw de Funda pagina.";
                    msg.style.color = "#fb7185";
                    return;
                }

                msg.textContent = "Data verzamelen...";
                chrome.tabs.sendMessage(activeTab.id, { action }, (response) => {
                    if (chrome.runtime.lastError || !response) {
                        msg.textContent = "Fout bij extraheren.";
                        msg.style.color = "#fb7185";
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
        try {
            const resp = await fetch("http://localhost:8000/api/extension/ingest", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (resp.ok) {
                const result = await resp.json();
                msg.textContent = "Succes! Klik om dashboard te openen.";
                msg.style.color = "#4ade80";
                msg.style.cursor = "pointer";
                msg.className = "hover:underline";

                msg.onclick = () => {
                    window.open(`http://localhost:8000/runs/${result.run_id}/status`, '_blank');
                };
            } else {
                const errData = await resp.json().catch(() => ({}));
                msg.textContent = "Fout: " + (errData.detail || resp.status);
                msg.style.color = "#fb7185";
            }
        } catch (e) {
            msg.textContent = "Verbinding mislukt: Draait de backend?";
            msg.style.color = "#fb7185";
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
