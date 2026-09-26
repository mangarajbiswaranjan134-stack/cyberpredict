// CYBERPREDICT: Master Command Center Client Application Controller (10/10 SIH PS Aligned)
const state = {
    activeTab: 'overview',
    activeHorizon: '24h',
    currentUser: null,
    hotspots: [],
    complaintsSummary: null,
    alerts: [],
    selectedHotspot: null,
    selectedAlertForFeedback: null,
    globalSearchQuery: ''
};

document.addEventListener('DOMContentLoaded', async () => {
    initTabs();
    initHorizonSelectors();
    initMapLayerToggles();
    window.initCharts();
    window.initGisMaps();
    initWebSocket();
    await loadInitialSession();
    await loadDashboardData();
    setupGlobalSearch();
});

// Navigation Tab Management
function initTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.getAttribute('data-tab');
            switchTab(target);
        });
    });
}

function animateCounter(element, target, prefix = '', suffix = '', duration = 800) {
    if (!element) return;
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        element.innerText = `${prefix}${typeof target === 'number' ? target.toLocaleString('en-IN') : target}${suffix}`;
        return;
    }
    const targetNum = typeof target === 'number' ? target : parseFloat(target) || 0;
    const start = 0;
    const startTime = performance.now();
    const isFloat = !Number.isInteger(targetNum);

    function step(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        const currentVal = start + (targetNum - start) * ease;

        if (isFloat) {
            element.innerText = `${prefix}${currentVal.toFixed(1)}${suffix}`;
        } else {
            element.innerText = `${prefix}${Math.round(currentVal).toLocaleString('en-IN')}${suffix}`;
        }

        if (progress < 1) {
            requestAnimationFrame(step);
        }
    }
    requestAnimationFrame(step);
}

function switchTab(tabId) {
    state.activeTab = tabId;
    
    document.querySelectorAll('.nav-tab').forEach(t => {
        if (t.getAttribute('data-tab') === tabId) {
            t.classList.add('active', 'text-red-600', 'font-bold');
            t.classList.remove('text-slate-600');
        } else {
            t.classList.remove('active', 'text-red-600', 'font-bold');
            t.classList.add('text-slate-600');
        }
    });

    document.querySelectorAll('.tab-view').forEach(view => {
        if (view.id === `view-${tabId}`) {
            view.classList.remove('hidden');
        } else {
            view.classList.add('hidden');
        }
    });

    if (tabId === 'overview') {
        setTimeout(() => { if (gisMap) gisMap.invalidateSize(); }, 150);
    } else if (tabId === 'gis') {
        setTimeout(() => { 
            if (fullGisMap) fullGisMap.invalidateSize(); 
            loadFullGisData();
        }, 150);
    } else if (tabId === 'predictions') {
        loadPredictionsTab();
    } else if (tabId === 'alerts') {
        loadAlertsTab();
    } else if (tabId === 'bank') {
        loadBankTab();
    } else if (tabId === 'audit') {
        loadAuditTab();
    } else if (tabId === 'investigations') {
        loadInvestigationsTab();
    } else if (tabId === 'financial') {
        loadFinancialTab();
    } else if (tabId === 'crime-patterns') {
        loadCrimePatternsTab();
    } else if (tabId === 'emergency') {
        loadEmergencyTab();
    } else if (tabId === 'reports') {
        loadReportsTab();
    } else if (tabId === 'system') {
        loadSystemTab();
    } else if (tabId === 'complaints') {
        loadComplaintsTab(1);
    } else if (tabId === 'stitch') {
        if (window.loadStitchGraph) window.loadStitchGraph(document.getElementById('stitch-case-selector')?.value || 'CYB-2026-004821');
    } else if (tabId === 'copilot') {
        const input = document.getElementById('copilot-chat-input');
        if (input) setTimeout(() => input.focus(), 150);
    } else if (tabId === 'settings') {
        loadSettingsTab();
    }
}

// Multi-Horizon Advance Forecasting Controls
function initHorizonSelectors() {
    const pills = document.querySelectorAll('.horizon-pill');
    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            const h = pill.getAttribute('data-horizon');
            setAdvanceHorizon(h);
        });
    });
}

function setAdvanceHorizon(horizon) {
    state.activeHorizon = horizon;
    document.querySelectorAll('.horizon-pill').forEach(p => {
        if (p.getAttribute('data-horizon') === horizon) {
            p.classList.add('active', 'bg-red-600', 'text-white');
            p.classList.remove('text-slate-400');
        } else {
            p.classList.remove('active', 'bg-red-600', 'text-white');
            p.classList.add('text-slate-400');
        }
    });

    const labelEl = document.getElementById('current-horizon-label');
    if (labelEl) {
        labelEl.innerText = horizon === '1h' ? 'Next 1 Hour' : `Next ${horizon.replace('h', ' Hours')}`;
    }

    loadDashboardData();
}

// Map Layer Checkbox Toggles
function initMapLayerToggles() {
    const checkPredicted = document.getElementById('toggle-layer-predicted');
    const checkHistorical = document.getElementById('toggle-layer-historical');
    const checkCorridors = document.getElementById('toggle-layer-corridors');

    if (checkPredicted) {
        checkPredicted.addEventListener('change', (e) => {
            window.toggleMapLayer('predicted', e.target.checked);
        });
    }
    if (checkHistorical) {
        checkHistorical.addEventListener('change', (e) => {
            window.toggleMapLayer('historical', e.target.checked);
        });
    }
    if (checkCorridors) {
        checkCorridors.addEventListener('change', (e) => {
            window.toggleMapLayer('corridors', e.target.checked);
        });
    }
}

// Session & RBAC with Real JWT Authentication
function getAuthHeaders() {
    const token = localStorage.getItem('cp_jwt_token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

async function loadInitialSession() {
    try {
        let token = localStorage.getItem('cp_jwt_token');
        if (!token) {
            // Auto-login with default administrator credentials on initial launch
            const loginRes = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: 'admin@i4c.gov.in', password: 'Admin@2026' })
            });
            const loginData = await loginRes.json();
            if (loginData.access_token) {
                token = loginData.access_token;
                localStorage.setItem('cp_jwt_token', token);
                state.currentUser = loginData.user;
            }
        } else {
            const meRes = await fetch('/api/auth/me', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (meRes.ok) {
                const meData = await meRes.json();
                state.currentUser = meData.user;
            } else {
                localStorage.removeItem('cp_jwt_token');
                await loadInitialSession();
                return;
            }
        }
        updateUserDisplay();
    } catch (err) {
        console.error("Auth error:", err);
    }
}

function updateUserDisplay() {
    const userRoleEl = document.getElementById('user-role-badge');
    const userJurisdictionEl = document.getElementById('user-jurisdiction');
    const headerNameEl = document.getElementById('header-officer-name');

    if (state.currentUser) {
        if (headerNameEl) headerNameEl.innerText = state.currentUser.name;
        if (userRoleEl) userRoleEl.innerText = state.currentUser.name;
        if (userJurisdictionEl) {
            userJurisdictionEl.innerText = `Jurisdiction: ${state.currentUser.jurisdiction} • ID: ${state.currentUser.badge}`;
        }
    }
}

function populateRoleDropdown(roles) {
    const select = document.getElementById('role-selector');
    if (!select) return;
    select.innerHTML = '';
    roles.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r.role_id;
        opt.innerText = r.name;
        if (state.currentUser && r.role_id === state.currentUser.role_id) opt.selected = true;
        select.appendChild(opt);
    });

    select.addEventListener('change', async (e) => {
        const roleId = e.target.value;
        const res = await fetch('/api/auth/switch-role', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role_id: roleId })
        });
        const data = await res.json();
        if (data.status === 'success') {
            state.currentUser = data.current_user;
            updateUserDisplay();
            showNotificationToast(`Security Context Updated: ${data.current_user.name}`, 'info');
        }
    });
}

