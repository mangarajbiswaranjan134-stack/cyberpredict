// CYBERPREDICT: Case Entity Relationship Network Graph (Vis.js)
let networkGraphInstance = null;

function renderCaseNetworkGraph(containerId, graphData) {
    const container = document.getElementById(containerId);
    if (!container || !graphData || !graphData.nodes) return;

    // Map node types to command-center icons and colors
    const typeStyles = {
        victim: { color: '#38BDF8', shape: 'dot', size: 24, font: { color: '#F8FAFC' } },
        mobile: { color: '#F59E0B', shape: 'diamond', size: 20, font: { color: '#F8FAFC' } },
        account: { color: '#0284C7', shape: 'box', size: 22, font: { color: '#F8FAFC' } },
        mule_account: { color: '#EC4899', shape: 'box', size: 22, font: { color: '#F8FAFC' } },
        atm: { color: '#EF4444', shape: 'triangle', size: 26, font: { color: '#F8FAFC' } },
        location: { color: '#F97316', shape: 'star', size: 28, font: { color: '#F8FAFC' } },
        lea: { color: '#10B981', shape: 'hexagon', size: 26, font: { color: '#F8FAFC' } }
    };

    const visNodes = graphData.nodes.map(n => {
        const style = typeStyles[n.type] || { color: '#94A3B8', shape: 'dot', size: 18 };
        return {
            id: n.id,
            label: n.label,
            color: {
                background: style.color,
                border: '#FFFFFF',
                highlight: { background: '#FFFFFF', border: style.color }
            },
            shape: style.shape,
            size: style.size,
            font: { color: '#F8FAFC', size: 11, face: 'Inter' },
            rawDetails: n.details,
            rawType: n.type
        };
    });

    const visEdges = graphData.edges.map(e => ({
        from: e.from,
        to: e.to,
        label: e.label || '',
        color: { color: 'rgba(148, 163, 184, 0.4)', highlight: '#38BDF8' },
        arrows: 'to',
        font: { color: '#94A3B8', size: 9, align: 'middle', background: '#0F172A' },
        smooth: { type: 'curvedCW', roundness: 0.15 }
    }));

    const data = {
        nodes: new vis.DataSet(visNodes),
        edges: new vis.DataSet(visEdges)
    };

    const options = {
        physics: {
            solver: 'forceAtlas2Based',
            forceAtlas2Based: {
                gravitationalConstant: -45,
                centralGravity: 0.01,
                springLength: 95,
                springConstant: 0.08
            },
            stabilization: { iterations: 120 }
        },
        interaction: {
            hover: true,
            tooltipDelay: 150,
            zoomView: true
        }
    };

    if (networkGraphInstance) {
        networkGraphInstance.destroy();
    }

    networkGraphInstance = new vis.Network(container, data, options);

    // Node selection inspector
    networkGraphInstance.on('selectNode', function(params) {
        if (params.nodes.length > 0) {
            const selectedId = params.nodes[0];
            const node = visNodes.find(n => n.id === selectedId);
            if (node && window.showNodeInspector) {
                window.showNodeInspector(node);
            }
        }
    });
}

window.renderCaseNetworkGraph = renderCaseNetworkGraph;
