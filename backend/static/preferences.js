// Use backend API
const API_URL = '/api/preferences';

function getActiveTags(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    return Array.from(container.querySelectorAll('.tag-item.active'))
        .map(el => el.textContent.trim());
}

function setActiveTags(containerId, activeTags) {
    const container = document.getElementById(containerId);
    if (!container || !activeTags) return;
    container.querySelectorAll('.tag-item').forEach(el => {
        if (activeTags.includes(el.textContent.trim())) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });
}

const btnSave = document.getElementById('btn-save');
if (btnSave) {
    btnSave.addEventListener('click', async () => {
        const btn = document.getElementById('btn-save');
        const originalText = btn.innerHTML;
        btn.innerHTML = 'Opslaan...';

        // Collect data
        const preferences = {
            shared: {
                budget: document.getElementById('shared-budget') ? document.getElementById('shared-budget').value : "",
                area: document.getElementById('shared-area') ? document.getElementById('shared-area').value : "",
                region: document.getElementById('shared-region') ? document.getElementById('shared-region').value : "",
                bedrooms: document.getElementById('shared-bedrooms') ? document.getElementById('shared-bedrooms').value : "",
                energyLabels: getActiveTags('shared-energy-group')
            },
            marcel: {
                priorities: getActiveTags('marcel-tags'),
                notes: document.getElementById('marcel-notes') ? document.getElementById('marcel-notes').value : ""
            },
            petra: {
                priorities: getActiveTags('petra-tags'),
                notes: document.getElementById('petra-notes') ? document.getElementById('petra-notes').value : ""
            }
        };

        try {
            const res = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(preferences)
            });
            if (res.ok) {
                btn.style.background = '#10b981';
                btn.innerHTML = `<ion-icon name="checkmark-outline" style="font-size: 1.2rem; vertical-align: text-bottom; margin-right: 0.5rem;"></ion-icon> Opgeslagen!`;
            } else {
                btn.style.background = '#ef4444';
                btn.innerText = 'Fout!';
            }
        } catch (e) {
            console.error(e);
            btn.style.background = '#ef4444';
            btn.innerText = 'Netwerk Fout!';
        }

        setTimeout(() => {
            btn.style.background = '';
            btn.innerHTML = originalText;
        }, 2000);
    });
}

// Load if exists
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await fetch(API_URL);
        const p = await res.json();

        if (p && Object.keys(p).length > 0) {
            // Shared
            if (p.shared) {
                if (p.shared.budget && document.getElementById('shared-budget')) document.getElementById('shared-budget').value = p.shared.budget;
                if (p.shared.area && document.getElementById('shared-area')) document.getElementById('shared-area').value = p.shared.area;
                if (p.shared.region && document.getElementById('shared-region')) document.getElementById('shared-region').value = p.shared.region;
                if (p.shared.bedrooms && document.getElementById('shared-bedrooms')) document.getElementById('shared-bedrooms').value = p.shared.bedrooms;
                if (p.shared.energyLabels) setActiveTags('shared-energy-group', p.shared.energyLabels);
            }
            // Marcel
            if (p.marcel) {
                if (p.marcel.priorities) setActiveTags('marcel-tags', p.marcel.priorities);
                if (p.marcel.notes && document.getElementById('marcel-notes')) document.getElementById('marcel-notes').value = p.marcel.notes;
            }
            // Petra
            if (p.petra) {
                if (p.petra.priorities) setActiveTags('petra-tags', p.petra.priorities);
                if (p.petra.notes && document.getElementById('petra-notes')) document.getElementById('petra-notes').value = p.petra.notes;
            }
        }
    } catch (e) {
        console.error("Could not load preferences", e);
    }
});