// Main Dashboard Data Loader
async function loadDashboardData() {
    try {
        const [complaintsRes, hotspotsRes, alertsRes, forecastRes] = await Promise.all([
            fetch('/api/complaints/summary'),
            fetch(`/api/hotspots/?horizon=${state.activeHorizon}`),
            fetch('/api/alerts/'),
            fetch(`/api/predictions/forecast?horizon=${state.activeHorizon}`)
        ]);

        const compData = await complaintsRes.json();
        const hotData = await hotspotsRes.json();
        const alertData = await alertsRes.json();
        const foreData = await forecastRes.json();

        state.complaintsSummary = compData;
        state.hotspots = foreData.predictions || [];
        state.alerts = alertData.alerts || [];
        window.lastHotspotData = hotData;

        // Update KPI Cards
        updateKpiCards(compData, foreData, alertData);

        // Render Multi-Layer GIS Map
        window.renderMapLayers(hotData, 'overview');

        // Render Top Predicted Hotspots List
        renderTopHotspotsList(state.hotspots);

        // Render Live Alerts List in Overview
        renderOverviewAlertsList(state.alerts);

        // Render Temporal Interval Curve
        const metricsRes = await fetch('/api/predictions/metrics');
        const metricsData = await metricsRes.json();
        if (metricsData.temporal_forecast_curve) {
            window.renderTemporalChart(metricsData.temporal_forecast_curve);
        }

        // Select Top Hotspot by default
        if (state.hotspots.length > 0) {
            selectHotspotById(state.hotspots[0].cluster_id);
        }

    } catch (err) {
        console.error("Dashboard data load failed:", err);
    }
}

function updateKpiCards(compData, foreData, alertData) {
    const elComplaints = document.getElementById('kpi-total-complaints');
    const elHighRisk = document.getElementById('kpi-high-risk');
    const elHotspots = document.getElementById('kpi-predicted-hotspots');
    const elExposure = document.getElementById('kpi-potential-exposure');
    const elTxns = document.getElementById('kpi-forecasted-txns');
    const elAlerts = document.getElementById('kpi-alerts-generated');
    const elInterventions = document.getElementById('kpi-interventions');
    const elOpportunity = document.getElementById('kpi-prevention-opp');

    if (elComplaints) animateCounter(elComplaints, compData.total_complaints || 5200);
    if (elHighRisk) animateCounter(elHighRisk, (compData.by_risk?.CRITICAL || 0) + (compData.by_risk?.HIGH || 0));
    if (elHotspots) animateCounter(elHotspots, foreData.total_hotspots_monitored || 12);
    if (elExposure) animateCounter(elExposure, foreData.total_estimated_exposure_crores || 18.7, '₹', ' Cr');
    if (elTxns) animateCounter(elTxns, foreData.total_estimated_transactions || 164, '', ' Txns');
    if (elAlerts) animateCounter(elAlerts, alertData.total || 12);
    if (elInterventions) elInterventions.innerText = "8 Active";
    if (elOpportunity) animateCounter(elOpportunity, ((foreData.total_estimated_exposure_crores || 18.7) * 0.45).toFixed(1), '₹', ' Cr');
}

function renderTopHotspotsList(hotspots) {
    const listEl = document.getElementById('top-hotspots-container');
    if (!listEl) return;

    listEl.innerHTML = '';
    hotspots.slice(0, 6).forEach((h) => {
        const item = document.createElement('div');
        const isCritical = h.risk_score >= 90;
        item.className = `p-3 mb-2 rounded-lg border cursor-pointer transition-all bg-white hover:bg-slate-50 border-slate-200 hover:border-red-400 shadow-sm`;
        item.innerHTML = `
            <div class="flex items-center justify-between mb-1">
                <span class="font-bold text-xs ${isCritical ? 'text-red-700 bg-red-50 border border-red-200' : 'text-amber-800 bg-amber-50 border border-amber-200'} font-mono px-1.5 py-0.5 rounded">
                    🔮 ${h.risk_level} (${h.risk_score}/100)
                </span>
                <span class="text-[10px] text-red-600 font-mono font-bold">🕒 ${h.forecast_window}</span>
            </div>
            <div class="text-sm font-bold text-slate-900">${h.name}</div>
            <div class="text-xs text-slate-500 mb-1.5">📍 ${h.locality}, ${h.district}</div>
            <div class="flex justify-between items-center text-[11px] text-slate-600 bg-slate-50 p-1.5 rounded border border-slate-100">
                <span>Exposure: <b class="text-red-600 font-bold">₹${h.estimated_exposure}L</b></span>
                <span>Txns: <b class="text-slate-900 font-semibold">${h.estimated_transactions || 18}</b></span>
                <span>Prob: <b class="text-slate-900 font-semibold">${Math.round(h.prediction_probability * 100)}%</b></span>
            </div>
        `;
        item.addEventListener('click', () => {
            selectHotspotById(h.cluster_id);
            if (window.zoomToHotspot) window.zoomToHotspot(h.lat, h.lng, 13);
        });
        listEl.appendChild(item);
    });
}

function renderOverviewAlertsList(alerts) {
    const container = document.getElementById('overview-alerts-feed');
    if (!container) return;

    container.innerHTML = '';
    alerts.slice(0, 5).forEach(a => {
        const item = document.createElement('div');
        const isCrit = a.risk_level === 'CRITICAL';
        item.className = 'p-2.5 mb-2 rounded border border-slate-200 bg-white hover:bg-slate-50 text-xs shadow-sm';
        item.innerHTML = `
            <div class="flex justify-between items-center mb-1">
                <span class="font-mono text-[10px] ${isCrit ? 'text-red-700 font-bold bg-red-50 border border-red-200' : 'text-orange-700 font-semibold bg-orange-50 border border-orange-200'} px-1.5 py-0.5 rounded">${a.id} • ${a.risk_level}</span>
                <span class="text-[10px] text-slate-400">${a.timestamp.split(' ')[1]}</span>
            </div>
            <div class="font-bold text-slate-900 mb-0.5">${a.title}</div>
            <div class="text-[11px] text-slate-500 line-clamp-1 mb-2">${a.predicted_event}</div>
            <div class="flex justify-between items-center">
                <span class="px-1.5 py-0.5 rounded text-[9px] font-bold ${
                    a.status === 'NEW' ? 'bg-red-50 text-red-700 border border-red-200' :
                    a.status === 'INTERVENTION ACTIVE' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                    a.status === 'RESOLVED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-700 border border-slate-200'
                }">${a.status}</span>
                <div class="space-x-1">
                    <button onclick="window.openFeedbackModal('${a.id}')" class="text-[10px] bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 px-2 py-0.5 rounded">
                        Log Outcome
                    </button>
                    <button onclick="window.openInterventionModal('${a.id}')" class="text-[10px] bg-red-600 hover:bg-red-700 text-white px-2 py-0.5 rounded font-medium shadow-sm">
                        Intervene
                    </button>
                </div>
            </div>
        `;
        container.appendChild(item);
    });
}

// Select Hotspot and Populate Explainable AI Drawer (9 Fields)
async function selectHotspotById(clusterId) {
    try {
        const res = await fetch(`/api/predictions/${clusterId}/explain?horizon=${state.activeHorizon}`);
        const data = await res.json();
        if (data.status === 'success') {
            state.selectedHotspot = data;
            renderExplainabilityPanel(data);
        }
    } catch (err) {
        console.error("Hotspot explain load error:", err);
    }
}

