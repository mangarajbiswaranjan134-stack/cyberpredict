// CYBERPREDICT: Chart.js Visualizations & Intelligence Analytics (White + Red + Dark Text Theme)
let temporalChart = null;
let crimeCategoryChart = null;
let financialFlowChart = null;
let featureImportanceChart = null;

function initCharts() {
    Chart.defaults.color = '#334155';
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
    Chart.defaults.borderColor = '#E2E8F0';
}

function renderTemporalChart(curveData) {
    const ctx = document.getElementById('temporal-risk-chart');
    if (!ctx) return;

    const labels = curveData.map(d => d.hour);
    const predicted = curveData.map(d => d.predicted_risk_level);
    const baseline = curveData.map(d => d.historical_baseline);

    if (temporalChart) temporalChart.destroy();

    temporalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Predicted Withdrawal Risk Level',
                    data: predicted,
                    borderColor: '#DC2626',
                    backgroundColor: 'rgba(220, 38, 38, 0.08)',
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#DC2626',
                    pointBorderColor: '#FFFFFF',
                    pointBorderWidth: 1.5,
                    pointRadius: 4,
                    pointHoverRadius: 7
                },
                {
                    label: 'Historical Baseline Activity',
                    data: baseline,
                    borderColor: '#94A3B8',
                    borderDash: [5, 5],
                    borderWidth: 1.75,
                    fill: false,
                    tension: 0.35,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { 
                    position: 'top', 
                    labels: { 
                        boxWidth: 12, 
                        font: { size: 11, weight: '500' },
                        color: '#0F172A'
                    } 
                },
                tooltip: {
                    backgroundColor: '#FFFFFF',
                    titleColor: '#0F172A',
                    bodyColor: '#DC2626',
                    borderColor: '#CBD5E1',
                    borderWidth: 1,
                    padding: 10,
                    boxPadding: 4,
                    usePointStyle: true,
                    titleFont: { weight: 'bold' }
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: '#F1F5F9' },
                    ticks: { 
                        callback: v => `${v}%`,
                        color: '#64748B',
                        font: { size: 10 }
                    }
                },
                x: {
                    grid: { color: '#F8FAFC' },
                    ticks: { 
                        color: '#64748B',
                        font: { size: 10 }
                    }
                }
            }
        }
    });
}

function renderCrimeCategoryChart(categoryData) {
    const ctx = document.getElementById('crime-category-chart');
    if (!ctx) return;

    const labels = Object.keys(categoryData);
    const values = Object.values(categoryData);

    if (crimeCategoryChart) crimeCategoryChart.destroy();

    crimeCategoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#DC2626', '#EA580C', '#D97706', '#0F172A', 
                    '#334155', '#059669', '#2563EB', '#475569'
                ],
                borderWidth: 2,
                borderColor: '#FFFFFF'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { 
                    position: 'right', 
                    labels: { 
                        boxWidth: 10, 
                        font: { size: 10 },
                        color: '#0F172A'
                    } 
                },
                tooltip: {
                    backgroundColor: '#FFFFFF',
                    titleColor: '#0F172A',
                    bodyColor: '#334155',
                    borderColor: '#CBD5E1',
                    borderWidth: 1,
                    padding: 8
                }
            },
            cutout: '68%'
        }
    });
}

function renderFinancialFlowChart(flowData) {
    const ctx = document.getElementById('financial-flow-chart');
    if (!ctx) return;

    const labels = flowData.map(d => d.stage);
    const values = flowData.map(d => d.amount_cr);

    if (financialFlowChart) financialFlowChart.destroy();

    financialFlowChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Volume (₹ Crores)',
                data: values,
                backgroundColor: [
                    'rgba(15, 23, 42, 0.85)',
                    'rgba(51, 65, 85, 0.85)',
                    'rgba(217, 119, 6, 0.85)',
                    'rgba(5, 150, 105, 0.85)',
                    'rgba(220, 38, 38, 0.85)'
                ],
                borderColor: ['#0F172A', '#334155', '#D97706', '#059669', '#DC2626'],
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#FFFFFF',
                    titleColor: '#0F172A',
                    bodyColor: '#DC2626',
                    borderColor: '#CBD5E1',
                    borderWidth: 1,
                    callbacks: { label: ctx => ` ₹${ctx.raw} Crores` }
                }
            },
            scales: {
                y: {
                    grid: { color: '#F1F5F9' },
                    ticks: { 
                        callback: v => `₹${v} Cr`,
                        color: '#64748B',
                        font: { size: 10 }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { 
                        font: { size: 10 },
                        color: '#0F172A'
                    }
                }
            }
        }
    });
}

function renderFeatureImportanceChart(features) {
    const ctx = document.getElementById('feature-importance-chart');
    if (!ctx) return;

    const labels = features.map(f => f.feature);
    const values = features.map(f => Math.round(f.importance * 100));

    if (featureImportanceChart) featureImportanceChart.destroy();

    featureImportanceChart = new Chart(ctx, {
        type: 'bar',
        indexAxis: 'y',
        data: {
            labels: labels,
            datasets: [{
                label: 'Predictive Feature Weight (%)',
                data: values,
                backgroundColor: 'rgba(220, 38, 38, 0.85)',
                borderColor: '#DC2626',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { 
                    backgroundColor: '#FFFFFF',
                    titleColor: '#0F172A',
                    bodyColor: '#DC2626',
                    borderColor: '#CBD5E1',
                    borderWidth: 1,
                    callbacks: { label: ctx => ` Weight: ${ctx.raw}%` } 
                }
            },
            scales: {
                x: {
                    max: 35,
                    ticks: { 
                        callback: v => `${v}%`,
                        color: '#64748B',
                        font: { size: 10 }
                    },
                    grid: { color: '#F1F5F9' }
                },
                y: {
                    grid: { display: false },
                    ticks: { 
                        font: { size: 11, weight: '500' }, 
                        color: '#0F172A' 
                    }
                }
            }
        }
    });
}

window.initCharts = initCharts;
window.renderTemporalChart = renderTemporalChart;
window.renderCrimeCategoryChart = renderCrimeCategoryChart;
window.renderFinancialFlowChart = renderFinancialFlowChart;
window.renderFeatureImportanceChart = renderFeatureImportanceChart;
