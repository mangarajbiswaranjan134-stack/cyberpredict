// CYBERPREDICT: 15-Step Complete SIH Demonstration Simulation Engine
async function triggerCybercrimeSurge() {
    const btn = document.getElementById('btn-simulate-event');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="animate-spin inline-block mr-1">⚙️</span> Step 1/15: Ingesting Burst Complaints...`;
    }

    // Step 1 & 2: Complaint Burst & Cluster Formation
    showNotificationToast("⚡ [Step 1/15] New synthetic complaints arriving: 15 high-value UPI fraud reports registered on NCRP...", "warning");

    try {
        const res = await fetch('/api/simulation/trigger-surge', { method: 'POST' });
        const data = await res.json();

        if (data.status === 'success') {
            const payload = data.payload;
            const boosted = payload.boosted_cluster;

            setTimeout(() => {
                if (btn) btn.innerHTML = `<span class="animate-spin inline-block mr-1">⚙️</span> Step 3-4/15: AI Pattern & Risk Scoring...`;
                showNotificationToast("🤖 [Step 3-4/15] Pattern Detection Running: Random Forest & Temporal Model detected multi-hop mule layering...", "info");
            }, 800);

            setTimeout(() => {
                if (btn) btn.innerHTML = `<span class="animate-spin inline-block mr-1">⚙️</span> Step 5-6/15: Advance Forecast & Window...`;
                showNotificationToast(`🔮 [Step 5-6/15] Advance Location Predicted: ${boosted.name} flagged as Critical Cashout Zone for ${boosted.forecast_window}!`, "critical");
            }, 1800);

            setTimeout(() => {
                if (btn) btn.innerHTML = `<span class="animate-spin inline-block mr-1">⚙️</span> Step 7-8/15: GIS Pulse & Explainable AI...`;
                showNotificationToast("🗺️ [Step 7-8/15] GIS Hotspot Pulsing: SHAP-style Explainable AI computed 7 contributing risk factors.", "critical");
                
                // Refresh dashboard and focus on Bhubaneswar
                if (window.loadDashboardData) window.loadDashboardData();
                if (window.zoomToHotspot) window.zoomToHotspot(boosted.lat, boosted.lng, 14);
                if (window.selectHotspotById) window.selectHotspotById(boosted.cluster_id);
            }, 2800);

            setTimeout(() => {
                if (btn) btn.innerHTML = `<span class="animate-spin inline-block mr-1">⚙️</span> Step 9-11/15: Alert & Intelligence Brief...`;
                showNotificationToast(`🚨 [Step 9-11/15] Actionable Alert Created: ${payload.new_alert.id}. Operator initiated human review.`, "critical");
            }, 3800);

            setTimeout(() => {
                if (btn) btn.innerHTML = `<span class="animate-spin inline-block mr-1">⚙️</span> Step 12-15/15: Intervention & Feedback Ready...`;
                showNotificationToast("🛡️ [Step 12-15/15] Multi-Agency Intervention Dispatched: Simulated Bank hold sent & LEA QRT staged. Incident ready for outcome logging!", "success");

                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = `⚡ Simulate Cybercrime Event`;
                }
            }, 5000);
        }
    } catch (err) {
        console.error("Simulation error:", err);
        showNotificationToast("Simulation engine temporarily unavailable.", "error");
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `⚡ Simulate Cybercrime Event`;
        }
    }
}

async function resetSimulation() {
    try {
        const res = await fetch('/api/simulation/reset', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
            showNotificationToast("System baseline restored to initial clean state.", "info");
            if (window.loadDashboardData) window.loadDashboardData();
        }
    } catch (err) {
        console.error("Reset error:", err);
    }
}

function showNotificationToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    const borderColors = {
        critical: 'border-slate-200 bg-white text-slate-900 shadow-lg border-l-4 border-l-red-600',
        warning: 'border-slate-200 bg-white text-slate-900 shadow-lg border-l-4 border-l-amber-500',
        info: 'border-slate-200 bg-white text-slate-900 shadow-lg border-l-4 border-l-slate-800',
        success: 'border-slate-200 bg-white text-slate-900 shadow-lg border-l-4 border-l-emerald-600'
    };

    toast.className = `p-3 mb-2 rounded-lg border text-xs shadow-lg flex items-start space-x-2 transition-all duration-300 transform translate-y-2 opacity-0 ${borderColors[type] || borderColors.info}`;
    toast.innerHTML = `
        <span class="text-sm">${type === 'critical' ? '🚨' : type === 'warning' ? '⚠️' : type === 'success' ? '✅' : 'ℹ️'}</span>
        <div class="flex-1 font-medium leading-tight">${message}</div>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
        toast.classList.add('translate-y-0', 'opacity-100');
    }, 20);

    setTimeout(() => {
        toast.classList.remove('opacity-100');
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 4800);
}

window.triggerCybercrimeSurge = triggerCybercrimeSurge;
window.resetSimulation = resetSimulation;
window.showNotificationToast = showNotificationToast;