function renderExplainabilityPanel(data) {
    const titleEl = document.getElementById('xai-hotspot-name');
    const localityEl = document.getElementById('xai-hotspot-locality');
    const scoreEl = document.getElementById('xai-risk-score');
    const probEl = document.getElementById('xai-probability');
    const windowEl = document.getElementById('xai-window');
    const horizonEl = document.getElementById('xai-horizon');
    const summaryEl = document.getElementById('xai-rationale-summary');
    const factorsContainer = document.getElementById('xai-factors-container');
    const evidenceContainer = document.getElementById('xai-evidence-container');
    const interventionsContainer = document.getElementById('xai-recommended-interventions');
    const dispatchBtn = document.getElementById('btn-xai-dispatch-intervention');
    const emergencyBtn = document.getElementById('btn-xai-112-escalate');

    if (titleEl) titleEl.innerText = data.cluster_name;
    if (localityEl) localityEl.innerText = `📍 ${data.locality}, ${data.district}, ${data.state}`;
    if (scoreEl) {
        scoreEl.innerText = `${data.risk_score}/100`;
        scoreEl.className = `text-xl font-black font-mono ${data.risk_score >= 90 ? 'text-red-600' : 'text-amber-600'}`;
    }
    if (probEl) probEl.innerText = `${data.probability_pct}%`;
    if (windowEl) windowEl.innerText = data.forecast_window;
    if (horizonEl) horizonEl.innerText = `Horizon: ${data.forecast_horizon.toUpperCase()}`;
    if (summaryEl) summaryEl.innerText = data.rationale_summary;

    // Render Evidence Signals
    if (evidenceContainer && data.evidence_signals) {
        evidenceContainer.innerHTML = '';
        data.evidence_signals.forEach(sig => {
            const chip = document.createElement('div');
            chip.className = 'bg-slate-50 p-1.5 rounded border border-slate-200 text-[11px]';
            chip.innerHTML = `
                <div class="text-[9px] text-slate-500 font-semibold">${sig.label}</div>
                <div class="font-bold text-slate-900 font-mono">${sig.value}</div>
            `;
            evidenceContainer.appendChild(chip);
        });
    }

    // Render Exact 7 Contributing Factors with Progress Bars
    if (factorsContainer && data.factors) {
        factorsContainer.innerHTML = '';
        data.factors.forEach(f => {
            const row = document.createElement('div');
            row.className = 'p-2 rounded bg-slate-50 border border-slate-200 mb-1.5';
            row.innerHTML = `
                <div class="flex justify-between items-center mb-0.5">
                    <span class="text-xs font-bold text-slate-900">${f.factor_name}</span>
                    <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${
                        f.impact_level === 'CRITICAL' ? 'bg-red-50 text-red-700 border border-red-200' : 
                        f.impact_level === 'HIGH' ? 'bg-orange-50 text-orange-700 border border-orange-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                    }">
                        Weight: ${Math.round(f.contribution_weight * 100)}% • ${f.impact_level}
                    </span>
                </div>
                <div class="text-[11px] text-slate-600 mb-1 leading-tight">${f.description}</div>
                <div class="xai-meter-bg">
                    <div class="xai-meter-fill" style="width: ${Math.min(100, Math.round(f.contribution_weight * 380))}%;"></div>
                </div>
            `;
            factorsContainer.appendChild(row);
        });
    }

    // Render Recommended Actions
    if (interventionsContainer && data.recommended_interventions) {
        interventionsContainer.innerHTML = '';
        data.recommended_interventions.forEach(rec => {
            const li = document.createElement('li');
            li.className = 'text-xs text-slate-700 flex items-start space-x-1.5 mb-1';
            li.innerHTML = `<span class="text-red-600 font-bold">✓</span><span>${rec}</span>`;
            interventionsContainer.appendChild(li);
        });
    }

    if (dispatchBtn) dispatchBtn.onclick = () => window.openInterventionModal(data.hotspot_id);
    if (emergencyBtn) emergencyBtn.onclick = () => window.openEmergency112Modal(data.hotspot_id);
}

// Proactive Intervention Modal
function openInterventionModal(targetId) {
    const modal = document.getElementById('intervention-dispatch-modal');
    if (!modal) return;
    const targetEl = document.getElementById('modal-intervention-target');
    if (targetEl) targetEl.innerText = targetId || 'Active Threat Cluster';
    modal.classList.remove('hidden');
}

function closeInterventionModal() {
    const modal = document.getElementById('intervention-dispatch-modal');
    if (modal) modal.classList.add('hidden');
}

async function submitProactiveIntervention() {
    const typeSelect = document.getElementById('intervention-type-select');
    const notesInput = document.getElementById('intervention-operator-notes');
    const targetEl = document.getElementById('modal-intervention-target');

    const payload = {
        alert_id: targetEl ? targetEl.innerText : "ALT-TOP",
        intervention_type: typeSelect ? typeSelect.value : "LEA_PATROL",
        notes: notesInput ? notesInput.value : "Proactive rapid intervention dispatched."
    };

    try {
        const res = await fetch('/api/interventions/dispatch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
            closeInterventionModal();
            showNotificationToast(`🛡️ Proactive Intervention Dispatched: ${data.intervention.id}`, 'success');
            loadDashboardData();
        }
    } catch (err) {
        console.error("Intervention dispatch error:", err);
    }
}

// Incident Outcome & Feedback Loop Modal
function openFeedbackModal(alertId) {
    state.selectedAlertForFeedback = alertId;
    const modal = document.getElementById('feedback-outcome-modal');
    if (!modal) return;
    const alertIdEl = document.getElementById('modal-feedback-alert-id');
    if (alertIdEl) alertIdEl.innerText = alertId;
    modal.classList.remove('hidden');
}

function closeFeedbackModal() {
    const modal = document.getElementById('feedback-outcome-modal');
    if (modal) modal.classList.add('hidden');
}

async function submitIncidentFeedback() {
    const outcomeSelect = document.getElementById('feedback-outcome-type');
    const amountInput = document.getElementById('feedback-recovered-amount');
    const notesInput = document.getElementById('feedback-officer-notes');

    const payload = {
        alert_id: state.selectedAlertForFeedback || "ALT-2026-1001",
        outcome_type: outcomeSelect ? outcomeSelect.value : "INTERCEPTED_CONFIRMED",
        amount_recovered_inr: amountInput ? parseFloat(amountInput.value || 0) : 0.0,
        officer_notes: notesInput ? notesInput.value : "Incident confirmed and resolved by investigating officer."
    };

    try {
        const res = await fetch(`/api/alerts/${payload.alert_id}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
            closeFeedbackModal();
            showNotificationToast(`🔄 Feedback Logged: Incident ${payload.alert_id} resolved. AI Model weights updated!`, 'success');
            loadDashboardData();
        }
    } catch (err) {
        console.error("Feedback submission error:", err);
    }
}

// Bank / FI Tab Loader
async function loadBankTab() {
    try {
        const res = await fetch('/api/bank/dashboard');
        const data = await res.json();
        if (data.status === 'success') {
            const banksContainer = document.getElementById('bank-partners-container');
            if (banksContainer && data.partner_banks) {
                banksContainer.innerHTML = '';
                data.partner_banks.forEach(b => {
                    const card = document.createElement('div');
                    card.className = 'p-3.5 bg-white border border-slate-200 rounded-lg text-xs shadow-xs';
                    card.innerHTML = `
                        <div class="flex justify-between items-center mb-1">
                            <span class="font-bold text-sm text-slate-900">${b.bank_name}</span>
                            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200">${b.status}</span>
                        </div>
                        <div class="text-slate-600 mb-2">Nodal Contact: ${b.nodal_officer}</div>
                        <div class="grid grid-cols-2 gap-2 bg-slate-50 p-2 rounded text-[11px] mb-2 font-mono border border-slate-200">
                            <div>Hotspot ATMs: <b class="text-slate-900">${b.monitored_atms}</b></div>
                            <div>Risk Exposure: <b class="text-red-600">₹${b.estimated_cashout_risk_lakhs}L</b></div>
                        </div>
                        <button onclick="window.triggerSimulatedBankFreeze('${b.bank_name}')" 
                            class="w-full btn-primary-red py-1.5 rounded text-xs font-semibold">
                            Dispatch Simulated Mule Freeze Advisory
                        </button>
                    `;
                    banksContainer.appendChild(card);
                });
            }

            // Flagged Accounts Table
            const tbody = document.getElementById('bank-flagged-accounts-body');
            if (tbody && data.flagged_accounts) {
                tbody.innerHTML = '';
                data.flagged_accounts.forEach(acc => {
                    const tr = document.createElement('tr');
                    tr.className = 'border-b border-slate-200 text-xs hover:bg-slate-50';
                    tr.innerHTML = `
                        <td class="p-2.5 font-mono text-slate-900 font-bold">${acc.account}</td>
                        <td class="p-2.5 text-slate-800 font-medium">${acc.bank}</td>
                        <td class="p-2.5 text-orange-700 font-semibold">${acc.mule_layer}</td>
                        <td class="p-2.5 text-slate-600">${acc.cluster}</td>
                        <td class="p-2.5 font-mono text-red-600 font-semibold">₹${(acc.inflow).toLocaleString('en-IN')}</td>
                        <td class="p-2.5"><span class="px-2 py-0.5 rounded bg-red-50 text-red-700 text-[10px] font-semibold border border-red-200">${acc.status}</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        }
    } catch (err) {
        console.error("Bank tab error:", err);
    }
}

async function triggerSimulatedBankFreeze(bankName) {
    const payload = {
        account_number: `HDFCXXXXXX${Math.floor(1000 + Math.random() * 9000)}`,
        bank_name: bankName,
        mule_layer: "Layer 2",
        requested_by: state.currentUser ? state.currentUser.name : "Authorized Officer"
    };

    try {
        const res = await fetch('/api/bank/freeze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
            showNotificationToast(`🏦 Simulated Core Banking Hold: Placed on ${data.record.account_number} (${bankName}) in ${data.record.latency_ms}ms!`, 'success');
            loadBankTab();
        }
    } catch (err) {
        console.error("Bank freeze error:", err);
    }
}

