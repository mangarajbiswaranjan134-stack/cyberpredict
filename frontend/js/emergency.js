// CYBERPREDICT: Emergency 112 Rapid Escalation Controller
let currentEscalationAlertId = null;

function openEmergency112Modal(alertId = null) {
    currentEscalationAlertId = alertId;
    const modal = document.getElementById('emergency-112-modal');
    if (!modal) return;

    // Prefill target alert or top hotspot if available
    const alertIdDisplay = document.getElementById('modal-emergency-alert-id');
    if (alertIdDisplay) {
        alertIdDisplay.innerText = alertId || 'ALT-TOP-HOTSPOT (Bhubaneswar Cluster #27)';
    }

    modal.classList.remove('hidden');
}

function closeEmergency112Modal() {
    const modal = document.getElementById('emergency-112-modal');
    if (modal) modal.classList.add('hidden');
}

async function submitEmergency112Escalation() {
    const confirmCheckbox = document.getElementById('emergency-confirm-checkbox');
    const notesInput = document.getElementById('emergency-operator-notes');

    if (!confirmCheckbox || !confirmCheckbox.checked) {
        alert("Safety Rule: Please verify and check the authorized human-in-the-loop confirmation before escalating to 112 ERSS.");
        return;
    }

    const payload = {
        alert_id: currentEscalationAlertId || "ALT-TOP-HOTSPOT",
        operator_notes: notesInput ? notesInput.value : "Emergency cashout interception authorized.",
        authorized_confirmation: true
    };

    try {
        const res = await fetch('/api/emergency/escalate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.status === 'success') {
            closeEmergency112Modal();
            showNotificationToast(`🚨 112 ERSS Incident Logged: ${data.incident.incident_id} dispatched to Quick Response Team!`, 'critical');
            
            // Refresh emergency incident table if on Emergency tab
            if (window.loadEmergencyTab) {
                window.loadEmergencyTab();
            }
        } else {
            alert(data.detail || "Escalation could not be completed.");
        }
    } catch (err) {
        console.error("Emergency escalation error:", err);
        alert("Failed to connect to Emergency ERSS service.");
    }
}

window.openEmergency112Modal = openEmergency112Modal;
window.closeEmergency112Modal = closeEmergency112Modal;
window.submitEmergency112Escalation = submitEmergency112Escalation;
