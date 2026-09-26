// CYBERPREDICT: Chart.js Visualizations & Intelligence Analytics
let temporalChart = null;
let crimeCategoryChart = null;
let financialFlowChart = null;
let featureImportanceChart = null;

function initCharts() {
    Chart.defaults.color = '#94A3B8';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.borderColor = '#1E293B';
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
                    borderColor: '#06B6D4',
                    backgroundColor: 'rgba(6, 182, 212, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#06B6D4',
                    pointRadius: 4,
                    pointHoverRadius: 7
                },
                {
                    label: 'Historical Baseline Activity',
                    data: baseline,
                    borderColor: '#64748B',
                    borderDash: [5, 5],
                    borderWidth: 2,
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
                legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#F8FAFC',
                    bodyColor: '#38BDF8',
                    borderColor: '#334155',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(30, 41, 59, 0.5)' },
                    ticks: { callback: v => `${v}%` }
                },
                x: {
                    grid: { color: 'rgba(30, 41, 59, 0.3)' }
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
                    '#06B6D4', '#3B82F6', '#0284C7', '#0EA5E9', 
                    '#F59E0B', '#10B981', '#F43F5E', '#14B8A6'
                ],
                borderWidth: 2,
                borderColor: '#0F172A'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { boxWidth: 10, font: { size: 10 } } }
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
                    'rgba(59, 130, 246, 0.75)',
                    'rgba(14, 165, 233, 0.75)',
                    'rgba(245, 158, 11, 0.75)',
                    'rgba(16, 185, 129, 0.75)',
                    'rgba(239, 68, 68, 0.75)'
                ],
                borderColor: ['#3B82F6', '#0EA5E9', '#F59E0B', '#10B981', '#EF4444'],
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
                    callbacks: { label: ctx => ` ₹${ctx.raw} Crores` }
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(30, 41, 59, 0.5)' },
                    ticks: { callback: v => `₹${v} Cr` }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
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
                backgroundColor: 'rgba(6, 182, 212, 0.65)',
                borderColor: '#06B6D4',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: ctx => ` Weight: ${ctx.raw}%` } }
            },
            scales: {
                x: {
                    max: 35,
                    ticks: { callback: v => `${v}%` },
                    grid: { color: 'rgba(30, 41, 59, 0.5)' }
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 11 }, color: '#F1F5F9' }
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
