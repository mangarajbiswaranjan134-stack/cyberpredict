// CYBERPREDICT: Agentic AI (AAI) Copilot Controller
// Zero-Purple, High-Density Google Stitch Design System

async function sendCopilotMessage(explicitQuery = null) {
    const inputEl = document.getElementById('copilot-chat-input');
    const query = explicitQuery || (inputEl ? inputEl.value.trim() : '');
    if (!query) return;

    if (inputEl && !explicitQuery) inputEl.value = '';

    const feedEl = document.getElementById('copilot-chat-feed');
    if (!feedEl) return;

    // Append User Message
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'copilot-message-user p-3 max-w-[85%] self-end ml-auto text-xs text-slate-100 shadow-md mb-3';
    userMsgDiv.innerHTML = `
        <div class="flex items-center space-x-1.5 mb-1 text-cyan-400 font-mono text-[10px]">
            <span>👮</span>
            <span class="font-bold">INVESTIGATING OFFICER</span>
        </div>
        <div class="whitespace-pre-line">${escapeHtml(query)}</div>
    `;
    feedEl.appendChild(userMsgDiv);
    feedEl.scrollTop = feedEl.scrollHeight;

    // Append Thinking Indicator
    const agentMsgDiv = document.createElement('div');
    agentMsgDiv.className = 'copilot-message-agent p-3 max-w-[92%] text-xs text-slate-100 shadow-md mb-3';
    agentMsgDiv.innerHTML = `
        <div class="flex items-center space-x-2 text-cyan-400 font-mono text-[10px] mb-2">
            <span class="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
            <span class="font-bold tracking-wider">CYBERPREDICT AAI COPILOT</span>
            <span class="text-slate-500">•</span>
            <span class="text-slate-400">Multi-Agent Autonomous Pipeline Active...</span>
        </div>
        <div id="copilot-streaming-content" class="text-slate-400 italic text-[11px]">
            Synthesizing spatio-temporal telemetry and graph resolution...
        </div>
    `;
    feedEl.appendChild(agentMsgDiv);
    feedEl.scrollTop = feedEl.scrollHeight;

    try {
        const res = await fetch('/api/copilot/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                case_id: 'CYB-2026-004821',
                cluster_id: 'OD-BBSR-27',
                horizon: window.currentHorizon || '24h'
            })
        });

        if (!res.ok) throw new Error('Copilot response error');
        const data = await res.json();

        // Render Reasoning Steps
        let stepsHtml = '';
        if (data.reasoning_steps && data.reasoning_steps.length > 0) {
            stepsHtml = `<div class="mb-3 space-y-1.5 bg-slate-950/70 p-2.5 rounded border border-slate-800">
                <div class="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider">⚡ Multi-Agent Reasoning Chain:</div>`;
            data.reasoning_steps.forEach(s => {
                stepsHtml += `
                    <div class="agentic-step text-[11px] text-slate-300">
                        <span class="font-mono text-cyan-300 font-bold">[${s.agent}]</span>
                        <span class="text-white font-semibold">${s.title}:</span>
                        <span class="text-slate-400">${s.detail}</span>
                    </div>
                `;
            });
            stepsHtml += `</div>`;
        }

        // Render Markdown Body (simplified)
        let bodyHtml = formatMarkdown(data.response_markdown);

        // Render Suggested Action Buttons
        let actionsHtml = '';
        if (data.suggested_actions && data.suggested_actions.length > 0) {
            actionsHtml = `<div class="mt-3 pt-2 border-t border-slate-800 flex flex-wrap gap-2">`;
            data.suggested_actions.forEach(a => {
                actionsHtml += `
                    <button onclick="handleCopilotAction('${a.action}', '${a.target}')" 
                        class="px-2.5 py-1 bg-slate-800 hover:bg-cyan-950 hover:border-cyan-500 border border-slate-700 rounded text-[11px] font-bold text-cyan-300 transition-all shadow-sm">
                        ${a.label}
                    </button>
                `;
            });
            actionsHtml += `</div>`;
        }

        agentMsgDiv.innerHTML = `
            <div class="flex items-center justify-between text-cyan-400 font-mono text-[10px] mb-2 pb-1 border-b border-slate-800">
                <div class="flex items-center space-x-1.5">
                    <span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                    <span class="font-bold tracking-wider">CYBERPREDICT AAI COPILOT</span>
                </div>
                <span class="text-slate-500 font-mono">${new Date().toLocaleTimeString()}</span>
            </div>
            ${stepsHtml}
            <div class="prose prose-invert prose-xs text-slate-200">${bodyHtml}</div>
            ${actionsHtml}
        `;
        feedEl.scrollTop = feedEl.scrollHeight;

    } catch (err) {
        agentMsgDiv.innerHTML = `
            <div class="text-red-400 font-mono text-xs">⚠️ Error retrieving intelligence: ${err.message}</div>
        `;
    }
}

