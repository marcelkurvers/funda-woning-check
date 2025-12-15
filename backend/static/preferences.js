const API_URL = '/api/preferences';

// Utility: Format currency
const formatCurrency = (val) => {
    return new Intl.NumberFormat('nl-NL', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(val);
};

// State Management
let currentPrefs = {
    shared: { budget: 650000, area: 120, region: "", energyLabels: [] },
    marcel: { priorities: [], notes: "" },
    petra: { priorities: [], notes: "" }
};

// UI Elements
const els = {
    budget: document.getElementById('in-budget'),
    budgetDisp: document.getElementById('disp-budget'),
    area: document.getElementById('in-area'),
    areaDisp: document.getElementById('disp-area'),
    region: document.getElementById('in-region'),
    marcelNotes: document.getElementById('in-marcel-notes'),
    petraNotes: document.getElementById('in-petra-notes'),
    btnSave: document.getElementById('btn-save'),
    options: document.querySelectorAll('.option-btn')
};

// Initialize
async function init() {
    setupListeners();
    await loadPreferences();
    updateDisplays();
}

function setupListeners() {
    // Sliders
    if (els.budget) els.budget.addEventListener('input', (e) => {
        els.budgetDisp.textContent = formatCurrency(e.target.value);
        if (e.target.value >= 1000000) els.budgetDisp.textContent = "€ 1.0M+";
    });

    if (els.area) els.area.addEventListener('input', (e) => {
        els.areaDisp.textContent = `${e.target.value} m²`;
    });

    // Option Buttons
    els.options.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('active');
        });
    });

    // Save Button
    if (els.btnSave) els.btnSave.addEventListener('click', savePreferences);
}

function updateDisplays() {
    if (els.budget) els.budgetDisp.textContent = formatCurrency(els.budget.value);
    if (els.area) els.areaDisp.textContent = `${els.area.value} m²`;
}

// Data Handling
function getActiveOptions(group) {
    return Array.from(document.querySelectorAll(`.option-btn[data-group="${group}"].active`))
        .map(el => el.dataset.val);
}

function setActiveOptions(group, values) {
    if (!values) return;
    document.querySelectorAll(`.option-btn[data-group="${group}"]`).forEach(btn => {
        if (values.includes(btn.dataset.val)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

function collectData() {
    return {
        shared: {
            budget: els.budget ? parseInt(els.budget.value) : 650000,
            area: els.area ? parseInt(els.area.value) : 120,
            region: els.region ? els.region.value : "",
            energyLabels: getActiveOptions('energy')
        },
        marcel: {
            priorities: getActiveOptions('marcel-prio'),
            notes: els.marcelNotes ? els.marcelNotes.value : ""
        },
        petra: {
            priorities: getActiveOptions('petra-prio'),
            notes: els.petraNotes ? els.petraNotes.value : ""
        }
    };
}

async function loadPreferences() {
    try {
        const res = await fetch(API_URL);
        const data = await res.json();

        if (data && Object.keys(data).length > 0) {
            currentPrefs = data;

            // Populate UI
            if (data.shared) {
                if (els.budget) els.budget.value = data.shared.budget || 650000;
                if (els.area) els.area.value = data.shared.area || 120;
                if (els.region) els.region.value = data.shared.region || "";
                setActiveOptions('energy', data.shared.energyLabels);
            }
            if (data.marcel) {
                if (els.marcelNotes) els.marcelNotes.value = data.marcel.notes || "";
                setActiveOptions('marcel-prio', data.marcel.priorities);
            }
            if (data.petra) {
                if (els.petraNotes) els.petraNotes.value = data.petra.notes || "";
                setActiveOptions('petra-prio', data.petra.priorities);
            }
        }
    } catch (e) {
        console.error("Failed to load preferences", e);
    }
}

async function savePreferences() {
    const btn = els.btnSave;
    const originalText = btn.innerHTML;
    btn.innerHTML = 'Opslaan...';
    btn.disabled = true;

    const payload = collectData();

    try {
        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            btn.style.background = '#10b981'; // Green
            btn.innerHTML = 'Opgeslagen!';
        } else {
            btn.style.background = '#ef4444'; // Red
            btn.innerHTML = 'Fout';
        }
    } catch (e) {
        btn.style.background = '#ef4444';
        btn.innerHTML = 'Netwerk Fout';
    }

    setTimeout(() => {
        btn.style.background = '';
        btn.innerHTML = originalText;
        btn.disabled = false;
    }, 2000);
}

// Start
document.addEventListener('DOMContentLoaded', init);