// Global Audit Trail Tab Loader
async function loadAuditTab() {
    try {
        const res = await fetch('/api/audit/logs');
        const data = await res.json();
        const tbody = document.getElementById('audit-logs-table-body');
        if (!tbody || !data.logs) return;

        tbody.innerHTML = '';
        data.logs.forEach(log => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-slate-200 hover:bg-slate-50 text-xs';
            tr.innerHTML = `
                <td class="p-2.5 font-mono text-slate-900 font-bold">${log.id}</td>
                <td class="p-2.5 text-slate-500 font-mono">${log.timestamp}</td>
                <td class="p-2.5 text-slate-800 font-semibold">${log.actor}</td>
                <td class="p-2.5 font-mono text-red-700 font-semibold">${log.action}</td>
                <td class="p-2.5 font-mono text-slate-700">${log.target_id}</td>
                <td class="p-2.5 text-slate-600 leading-tight">${log.details}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Audit tab error:", err);
    }
}

// Predictive Intelligence Tab Loader
async function loadPredictionsTab() {
    try {
        const res = await fetch(`/api/predictions/forecast?horizon=${state.activeHorizon}`);
        const data = await res.json();
        const tbody = document.getElementById('predictions-table-body');
        if (!tbody || !data.predictions) return;

        tbody.innerHTML = '';
        data.predictions.forEach(p => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-slate-200 hover:bg-red-50/50 text-xs';
            tr.innerHTML = `
                <td class="p-3 font-semibold text-slate-900">${p.name}</td>
                <td class="p-3 text-slate-600">${p.district}, ${p.state}</td>
                <td class="p-3 font-mono font-bold ${p.risk_score >= 90 ? 'text-red-600' : 'text-orange-600'}">
                    ${p.risk_score}/100 (${p.risk_level})
                </td>
                <td class="p-3 font-mono text-red-700 font-semibold">${p.forecast_window}</td>
                <td class="p-3 font-mono text-slate-900 font-semibold">₹${p.estimated_exposure} Lakhs</td>
                <td class="p-3 font-mono text-slate-700">${Math.round(p.prediction_probability * 100)}%</td>
                <td class="p-3 text-slate-300">${p.primary_crime_category}</td>
                <td class="p-3">
                    <button onclick="window.selectHotspotById('${p.cluster_id}'); window.switchTab('overview');" 
                        class="btn-secondary-light px-2.5 py-1 text-xs font-semibold">
                        Inspect XAI
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        const metricRes = await fetch('/api/predictions/metrics');
        const metricData = await metricRes.json();
        if (metricData.feature_importance) {
            window.renderFeatureImportanceChart(metricData.feature_importance);
        }
    } catch (err) {
        console.error("Predictions tab error:", err);
    }
}

// Full GIS Map Loader
async function loadFullGisData() {
    try {
        const res = await fetch(`/api/hotspots/?horizon=${state.activeHorizon}`);
        const data = await res.json();
        window.renderMapLayers(data, 'full');
    } catch (err) {
        console.error("Full GIS load error:", err);
    }
}

// Alerts Tab Loader
async function loadAlertsTab() {
    try {
        const res = await fetch('/api/alerts/');
        const data = await res.json();
        const tbody = document.getElementById('alerts-table-body');
        if (!tbody || !data.alerts) return;

        tbody.innerHTML = '';
        data.alerts.forEach(a => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-slate-200 hover:bg-slate-50 text-xs';
            tr.innerHTML = `
                <td class="p-3 font-mono text-slate-900 font-semibold">${a.id}</td>
                <td class="p-3 text-slate-500">${a.timestamp}</td>
                <td class="p-3 font-bold ${a.risk_level === 'CRITICAL' ? 'text-red-700' : 'text-orange-700'}">${a.risk_level}</td>
                <td class="p-3 text-slate-900 font-medium">${a.title}</td>
                <td class="p-3 text-slate-700">${a.location}</td>
                <td class="p-3 font-mono text-red-600 font-semibold">₹${(a.estimated_exposure_inr / 100000).toFixed(1)}L</td>
                <td class="p-3">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold ${
                        a.status === 'NEW' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                        a.status === 'INTERVENTION ACTIVE' ? 'bg-amber-50 text-amber-800 border border-amber-200' :
                        a.status === 'RESOLVED' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-slate-100 text-slate-700 border border-slate-200'
                    }">${a.status}</span>
                </td>
                <td class="p-3 space-x-1">
                    <button onclick="window.openFeedbackModal('${a.id}')" 
                        class="btn-secondary-light px-2.5 py-1 text-xs">
                        Log Outcome
                    </button>
                    <button onclick="window.openInterventionModal('${a.id}')" 
                        class="btn-primary-red px-2.5 py-1 text-xs font-semibold">
                        Intervene
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Alerts tab error:", err);
    }
}

// Investigator Tab Loader
async function loadInvestigationsTab() {
    try {
        const res = await fetch('/api/investigations/CYB-2026-004821');
        const data = await res.json();
        if (data.status === 'success') {
            const c = data.case;
            const titleEl = document.getElementById('case-title');
            const amtEl = document.getElementById('case-total-fraud');
            const invEl = document.getElementById('case-lead-inv');
            const timelineContainer = document.getElementById('case-timeline-container');

            if (titleEl) titleEl.innerText = `${c.case_id} — ${c.title}`;
            if (amtEl) amtEl.innerText = `₹${(c.total_fraud_amount / 100000).toFixed(2)} Lakhs`;
            if (invEl) invEl.innerText = c.lead_investigator;

            if (timelineContainer && c.timeline) {
                timelineContainer.innerHTML = '';
                c.timeline.forEach(t => {
                    const item = document.createElement('div');
                    item.className = 'flex items-start space-x-2 text-xs border-l-2 border-red-600 pl-3 py-1 mb-2';
                    item.innerHTML = `
                        <span class="font-mono text-red-700 font-semibold">${t.time}</span>
                        <span class="text-slate-700">${t.event}</span>
                    `;
                    timelineContainer.appendChild(item);
                });
            }

            const graphRes = await fetch('/api/investigations/CYB-2026-004821/graph');
            const graphData = await graphRes.json();
            if (window.renderCaseNetworkGraph) {
                window.renderCaseNetworkGraph('case-network-container', graphData);
            }
        }
    } catch (err) {
        console.error("Investigations tab error:", err);
    }
}

function showNodeInspector(node) {
    const container = document.getElementById('node-inspector-panel');
    if (!container) return;

    container.classList.remove('hidden');
    container.innerHTML = `
        <div class="p-3 bg-white border border-slate-200 shadow-sm rounded-lg text-xs">
            <div class="flex justify-between items-center mb-1">
                <span class="font-bold text-red-700 uppercase">${node.rawType} NODE</span>
                <button onclick="document.getElementById('node-inspector-panel').classList.add('hidden')" class="text-slate-400 hover:text-slate-700 font-bold">✕</button>
            </div>
            <div class="font-semibold text-slate-900 text-sm mb-2">${node.label}</div>
            <pre class="bg-slate-50 border border-slate-200 p-2 rounded text-[11px] text-slate-800 font-mono overflow-x-auto">${JSON.stringify(node.rawDetails, null, 2)}</pre>
        </div>
    `;
}

// Financial Tab Loader
async function loadFinancialTab() {
    try {
        const res = await fetch('/api/financial/metrics');
        const data = await res.json();
        if (data.status === 'success') {
            document.getElementById('fin-total-reported').innerText = `₹${data.total_reported_crores} Cr`;
            document.getElementById('fin-recoverable').innerText = `₹${data.potentially_recoverable_crores} Cr`;
            document.getElementById('fin-blocked').innerText = `₹${data.blocked_amount_crores} Cr`;
            document.getElementById('fin-recovered').innerText = `₹${data.recovered_amount_crores} Cr`;

            if (window.renderFinancialFlowChart && data.flow_stages) {
                window.renderFinancialFlowChart(data.flow_stages);
            }
        }
    } catch (err) {
        console.error("Financial tab error:", err);
    }
}

// Crime Patterns Tab Loader
async function loadCrimePatternsTab() {
    try {
        const res = await fetch('/api/complaints/summary');
        const data = await res.json();
        if (data.by_category && window.renderCrimeCategoryChart) {
            window.renderCrimeCategoryChart(data.by_category);
        }
    } catch (err) {
        console.error("Crime patterns tab error:", err);
    }
}

// Emergency Tab Loader
async function loadEmergencyTab() {
    try {
        const [contactsRes, incidentsRes] = await Promise.all([
            fetch('/api/emergency/contacts'),
            fetch('/api/emergency/incidents')
        ]);
        const contactsData = await contactsRes.json();
        const incidentsData = await incidentsRes.json();

        const dirContainer = document.getElementById('emergency-directory-container');
        if (dirContainer && contactsData.directory) {
            dirContainer.innerHTML = '';
            contactsData.directory.forEach(d => {
                const item = document.createElement('div');
                item.className = 'p-3 bg-white border border-slate-200 rounded-lg text-xs shadow-xs';
                item.innerHTML = `
                    <div class="text-[10px] text-red-600 font-bold uppercase mb-0.5">${d.category}</div>
                    <div class="font-semibold text-slate-900 text-sm mb-1">${d.name}</div>
                    <div class="flex justify-between items-center text-slate-600 mb-1">
                        <span>Jurisdiction: ${d.jurisdiction}</span>
                        <span class="text-emerald-700 font-mono font-semibold">SLA: ${d.response_time_sla}</span>
                    </div>
                    <div class="font-mono text-slate-900 font-bold text-sm">📞 ${d.contact}</div>
                `;
                dirContainer.appendChild(item);
            });
        }

        const tbody = document.getElementById('emergency-incidents-body');
        if (tbody) {
            tbody.innerHTML = '';
            (incidentsData.incidents || []).forEach(inc => {
                const tr = document.createElement('tr');
                tr.className = 'border-b border-slate-200 text-xs hover:bg-slate-50';
                tr.innerHTML = `
                    <td class="p-2.5 font-mono text-red-700 font-bold">${inc.incident_id}</td>
                    <td class="p-2.5 text-slate-600">${inc.timestamp}</td>
                    <td class="p-2.5 text-slate-900 font-medium">${inc.location}</td>
                    <td class="p-2.5 text-slate-700">${inc.jurisdiction_lea}</td>
                    <td class="p-2.5"><span class="px-2 py-0.5 rounded bg-red-50 text-red-700 text-[10px] border border-red-200 font-semibold">${inc.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error("Emergency tab error:", err);
    }
}

// Reports Tab Loader
async function loadReportsTab() {
    try {
        const res = await fetch('/api/reports/brief');
        const data = await res.json();
        if (data.status === 'success') {
            const report = data.report;
            document.getElementById('report-generated-at').innerText = report.generated_at;
            document.getElementById('report-exec-summary').innerText = report.executive_summary;

            const actionsList = document.getElementById('report-actions-list');
            if (actionsList && report.recommended_strategic_actions) {
                actionsList.innerHTML = '';
                report.recommended_strategic_actions.forEach(act => {
                    const li = document.createElement('li');
                    li.className = 'text-xs text-slate-700 mb-1.5 flex items-start space-x-2';
                    li.innerHTML = `<span class="text-red-600 font-bold">▶</span><span>${act}</span>`;
                    actionsList.appendChild(li);
                });
            }
        }
    } catch (err) {
        console.error("Reports tab error:", err);
    }
}

// System Tab Loader
async function loadSystemTab() {
    try {
        const res = await fetch('/api/system/status');
        const data = await res.json();
        if (data.status === 'healthy') {
            const servicesContainer = document.getElementById('system-services-container');
            if (servicesContainer && data.services) {
                servicesContainer.innerHTML = '';
                data.services.forEach(s => {
                    const card = document.createElement('div');
                    card.className = 'p-3 bg-slate-900 border border-slate-800 rounded-lg flex items-center justify-between text-xs';
                    card.innerHTML = `
                        <div class="flex items-center space-x-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                            <span class="font-semibold text-slate-200">${s.service}</span>
                        </div>
                        <div class="flex items-center space-x-3 font-mono">
                            <span class="text-slate-400">${s.latency_ms} ms</span>
                            <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800">${s.status}</span>
                        </div>
                    `;
                    servicesContainer.appendChild(card);
                });
            }
        }
    } catch (err) {
        console.error("System tab error:", err);
    }
}

// Global Search
function setupGlobalSearch() {
    const input = document.getElementById('global-search-input');
    if (!input) return;

    let debounceTimer;
    input.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(async () => {
            const query = e.target.value.trim();
            if (query.length < 2) return;

            const res = await fetch(`/api/complaints/?search=${encodeURIComponent(query)}&limit=5`);
            const data = await res.json();
            if (data.data && data.data.length > 0) {
                showNotificationToast(`Found ${data.total} records matching "${query}". Top: ${data.data[0].id} (${data.data[0].victim_name})`, 'info');
            } else {
                showNotificationToast(`No records found for "${query}".`, 'warning');
            }
        }, 400);
    });
}

// ==========================================
// REAL-TIME WEBSOCKET PIPELINE & TELEMETRY
// ==========================================
let liveSocket = null;
let wsReconnectTimer = null;
let wsReconnectDelay = 2000;

function initWebSocket() {
    if (liveSocket && (liveSocket.readyState === WebSocket.OPEN || liveSocket.readyState === WebSocket.CONNECTING)) {
        return;
    }
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/live`;
    try {
        liveSocket = new WebSocket(wsUrl);
        liveSocket.onopen = () => {
            console.log("WebSocket telemetry active.");
            wsReconnectDelay = 2000;
            const dbBadge = document.getElementById('db-indicator-badge');
            if (dbBadge) {
                dbBadge.className = "bg-emerald-950/90 text-emerald-300 border border-emerald-600/70 text-[10px] font-bold px-2 py-0.5 rounded flex items-center space-x-1";
            }
        };
        liveSocket.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                handleLiveTelemetryMessage(msg);
            } catch (err) {
                console.warn("WebSocket parse error:", err);
            }
        };
        liveSocket.onclose = () => {
            console.log("WebSocket connection closed. Reconnecting in " + wsReconnectDelay + "ms...");
            clearTimeout(wsReconnectTimer);
            wsReconnectTimer = setTimeout(initWebSocket, wsReconnectDelay);
            wsReconnectDelay = Math.min(wsReconnectDelay * 1.5, 15000);
        };
        liveSocket.onerror = (err) => {
            console.warn("WebSocket connection notice:", err);
        };
    } catch (err) {
        console.warn("WebSocket initialization fallback:", err);
    }
}

function handleLiveTelemetryMessage(msg) {
    const eventType = msg.event || msg.type;
    const payload = msg.payload || msg.data || msg;

    if (eventType === 'COMPLAINT_CREATED') {
        // 1. Increment KPI counts dynamically
        const elComplaints = document.getElementById('kpi-total-complaints');
        if (elComplaints) {
            let current = parseInt(elComplaints.innerText.replace(/,/g, '')) || 5200;
            elComplaints.innerText = (current + 1).toLocaleString('en-IN');
        }

        const riskLvl = payload.risk_level || 'HIGH';
        if (riskLvl === 'CRITICAL' || riskLvl === 'HIGH') {
            const elHighRisk = document.getElementById('kpi-high-risk');
            if (elHighRisk) {
                let currHigh = parseInt(elHighRisk.innerText.replace(/,/g, '')) || 1480;
                elHighRisk.innerText = (currHigh + 1).toLocaleString('en-IN');
            }
        }

        // 2. Update Map Hotspot Marker without page reload
        if (payload.cluster_id && window.updateHotspotMarker) {
            window.updateHotspotMarker(payload.cluster_id, payload.recalculated_risk_score, payload.cluster_name);
        }

        // 3. Prepend Live Alert in Overview Feed
        if (payload.alert_created && payload.alert_details) {
            prependLiveAlert(payload.alert_details);
            const elAlerts = document.getElementById('kpi-alerts-generated');
            if (elAlerts) {
                let currAlerts = parseInt(elAlerts.innerText) || 12;
                elAlerts.innerText = currAlerts + 1;
            }
        }

        // 4. Trigger Toast Notification
        showNotificationToast(
            `⚡ [PostgreSQL Ingested] ${payload.complaint_id}: ₹${(payload.amount_lost_inr || 0).toLocaleString('en-IN')} ${payload.crime_category} in ${payload.district}. Cluster risk updated to ${payload.recalculated_risk_score}/100!`,
            riskLvl === 'CRITICAL' ? 'critical' : 'warning'
        );

        // 5. Update complaints tab if active
        if (state.activeTab === 'complaints') {
            loadComplaintsTab(currentComplaintsPage);
        }

        // 6. Update XAI drawer if selected hotspot matches
        if (state.selectedHotspot && state.selectedHotspot.cluster_id === payload.cluster_id) {
            selectHotspotById(payload.cluster_id);
        }

    } else if (eventType === 'SURGE_SIMULATED') {
        showNotificationToast("🚨 Cybercrime burst ingested! Advance predictive models updated.", "critical");
        if (state.activeTab === 'overview') loadDashboardData();
    } else if (eventType === 'INTERVENTION_DISPATCHED') {
        showNotificationToast(`🛡️ Intervention ${payload.id || ''} confirmed active in field.`, 'success');
        if (state.activeTab === 'overview') loadDashboardData();
    } else if (eventType === 'MULE_FREEZE_TRIGGERED') {
        showNotificationToast(`🏦 Core Banking Mule Account Hold Dispatched: ${payload.account_number || ''}`, 'warning');
        if (state.activeTab === 'bank') loadBankTab();
    } else if (eventType === 'EMERGENCY_ESCALATION') {
        showNotificationToast(`🚨 112 ERSS Emergency CAD Ticket Logged: ${payload.incident_id || ''}`, 'critical');
        if (state.activeTab === 'emergency') loadEmergencyTab();
    }
}

function prependLiveAlert(alert) {
    const container = document.getElementById('overview-alerts-feed');
    if (!container) return;

    const item = document.createElement('div');
    const isCrit = alert.risk_level === 'CRITICAL';
    item.className = 'p-3 mb-2 rounded border border-slate-200 bg-white hover:border-red-400 text-xs shadow-xs transition-all border-l-4 border-l-red-600';
    item.innerHTML = `
        <div class="flex justify-between items-center mb-1">
            <span class="font-mono text-[10px] ${isCrit ? 'text-red-700 font-bold' : 'text-orange-700 font-bold'}">${alert.id} • ${alert.risk_level}</span>
            <span class="text-[10px] text-red-600 font-semibold font-mono">JUST NOW</span>
        </div>
        <div class="font-bold text-slate-900 mb-0.5">${alert.title}</div>
        <div class="text-[11px] text-slate-600 line-clamp-1 mb-2">${alert.predicted_event || ''}</div>
        <div class="flex justify-between items-center">
            <span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-slate-100 text-slate-800 border border-slate-200">${alert.status || 'NEW'}</span>
            <div class="space-x-1">
                <button onclick="window.openFeedbackModal('${alert.id}')" class="btn-secondary-light text-[10px] px-2 py-0.5 rounded">
                    Log Outcome
                </button>
                <button onclick="window.openInterventionModal('${alert.id}')" class="btn-primary-red text-[10px] px-2 py-0.5 rounded font-medium">
                    Intervene
                </button>
            </div>
        </div>
    `;
    container.insertBefore(item, container.firstChild);
}

// ==========================================
// COMPLAINT ENTRY & PUBLIC REAL DATA GATEWAY
// ==========================================
function populateSampleComplaint(crimeType) {
    const samples = {
        'UPI Fraud': {
            name: "Rajesh Mohapatra",
            phone: "+91 98610 23412",
            city: "Bhubaneswar",
            category: "UPI Fraud",
            amount: 245000,
            lossType: "Direct Transfer",
            muleAccount: "HDFC0001928412",
            muleUpi: "instant.mule99@hdfc",
            ifsc: "HDFC0000060",
            state: "Odisha",
            district: "Khordha",
            lat: 20.3533,
            lng: 85.8266,
            synthetic: true
        },
        'Investment Scam': {
            name: "Dr. Sunita Patnaik",
            phone: "+91 94370 12988",
            city: "Cuttack",
            category: "Investment Scam",
            amount: 1850000,
            lossType: "Multi-Hop Mule",
            muleAccount: "SBIN0091240182",
            muleUpi: "securewealth.fund@sbi",
            ifsc: "SBIN0010232",
            state: "Odisha",
            district: "Cuttack",
            lat: 20.4625,
            lng: 85.8828,
            synthetic: true
        },
        'ATM Skimming': {
            name: "Manoj Kumar Das",
            phone: "+91 99371 05521",
            city: "Bhubaneswar",
            category: "ATM Skimming",
            amount: 80000,
            lossType: "ATM Cashout",
            muleAccount: "ICIC0003418291",
            muleUpi: "atmcashout.layer1@icici",
            ifsc: "ICIC0000001",
            state: "Odisha",
            district: "Khordha",
            lat: 20.3540,
            lng: 85.8275,
            synthetic: true
        }
    };

    const s = samples[crimeType] || samples['UPI Fraud'];
    const victimNameInp = document.getElementById('inp-victim-name');
    if (victimNameInp) victimNameInp.value = s.name;
    const victimPhoneInp = document.getElementById('inp-victim-phone');
    if (victimPhoneInp) victimPhoneInp.value = s.phone;
    const victimCityInp = document.getElementById('inp-victim-city');
    if (victimCityInp) victimCityInp.value = s.city;
    const catInp = document.getElementById('inp-crime-category');
    if (catInp) catInp.value = s.category;
    const amtInp = document.getElementById('inp-amount');
    if (amtInp) amtInp.value = s.amount;
    const lossInp = document.getElementById('inp-loss-type');
    if (lossInp) lossInp.value = s.lossType;
    const accInp = document.getElementById('inp-beneficiary-account');
    if (accInp) accInp.value = s.muleAccount;
    const upiInp = document.getElementById('inp-beneficiary-upi');
    if (upiInp) upiInp.value = s.muleUpi;
    const ifscInp = document.getElementById('inp-beneficiary-ifsc');
    if (ifscInp) ifscInp.value = s.ifsc;
    const stateInp = document.getElementById('inp-state');
    if (stateInp) stateInp.value = s.state;
    updateDistrictOptions();
    const distInp = document.getElementById('inp-district');
    if (distInp) distInp.value = s.district;
    const latInp = document.getElementById('inp-lat');
    if (latInp) latInp.value = s.lat;
    const lngInp = document.getElementById('inp-lng');
    if (lngInp) lngInp.value = s.lng;
    const synthInp = document.getElementById('inp-is-synthetic');
    if (synthInp) synthInp.checked = s.synthetic;

    showNotificationToast(`Sample pre-filled: ${s.category} (${s.name})`, 'info');
    verifyIFSCCode();
}

async function verifyIFSCCode() {
    const input = document.getElementById('inp-beneficiary-ifsc');
    const ifsc = (input ? input.value : '').trim().toUpperCase();
    if (!ifsc || ifsc.length !== 11) {
        showNotificationToast("Please enter an 11-character IFSC code (e.g. SBIN0010232 or HDFC0000060).", "warning");
        return;
    }

    try {
        const res = await fetch(`/api/public/ifsc/${ifsc}`);
        const data = await res.json();
        if (res.ok && data.bank) {
            const box = document.getElementById('ifsc-verified-box');
            document.getElementById('ifsc-bank-name').innerText = `🏦 ${data.bank} (${data.ifsc})`;
            document.getElementById('ifsc-branch').innerText = data.branch;
            document.getElementById('ifsc-district').innerText = data.district || 'City Center';
            document.getElementById('ifsc-state').innerText = data.state || 'India';
            document.getElementById('ifsc-address').innerText = data.address || 'Central Banking Hub';

            const railsContainer = document.getElementById('ifsc-rails');
            if (railsContainer) {
                railsContainer.innerHTML = `
                    <span>✓ NEFT: ${data.neft ? 'Active' : 'No'}</span>
                    <span>✓ RTGS: ${data.rtgs ? 'Active' : 'No'}</span>
                    <span>✓ IMPS: ${data.imps ? 'Active' : 'No'}</span>
                    <span>✓ UPI: ${data.upi ? 'Active' : 'No'}</span>
                `;
            }
            if (box) box.classList.remove('hidden');
            showNotificationToast(`🏛️ Verified via Real Gateway: ${data.bank} (${data.branch})`, 'success');
        } else {
            showNotificationToast(`IFSC validation: ${data.detail || 'Code not found in national directory'}`, 'warning');
        }
    } catch (err) {
        console.error("IFSC lookup error:", err);
        showNotificationToast("IFSC verification gateway unavailable.", "warning");
    }
}

function updateDistrictOptions() {
    const stateEl = document.getElementById('inp-state');
    if (!stateEl) return;
    const stateVal = stateEl.value;
    const distSelect = document.getElementById('inp-district');
    if (!distSelect) return;

    distSelect.innerHTML = '';
    const districtsByState = {
        'Odisha': [
            { val: 'Khordha', label: 'Khordha (Bhubaneswar)' },
            { val: 'Cuttack', label: 'Cuttack' }
        ],
        'Jharkhand': [
            { val: 'Deoghar', label: 'Deoghar (Cyber Crime Hub)' }
        ],
        'Haryana': [
            { val: 'Nuh', label: 'Nuh (Mewat Region)' }
        ],
        'Gujarat': [
            { val: 'Surat', label: 'Surat (Diamond Bourse)' }
        ],
        'Telangana': [
            { val: 'Hyderabad', label: 'Cyberabad (Hyderabad)' }
        ]
    };

    const list = districtsByState[stateVal] || [{ val: 'Khordha', label: 'Khordha (Bhubaneswar)' }];
    list.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d.val;
        opt.innerText = d.label;
        distSelect.appendChild(opt);
    });
    updateCoordinatesFromDistrict();
}

function updateCoordinatesFromDistrict() {
    const distEl = document.getElementById('inp-district');
    if (!distEl) return;
    const distVal = distEl.value;
    const coords = {
        'Khordha': { lat: 20.3533, lng: 85.8266 },
        'Cuttack': { lat: 20.4625, lng: 85.8828 },
        'Deoghar': { lat: 24.4826, lng: 86.7000 },
        'Nuh': { lat: 28.1158, lng: 77.0062 },
        'Surat': { lat: 21.1702, lng: 72.8311 },
        'Hyderabad': { lat: 17.4483, lng: 78.3915 }
    };
    const c = coords[distVal] || { lat: 20.3533, lng: 85.8266 };
    const latInp = document.getElementById('inp-lat');
    const lngInp = document.getElementById('inp-lng');
    if (latInp) latInp.value = c.lat;
    if (lngInp) lngInp.value = c.lng;
}

async function handleComplaintSubmit(event) {
    if (event) event.preventDefault();
    const btn = document.getElementById('btn-submit-complaint');
    const statusEl = document.getElementById('complaint-submit-status');
    const outcomePanel = document.getElementById('complaint-outcome-panel');

    const payload = {
        victim_name: document.getElementById('inp-victim-name').value.trim(),
        victim_phone: document.getElementById('inp-victim-phone').value.trim(),
        victim_city: document.getElementById('inp-victim-city').value.trim(),
        crime_category: document.getElementById('inp-crime-category').value,
        amount_lost_inr: parseFloat(document.getElementById('inp-amount').value || 0),
        loss_type: document.getElementById('inp-loss-type').value,
        beneficiary_account: document.getElementById('inp-beneficiary-account').value.trim() || "N/A",
        beneficiary_upi: document.getElementById('inp-beneficiary-upi').value.trim() || "N/A",
        beneficiary_ifsc: document.getElementById('inp-beneficiary-ifsc').value.trim().toUpperCase(),
        state: document.getElementById('inp-state').value,
        district: document.getElementById('inp-district').value,
        latitude: parseFloat(document.getElementById('inp-lat').value),
        longitude: parseFloat(document.getElementById('inp-lng').value),
        is_synthetic: document.getElementById('inp-is-synthetic').checked
    };

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="animate-spin inline-block mr-1">⚙️</span> Ingesting into PostgreSQL...`;
    }
    if (statusEl) statusEl.innerText = "Persisting to database and triggering ML inference...";

    try {
        const res = await fetch('/api/complaints/', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok && data.status === 'success') {
            if (statusEl) {
                statusEl.innerHTML = `<span class="text-emerald-400 font-bold">✓ Successfully Saved to PostgreSQL (${data.complaint.id})</span>`;
            }
            if (outcomePanel) {
                outcomePanel.classList.remove('hidden');
                document.getElementById('outcome-complaint-id').innerText = data.complaint.id;
                document.getElementById('outcome-hotspot-name').innerText = data.recalculated_hotspot.name;
                document.getElementById('outcome-risk-score').innerText = `${data.recalculated_hotspot.risk_score}/100`;
            }
            showNotificationToast(`✅ Stored in PostgreSQL: ${data.complaint.id}. Hotspot risk updated to ${data.recalculated_hotspot.risk_score}!`, 'success');
        } else {
            if (statusEl) {
                statusEl.innerHTML = `<span class="text-red-400 font-bold">Error: ${data.detail || 'Failed to persist complaint'}</span>`;
            }
            showNotificationToast(data.detail || 'Failed to submit complaint', 'warning');
        }
    } catch (err) {
        console.error("Complaint submit error:", err);
        if (statusEl) statusEl.innerHTML = `<span class="text-red-400 font-bold">Network / DB error occurred.</span>`;
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<span>⚡</span><span>Submit Complaint to PostgreSQL & Recalculate Risk</span>`;
        }
    }
}

// ==========================================
// COMPLAINT REGISTRY TAB (MANAGEMENT)
// ==========================================
let currentComplaintsPage = 1;
let compSearchDebounceTimer = null;

function debounceComplaintSearch() {
    clearTimeout(compSearchDebounceTimer);
    compSearchDebounceTimer = setTimeout(() => {
        loadComplaintsTab(1);
    }, 350);
}

function prevComplaintsPage() {
    if (currentComplaintsPage > 1) {
        loadComplaintsTab(currentComplaintsPage - 1);
    }
}

function nextComplaintsPage() {
    loadComplaintsTab(currentComplaintsPage + 1);
}

async function loadComplaintsTab(page = 1) {
    currentComplaintsPage = page;
    const searchVal = (document.getElementById('comp-filter-search')?.value || '').trim();
    const catVal = document.getElementById('comp-filter-category')?.value || 'All';
    const riskVal = document.getElementById('comp-filter-risk')?.value || 'All';

    let url = `/api/complaints/?page=${page}&limit=15`;
    if (searchVal) url += `&search=${encodeURIComponent(searchVal)}`;
    if (catVal && catVal !== 'All') url += `&category=${encodeURIComponent(catVal)}`;
    if (riskVal && riskVal !== 'All') url += `&risk_level=${encodeURIComponent(riskVal)}`;

    try {
        const res = await fetch(url, { headers: getAuthHeaders() });
        const data = await res.json();
        const tbody = document.getElementById('complaints-registry-body');
        const countDisplay = document.getElementById('comp-table-total-count');
        const pageIndicator = document.getElementById('complaints-page-indicator');
        const prevBtn = document.getElementById('btn-prev-complaints');
        const nextBtn = document.getElementById('btn-next-complaints');

        if (countDisplay) {
            countDisplay.innerText = `Showing ${data.data?.length || 0} of ${(data.total || 0).toLocaleString('en-IN')} records`;
        }
        if (pageIndicator) {
            const totalPages = Math.ceil((data.total || 1) / 15);
            pageIndicator.innerText = `Page ${data.page || page} of ${totalPages || 1}`;
        }
        if (prevBtn) prevBtn.disabled = page <= 1;
        if (nextBtn) nextBtn.disabled = (data.data?.length || 0) < 15;

        if (!tbody) return;
        tbody.innerHTML = '';

        (data.data || []).forEach(c => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-slate-200 hover:bg-slate-50 text-xs';
            const isCrit = c.risk_score >= 90;
            const isHigh = c.risk_score >= 70 && c.risk_score < 90;
            const badgeColor = isCrit ? 'bg-red-50 text-red-700 border-red-200' :
                               isHigh ? 'bg-orange-50 text-orange-700 border-orange-200' :
                               'bg-slate-100 text-slate-700 border-slate-200';

            tr.innerHTML = `
                <td class="p-2.5 font-mono text-slate-900 font-bold">${c.id}</td>
                <td class="p-2.5 text-slate-500 font-mono text-[11px]">${c.timestamp || '2026-03-15'}</td>
                <td class="p-2.5 font-semibold text-slate-900">${c.category}</td>
                <td class="p-2.5">
                    <div class="text-slate-900 font-medium">${c.victim_name}</div>
                    <div class="text-[10px] text-slate-500">${c.victim_city} • ${c.phone_redacted}</div>
                </td>
                <td class="p-2.5 font-mono font-bold text-red-600">₹${(c.amount || 0).toLocaleString('en-IN')}</td>
                <td class="p-2.5">
                    <div class="font-mono text-slate-800 text-[11px]">${c.beneficiary_account || 'N/A'}</div>
                    <div class="text-[10px] text-slate-500 font-mono">${c.beneficiary_ifsc || 'N/A'}</div>
                </td>
                <td class="p-2.5">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold border ${badgeColor}">
                        ${c.risk_score}/100
                    </span>
                </td>
                <td class="p-2.5">
                    <span class="px-1.5 py-0.5 rounded text-[9px] font-mono ${c.is_synthetic ? 'bg-amber-50 text-amber-800 border border-amber-200' : 'bg-emerald-50 text-emerald-800 border border-emerald-200'}">
                        ${c.is_synthetic ? 'DEMO' : 'CITIZEN'}
                    </span>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Complaints load error:", err);
    }
}

