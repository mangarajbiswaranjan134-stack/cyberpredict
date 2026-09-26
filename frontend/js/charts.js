// CYBERPREDICT: Chart.js Visualizations & Intelligence Analytics (High-Tech Black & Red Theme)
let temporalChart = null;
let crimeCategoryChart = null;
let financialFlowChart = null;
let featureImportanceChart = null;

function initCharts() {
    Chart.defaults.color = '#94A3B8';
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.08)';
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
                    borderColor: '#EF4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.15)',
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#EF4444',
                    pointBorderColor: '#FFFFFF',
                    pointBorderWidth: 1.5,
                    pointRadius: 4,
                    pointHoverRadius: 7
                },
                {
                    label: 'Historical Baseline Activity',
                    data: baseline,
                    borderColor: '#64748B',
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
                        color: '#F8FAFC'
                    } 
                },
                tooltip: {
                    backgroundColor: '#0F172A',
                    titleColor: '#F8FAFC',
                    bodyColor: '#EF4444',
                    borderColor: '#DC2626',
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
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { 
                        callback: v => `${v}%`,
                        color: '#94A3B8',
                        font: { size: 10 }
                    }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.04)' },
                    ticks: { 
                        color: '#94A3B8',
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
                    '#EF4444', '#F97316', '#F59E0B', '#3B82F6', 
                    '#10B981', '#64748B', '#8B5CF6', '#EC4899'
                ],
                borderWidth: 2,
                borderColor: '#0F172A'
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
                        color: '#F8FAFC'
                    } 
                },
                tooltip: {
                    backgroundColor: '#0F172A',
                    titleColor: '#F8FAFC',
                    bodyColor: '#CBD5E1',
                    borderColor: '#DC2626',
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
                    'rgba(148, 163, 184, 0.85)',
                    'rgba(59, 130, 246, 0.85)',
                    'rgba(245, 158, 11, 0.85)',
                    'rgba(16, 185, 129, 0.85)',
                    'rgba(239, 68, 68, 0.85)'
                ],
                borderColor: ['#94A3B8', '#3B82F6', '#F59E0B', '#10B981', '#EF4444'],
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
                    backgroundColor: '#0F172A',
                    titleColor: '#F8FAFC',
                    bodyColor: '#EF4444',
                    borderColor: '#DC2626',
                    borderWidth: 1,
                    callbacks: { label: ctx => ` ₹${ctx.raw} Crores` }
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { 
                        callback: v => `₹${v} Cr`,
                        color: '#94A3B8',
                        font: { size: 10 }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { 
                        font: { size: 10 },
                        color: '#F8FAFC'
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
                backgroundColor: 'rgba(239, 68, 68, 0.85)',
                borderColor: '#EF4444',
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
                    backgroundColor: '#0F172A',
                    titleColor: '#F8FAFC',
                    bodyColor: '#EF4444',
                    borderColor: '#DC2626',
                    borderWidth: 1,
                    callbacks: { label: ctx => ` Weight: ${ctx.raw}%` } 
                }
            },
            scales: {
                x: {
                    max: 35,
                    ticks: { 
                        callback: v => `${v}%`,
                        color: '#94A3B8',
                        font: { size: 10 }
                    },
                    grid: { color: 'rgba(255, 255, 255, 0.06)' }
                },
                y: {
                    grid: { display: false },
                    ticks: { 
                        font: { size: 11, weight: '500' }, 
                        color: '#F8FAFC' 
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