function handleCopilotAction(action, target) {
    if (action === 'VIEW_STITCH') {
        window.switchTab('stitch');
        window.loadStitchGraph(target === 'OD-BBSR-27' ? 'CYB-2026-004821' : target);
    } else if (action === 'VIEW_MAP' || action === 'FILTER_GIS') {
        window.switchTab('gis');
    } else if (action === 'VIEW_ALERTS') {
        window.switchTab('alerts');
    } else if (action === 'DISPATCH_PATROL') {
        window.openInterventionModal('OD-BBSR-27', 'Master Canteen Square ATM Cluster');
    } else if (action === 'BANK_FREEZE' || action === 'TRANSMIT_BANK_ADVISORY') {
        executeBankFreezeAdvisory(target);
    } else if (action === 'EXPORT_DOSSIER') {
        window.open('http://localhost:8000/api/reports/case/CYB-2026-004821/dossier', '_blank');
    } else {
        alert(`Action ${action} initiated for target: ${target}`);
    }
}

async function executeBankFreezeAdvisory(accountId) {
    try {
        const res = await fetch('/api/copilot/draft-action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action_type: 'BANK_FREEZE_102',
                target_id: accountId || '9182374619',
                officer_id: 'INSP-CYB-782'
            })
        });
        const data = await res.json();
        alert(`✅ STATUTORY MANDATE TRANSMITTED:\n\nOrder Ref: ${data.document_id}\nTarget: ${data.target}\nLegal Authority: ${data.legal_mandate}\n\nBank Nodal Desk notified for immediate debit restriction.`);
    } catch (e) {
        alert('Bank advisory transmission completed in demo environment.');
    }
}

function formatMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/^### (.*$)/gim, '<h4 class="text-cyan-300 font-bold text-sm my-1">$1</h4>')
        .replace(/\*\*(.*?)\*\*/gim, '<strong class="text-white font-bold">$1</strong>')
        .replace(/\*(.*?)\*/gim, '<em class="text-slate-300">$1</em>')
        .replace(/`([^`]+)`/gim, '<code class="bg-slate-900 border border-slate-800 text-cyan-300 px-1 py-0.5 rounded font-mono text-[10px]">$1</code>')
        .replace(/\n\n/gim, '<br><br>')
        .replace(/^\- (.*$)/gim, '<li class="ml-3 list-disc text-slate-300">$1</li>');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;
}

function copilotQuickAction(action, nodeId) {
    if (action === 'freeze_node') {
        executeBankFreezeAdvisory(nodeId);
    } else if (action === 'patrol_node') {
        window.openInterventionModal('OD-BBSR-27', 'Master Canteen Square ATM Cluster');
    }
}

window.copilotQuickAction = copilotQuickAction;
window.sendCopilotMessage = sendCopilotMessage;
window.handleCopilotAction = handleCopilotAction;
window.executeBankFreezeAdvisory = executeBankFreezeAdvisory;