// ==========================================
// USERS & RBAC TAB
// ==========================================
async function loadUsersTab() {
    try {
        const res = await fetch('/api/auth/demo-users');
        const data = await res.json();
        const users = data.users || data || [];

        // Update session card
        if (state.currentUser) {
            const nameEl = document.getElementById('session-user-name');
            if (nameEl) nameEl.innerText = state.currentUser.name;
            const roleEl = document.getElementById('session-user-role');
            if (roleEl) roleEl.innerText = `${state.currentUser.role_id} • ${state.currentUser.name}`;
            const jurisEl = document.getElementById('session-user-jurisdiction');
            if (jurisEl) jurisEl.innerText = `${state.currentUser.jurisdiction} (Badge: ${state.currentUser.badge})`;
            const token = localStorage.getItem('cp_jwt_token') || 'No active JWT';
            const jwtPreviewEl = document.getElementById('session-jwt-preview');
            if (jwtPreviewEl) jwtPreviewEl.innerText = token.substring(0, 36) + '...' + token.slice(-20);
        }

        // Render RBAC Table
        const tbody = document.getElementById('users-rbac-table-body');
        if (!tbody) return;
        tbody.innerHTML = '';

        users.forEach(u => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-slate-200 hover:bg-slate-50 text-xs';

            tr.innerHTML = `
                <td class="p-2.5 font-mono text-slate-900 font-bold">${u.role_id}</td>
                <td class="p-2.5">
                    <div class="font-semibold text-slate-900">${u.name}</div>
                    <div class="text-[10px] text-slate-500">${u.username || u.email}</div>
                </td>
                <td class="p-2.5 text-slate-700">${u.jurisdiction}</td>
                <td class="p-2.5"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">PERMITTED</span></td>
                <td class="p-2.5">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold ${u.role_id === 'BANK_NODAL' || u.role_id === 'SYSTEM_ADMIN' || u.role_id === 'I4C_ADMIN' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-slate-100 text-slate-600 border border-slate-200'}">
                        ${u.role_id === 'BANK_NODAL' || u.role_id === 'SYSTEM_ADMIN' || u.role_id === 'I4C_ADMIN' ? 'PERMITTED' : 'RESTRICTED'}
                    </span>
                </td>
                <td class="p-2.5">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold ${u.role_id !== 'AUDITOR' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-slate-100 text-slate-600 border border-slate-200'}">
                        ${u.role_id !== 'AUDITOR' ? 'PERMITTED' : 'READ-ONLY'}
                    </span>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Users tab error:", err);
    }
}

// ==========================================
// SETTINGS TAB & DATABASE TELEMETRY
// ==========================================
async function loadSettingsTab() {
    try {
        const [sysRes, compRes] = await Promise.all([
            fetch('/api/system/status'),
            fetch('/api/complaints/summary')
        ]);
        const compData = await compRes.json();

        const tablesContainer = document.getElementById('settings-db-tables');
        if (tablesContainer) {
            const counts = [
                { name: 'complaints', count: compData.total_complaints || 5200 },
                { name: 'clusters', count: 12 },
                { name: 'atms', count: 240 },
                { name: 'alerts', count: 12 },
                { name: 'audit_logs', count: 48 },
                { name: 'users', count: 5 }
            ];
            tablesContainer.innerHTML = '';
            counts.forEach(c => {
                const box = document.createElement('div');
                box.className = 'bg-white p-2.5 rounded border border-slate-200 shadow-xs';
                box.innerHTML = `
                    <div class="text-[9px] text-slate-500 font-mono uppercase">${c.name}</div>
                    <div class="font-bold text-slate-900 text-sm font-mono">${c.count.toLocaleString('en-IN')}</div>
                `;
                tablesContainer.appendChild(box);
            });
        }
    } catch (err) {
        console.error("Settings tab error:", err);
    }
}

// ==========================================
// OFFICER AUTHENTICATION & LOGIN MODAL
// ==========================================
async function openLoginModal() {
    const modal = document.getElementById('login-modal');
    if (!modal) return;

    try {
        const res = await fetch('/api/auth/demo-users');
        const data = await res.json();
        const users = data.users || data || [];
        const picker = document.getElementById('demo-officers-picker');
        if (picker) {
            picker.innerHTML = '';
            users.forEach(u => {
                const card = document.createElement('div');
                card.className = 'p-2.5 bg-slate-50 border border-slate-200 hover:border-red-400 rounded-lg cursor-pointer transition-all flex items-center justify-between text-xs';
                card.innerHTML = `
                    <div>
                        <div class="font-bold text-slate-900">${u.name}</div>
                        <div class="text-[10px] text-slate-500">${u.role_id} • ${u.jurisdiction}</div>
                    </div>
                    <button class="px-2.5 py-1 bg-white hover:bg-red-50 text-red-700 border border-slate-300 hover:border-red-300 rounded text-[10px] font-bold shadow-xs">Select</button>
                `;
                card.addEventListener('click', () => {
                    document.getElementById('login-username').value = u.username || u.email;
                    document.getElementById('login-password').value = u.demo_password || 'Admin@2026';
                    submitOfficerLogin();
                });
                picker.appendChild(card);
            });
        }
    } catch (err) {
        console.error("Demo officers load error:", err);
    }

    modal.classList.remove('hidden');
}

function closeLoginModal() {
    const modal = document.getElementById('login-modal');
    if (modal) modal.classList.add('hidden');
    const errEl = document.getElementById('login-error-msg');
    if (errEl) errEl.classList.add('hidden');
}

async function submitOfficerLogin() {
    const userInp = document.getElementById('login-username');
    const passInp = document.getElementById('login-password');
    const errEl = document.getElementById('login-error-msg');

    const username = userInp ? userInp.value.trim() : '';
    const password = passInp ? passInp.value.trim() : '';

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (res.ok && data.access_token) {
            localStorage.setItem('cp_jwt_token', data.access_token);
            state.currentUser = data.user;
            updateUserDisplay();
            closeLoginModal();
            showNotificationToast(`🔑 Officer Authenticated: ${data.user.name} (${data.user.role_id})`, 'success');
            if (state.activeTab === 'users') loadUsersTab();
        } else {
            if (errEl) {
                errEl.innerText = data.detail || "Authentication failed.";
                errEl.classList.remove('hidden');
            }
        }
    } catch (err) {
        console.error("Login error:", err);
        if (errEl) {
            errEl.innerText = "Network error connecting to auth service.";
            errEl.classList.remove('hidden');
        }
    }
}

// Global Exports
window.switchTab = switchTab;
window.setAdvanceHorizon = setAdvanceHorizon;
window.loadDashboardData = loadDashboardData;
window.selectHotspotById = selectHotspotById;
window.openInterventionModal = openInterventionModal;
window.closeInterventionModal = closeInterventionModal;
window.submitProactiveIntervention = submitProactiveIntervention;
window.openFeedbackModal = openFeedbackModal;
window.closeFeedbackModal = closeFeedbackModal;
window.submitIncidentFeedback = submitIncidentFeedback;
window.triggerSimulatedBankFreeze = triggerSimulatedBankFreeze;
window.showNodeInspector = showNodeInspector;
window.loadEmergencyTab = loadEmergencyTab;
window.initWebSocket = initWebSocket;
window.populateSampleComplaint = populateSampleComplaint;
window.verifyIFSCCode = verifyIFSCCode;
window.updateDistrictOptions = updateDistrictOptions;
window.updateCoordinatesFromDistrict = updateCoordinatesFromDistrict;
window.handleComplaintSubmit = handleComplaintSubmit;
window.loadComplaintsTab = loadComplaintsTab;
window.debounceComplaintSearch = debounceComplaintSearch;
window.prevComplaintsPage = prevComplaintsPage;
window.nextComplaintsPage = nextComplaintsPage;
window.loadUsersTab = loadUsersTab;
window.loadSettingsTab = loadSettingsTab;
window.openLoginModal = openLoginModal;
window.closeLoginModal = closeLoginModal;
window.submitOfficerLogin = submitOfficerLogin;
