// CYBERPREDICT: Google Stitch Entity & Cashout Flow Canvas (vis.js)
// High-Tech Black & Red Intelligence Design System
let stitchNetworkInstance = null;
let currentStitchData = null;

async function loadStitchGraph(caseId = 'CYB-2026-004821') {
    const container = document.getElementById('stitch-network-container');
    if (!container) return;

    try {
        const res = await fetch(`/api/copilot/stitch-graph?case_id=${encodeURIComponent(caseId)}`);
        if (!res.ok) throw new Error('Failed to fetch Stitch graph');
        const data = await res.json();
        currentStitchData = data;
        renderStitchCanvas(data);
        updateStitchTelemetry(data.stitch_summary);
    } catch (err) {
        console.error('Stitch load error:', err);
    }
}

function renderStitchCanvas(graphData) {
    const container = document.getElementById('stitch-network-container');
    if (!container || !graphData || !graphData.nodes) return;

    const visNodes = graphData.nodes.map(n => ({
        id: n.id,
        label: n.label,
        color: {
            background: n.color || '#EF4444',
            border: '#F8FAFC',
            highlight: { background: '#EF4444', border: '#FFFFFF' }
        },
        shape: n.shape || 'box',
        size: n.size || 24,
        font: { color: '#F8FAFC', size: 11, face: 'Inter', strokeWidth: 2, strokeColor: '#080C14' },
        rawDetails: n.details,
        stitchRole: n.stitch_role
    }));

    const visEdges = graphData.edges.map(e => ({
        from: e.from,
        to: e.to,
        label: e.label || '',
        color: { color: e.color || '#EF4444', highlight: '#F87171' },
        width: e.width || 2,
        dashes: e.dashes || false,
        arrows: e.arrows ? { to: { enabled: true, scaleFactor: 0.8 } } : undefined,
        font: { color: '#CBD5E1', size: 9, face: 'JetBrains Mono', background: '#0F172A' }
    }));

    const options = {
        physics: {
            solver: 'forceAtlas2Based',
            forceAtlas2Based: {
                gravitationalConstant: -70,
                centralGravity: 0.015,
                springLength: 140,
                springConstant: 0.08
            },
            stabilization: { iterations: 120 }
        },
        interaction: {
            hover: true,
            zoomView: true,
            dragView: true
        }
    };

    if (stitchNetworkInstance) {
        stitchNetworkInstance.destroy();
    }

    stitchNetworkInstance = new vis.Network(container, { nodes: visNodes, edges: visEdges }, options);

    stitchNetworkInstance.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = visNodes.find(n => n.id === nodeId);
            if (node) {
                showStitchNodeDetails(node);
            }
        }
    });
}

function updateStitchTelemetry(summary) {
    if (!summary) return;
    const amountEl = document.getElementById('stitch-amount-at-risk');
    const atmEl = document.getElementById('stitch-predicted-atm');
    const confEl = document.getElementById('stitch-confidence-badge');
    const windowEl = document.getElementById('stitch-intercept-window');

    if (amountEl) amountEl.innerText = `₹${(summary.amount_at_risk / 100000).toFixed(2)} L`;
    if (atmEl) atmEl.innerText = summary.predicted_atm || 'Axis Bank ATM - Master Canteen';
    if (confEl) confEl.innerText = `${(summary.confidence_score * 100).toFixed(1)}% ML CONFIDENCE`;
    if (windowEl) windowEl.innerText = summary.proactive_intercept_window || '18:00 - 21:00 IST';
}

function showStitchNodeDetails(node) {
    const detailPanel = document.getElementById('stitch-node-detail-panel');
    if (!detailPanel) return;

    let detailsHtml = `
        <div class="p-3 bg-[#0F172A] rounded border border-slate-800 shadow-md text-slate-100">
            <div class="flex items-center justify-between mb-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-950 text-red-400 border border-red-800">${node.stitchRole || 'Entity'}</span>
                <span class="text-[10px] text-slate-400 font-mono">${node.id}</span>
            </div>
            <div class="text-sm font-bold text-white mb-2 whitespace-pre-line">${node.label}</div>
            <div class="space-y-1 text-xs text-slate-300">
    `;

    if (node.rawDetails) {
        for (const [k, v] of Object.entries(node.rawDetails)) {
            detailsHtml += `<div class="flex justify-between border-b border-slate-800 pb-1">
                <span class="text-slate-400 uppercase text-[10px]">${k.replace(/_/g, ' ')}:</span>
                <span class="font-mono text-white font-semibold">${v}</span>
            </div>`;
        }
    }

    detailsHtml += `
            </div>
            <div class="mt-3 flex gap-2">
                <button onclick="copilotQuickAction('freeze_node', '${node.id}')" class="flex-1 py-1.5 px-2 bg-red-600 hover:bg-red-500 text-white rounded text-[11px] font-bold transition-all shadow-xs">
                    🛑 Section 102 Freeze
                </button>
                <button onclick="copilotQuickAction('patrol_node', '${node.id}')" class="flex-1 py-1.5 px-2 bg-slate-800 hover:bg-slate-700 text-white rounded text-[11px] font-bold transition-all shadow-xs border border-slate-700">
                    🚓 Dispatch 112 Patrol
                </button>
            </div>
        </div>
    `;

    detailPanel.innerHTML = detailsHtml;
}

window.loadStitchGraph = loadStitchGraph;
window.renderStitchCanvas = renderStitchCanvas;
window.showStitchNodeDetails = showStitchNodeDetails;
