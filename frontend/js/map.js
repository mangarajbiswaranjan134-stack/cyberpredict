// CYBERPREDICT: Advanced GIS Risk Heatmap & Google Maps Platform Controller
// Google Maps API Key Integrated: AIzaSyBi0rNSgraXQAZSbyie6fDTQ7Cwsy3DAWY
const GOOGLE_MAPS_KEY = 'AIzaSyBi0rNSgraXQAZSbyie6fDTQ7Cwsy3DAWY';

let gisMap = null;
let fullGisMap = null;

// Map Layer Groups
let predictedLayer = null;
let historicalLayer = null;
let corridorLayer = null;
let heatLayer = null;

let fullPredictedLayer = null;
let fullHistoricalLayer = null;
let fullCorridorLayer = null;
let fullHeatLayer = null;

// Base Map Providers (Carto Dark Zero-Purple + Google Maps Platform)
const MAP_PROVIDERS = {
    carto_dark: {
        url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        options: { subdomains: 'abcd', maxZoom: 19, attribution: 'CartoDB Dark Slate' }
    },
    google_satellite: {
        url: `https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&key=${GOOGLE_MAPS_KEY}`,
        options: { maxZoom: 20, attribution: '© Google Satellite' }
    },
    google_hybrid: {
        url: `https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}&key=${GOOGLE_MAPS_KEY}`,
        options: { maxZoom: 20, attribution: '© Google Hybrid' }
    },
    google_streets: {
        url: `https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&key=${GOOGLE_MAPS_KEY}`,
        options: { maxZoom: 20, attribution: '© Google Maps' }
    },
    google_terrain: {
        url: `https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}&key=${GOOGLE_MAPS_KEY}`,
        options: { maxZoom: 20, attribution: '© Google Terrain' }
    }
};

let currentBaseLayerKey = 'carto_dark';
let overviewBaseLayer = null;
let fullGisBaseLayer = null;

// Layer visibility states
const layerVisibility = {
    predicted: true,
    historical: true,
    corridors: true,
    heat: true
};

function initGisMaps() {
    // 1. Overview Map (Command Center)
    const mapEl = document.getElementById('gis-map');
    if (mapEl && !gisMap) {
        gisMap = L.map('gis-map', {
            center: [21.5, 82.0],
            zoom: 5,
            minZoom: 4,
            maxZoom: 18,
            zoomControl: true,
            attributionControl: false
        });

        overviewBaseLayer = L.tileLayer(MAP_PROVIDERS.carto_dark.url, MAP_PROVIDERS.carto_dark.options).addTo(gisMap);
        predictedLayer = L.layerGroup().addTo(gisMap);
        historicalLayer = L.layerGroup().addTo(gisMap);
        corridorLayer = L.layerGroup().addTo(gisMap);
    }

    // 2. Full GIS View
    const fullMapEl = document.getElementById('full-gis-map');
    if (fullMapEl && !fullGisMap) {
        fullGisMap = L.map('full-gis-map', {
            center: [21.5, 82.0],
            zoom: 5,
            minZoom: 4,
            maxZoom: 18,
            zoomControl: true,
            attributionControl: false
        });

        fullGisBaseLayer = L.tileLayer(MAP_PROVIDERS.carto_dark.url, MAP_PROVIDERS.carto_dark.options).addTo(fullGisMap);
        fullPredictedLayer = L.layerGroup().addTo(fullGisMap);
        fullHistoricalLayer = L.layerGroup().addTo(fullGisMap);
        fullCorridorLayer = L.layerGroup().addTo(fullGisMap);
    }
}

function setMapBaseLayer(layerKey, targetMap = 'both') {
    if (!MAP_PROVIDERS[layerKey]) return;
    currentBaseLayerKey = layerKey;
    const provider = MAP_PROVIDERS[layerKey];

    if (gisMap && (targetMap === 'both' || targetMap === 'overview')) {
        if (overviewBaseLayer) gisMap.removeLayer(overviewBaseLayer);
        overviewBaseLayer = L.tileLayer(provider.url, provider.options).addTo(gisMap);
        overviewBaseLayer.bringToBack();
    }

    if (fullGisMap && (targetMap === 'both' || targetMap === 'full')) {
        if (fullGisBaseLayer) fullGisMap.removeLayer(fullGisBaseLayer);
        fullGisBaseLayer = L.tileLayer(provider.url, provider.options).addTo(fullGisMap);
        fullGisBaseLayer.bringToBack();
    }

    // Update active button state
    document.querySelectorAll('.map-tile-btn').forEach(btn => {
        if (btn.getAttribute('data-layer') === layerKey) {
            btn.classList.add('bg-cyan-900', 'text-cyan-200', 'font-bold');
            btn.classList.remove('text-slate-400');
        } else {
            btn.classList.remove('bg-cyan-900', 'text-cyan-200', 'font-bold');
            btn.classList.add('text-slate-400');
        }
    });
}

function renderMapLayers(hotspotData, targetMap = 'both') {
    if (!hotspotData) return;

    const { predicted_hotspots, historical_clusters, predicted_heat_points, corridors } = hotspotData;

    const populate = (mapInst, pLayer, hLayer, cLayer, isFull = false) => {
        if (!mapInst) return;

        if (pLayer) pLayer.clearLayers();
        if (hLayer) hLayer.clearLayers();
        if (cLayer) cLayer.clearLayers();

        // 1. Render Heatmap Layer
        if (typeof L.heatLayer === 'function' && predicted_heat_points && layerVisibility.heat) {
            if (isFull && fullHeatLayer) mapInst.removeLayer(fullHeatLayer);
            if (!isFull && heatLayer) mapInst.removeLayer(heatLayer);

            const heat = L.heatLayer(predicted_heat_points, {
                radius: 30,
                blur: 22,
                maxZoom: 10,
                max: 1.0,
                gradient: { 0.2: '#06B6D4', 0.5: '#EAB308', 0.75: '#F97316', 0.95: '#EF4444' }
            }).addTo(mapInst);

            if (isFull) fullHeatLayer = heat;
            else heatLayer = heat;
        }

        // 2. Render Predicted Hotspots (Advance Future Risk)
        if (predicted_hotspots && pLayer && layerVisibility.predicted) {
            predicted_hotspots.forEach(hotspot => {
                const isCritical = hotspot.risk_score >= 90;
                const isHigh = hotspot.risk_score >= 75 && hotspot.risk_score < 90;
                const pinColor = isCritical ? '#EF4444' : isHigh ? '#F97316' : '#FBBF24';

                const icon = L.divIcon({
                    className: 'custom-map-icon',
                    html: `
                        <div style="
                            background: ${pinColor}; 
                            border: 2px solid #FFFFFF; 
                            border-radius: 50%; 
                            width: ${isCritical ? 26 : 22}px; 
                            height: ${isCritical ? 26 : 22}px; 
                            display: flex; align-items: center; justify-content: center; 
                            color: white; font-weight: 800; font-size: 10px; 
                            box-shadow: 0 0 14px ${pinColor};
                            cursor: pointer;">
                            ${hotspot.risk_score}
                        </div>
                    `,
                    iconSize: [26, 26],
                    iconAnchor: [13, 13]
                });

                const marker = L.marker([hotspot.lat, hotspot.lng], { icon: icon }).addTo(pLayer);

                const popupHtml = `
                    <div style="min-width: 260px; padding: 4px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 10px; font-weight: 800; color: ${pinColor}; border: 1px solid ${pinColor}; padding: 1px 6px; border-radius: 4px;">
                                🔮 PREDICTED FUTURE RISK: ${hotspot.risk_score}/100
                            </span>
                            <span style="font-size: 10px; color: #94A3B8;">Prob: ${Math.round(hotspot.prediction_probability * 100)}%</span>
                        </div>
                        <div style="font-weight: 700; font-size: 13px; color: #F8FAFC; margin-bottom: 2px;">
                            ${hotspot.name}
                        </div>
                        <div style="font-size: 11px; color: #94A3B8; margin-bottom: 6px;">
                            📍 ${hotspot.locality}, ${hotspot.district}
                        </div>
                        <div style="background: rgba(30, 41, 59, 0.8); padding: 8px; border-radius: 6px; font-size: 11px; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                                <span style="color: #94A3B8;">Forecast Window:</span>
                                <span style="color: #38BDF8; font-weight: 700;">${hotspot.forecast_window}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                                <span style="color: #94A3B8;">Est. Cashout Txns:</span>
                                <span style="color: #F8FAFC; font-weight: 600;">${hotspot.estimated_transactions || 18} attempts</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: #94A3B8;">Potential Exposure:</span>
                                <span style="color: #EF4444; font-weight: 700;">₹${hotspot.estimated_exposure} Lakhs</span>
                            </div>
                        </div>
                        <button onclick="window.selectHotspotById('${hotspot.cluster_id}')" 
                            style="width: 100%; background: #0284C7; color: white; border: none; padding: 6px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; cursor: pointer; margin-bottom: 4px;">
                            Inspect Why This Location (XAI)
                        </button>
                        <button onclick="window.openStreetViewPanorama(${hotspot.lat}, ${hotspot.lng}, '${hotspot.name}')" 
                            style="width: 100%; background: #0F766E; color: white; border: none; padding: 5px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; cursor: pointer;">
                            🛰️ Google Satellite & Street View
                        </button>
                    </div>
                `;

                marker.bindPopup(popupHtml);
                marker.on('click', () => {
                    if (window.selectHotspotById) window.selectHotspotById(hotspot.cluster_id);
                });
            });
        }

        // 3. Render Historical Withdrawal Clusters (Past 7 Days)
        if (historical_clusters && hLayer && layerVisibility.historical) {
            historical_clusters.forEach(h => {
                const hIcon = L.divIcon({
                    className: 'custom-hist-icon',
                    html: `
                        <div style="
                            background: rgba(15, 23, 42, 0.9); 
                            border: 1.5px solid #94A3B8; 
                            border-radius: 50%; 
                            width: 14px; height: 14px; 
                            display: flex; align-items: center; justify-content: center; 
                            color: #94A3B8; font-size: 8px; font-weight: bold;
                            opacity: 0.85; cursor: pointer;">
                            H
                        </div>
                    `,
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                });

                const marker = L.marker([h.lat, h.lng], { icon: hIcon }).addTo(hLayer);
                const hPopup = `
                    <div style="min-width: 220px; padding: 3px; font-size: 11px;">
                        <span style="font-size: 9px; font-weight: bold; color: #94A3B8; border: 1px solid #475569; padding: 1px 4px; border-radius: 3px;">
                            📜 HISTORICAL WITHDRAWAL (PAST EVENT)
                        </span>
                        <div style="font-weight: 700; color: #F1F5F9; margin-top: 4px;">${h.cluster_name}</div>
                        <div style="color: #94A3B8;">Terminal: ${h.atm_id} (${h.bank})</div>
                        <div style="color: #EF4444; font-weight: 600; margin-top: 3px;">Withdrawn: ₹${(h.amount_withdrawn_inr).toLocaleString('en-IN')}</div>
                        <div style="color: #64748B; font-size: 10px;">Time: ${h.timestamp}</div>
                    </div>
                `;
                marker.bindPopup(hPopup);
            });
        }

        // 4. Render Corridors
        if (corridors && cLayer && layerVisibility.corridors) {
            corridors.forEach(corr => {
                const polyline = L.polyline([corr.start, corr.end], {
                    color: corr.risk === 'CRITICAL' ? '#EF4444' : '#F97316',
                    weight: 3,
                    dashArray: '6, 8',
                    opacity: 0.8
                }).addTo(cLayer);
                polyline.bindTooltip(`<b>${corr.name}</b><br>${corr.description}`, { sticky: true });
            });
        }
    };

    if (targetMap === 'both' || targetMap === 'overview') {
        populate(gisMap, predictedLayer, historicalLayer, corridorLayer, false);
    }
    if (targetMap === 'both' || targetMap === 'full') {
        populate(fullGisMap, fullPredictedLayer, fullHistoricalLayer, fullCorridorLayer, true);
    }
}

function toggleMapLayer(layerName, isVisible) {
    layerVisibility[layerName] = isVisible;
    if (window.lastHotspotData) {
        renderMapLayers(window.lastHotspotData, 'both');
    }
}

function zoomToHotspot(lat, lng, zoomLevel = 13) {
    if (gisMap) gisMap.setView([lat, lng], zoomLevel, { animate: true, duration: 1.0 });
    if (fullGisMap) fullGisMap.setView([lat, lng], zoomLevel, { animate: true, duration: 1.0 });
}

function updateHotspotMarker(pred) {
    if (!pred || !gisMap) return;
    if (window.lastHotspotData && window.lastHotspotData.predicted_hotspots) {
        const idx = window.lastHotspotData.predicted_hotspots.findIndex(p => p.cluster_id === pred.cluster_id || p.id === pred.id);
        if (idx !== -1) {
            window.lastHotspotData.predicted_hotspots[idx] = { ...window.lastHotspotData.predicted_hotspots[idx], ...pred };
        } else {
            window.lastHotspotData.predicted_hotspots.unshift(pred);
        }
        renderMapLayers(window.lastHotspotData, 'overview');
        gisMap.flyTo([pred.lat, pred.lng], 9, { animate: true, duration: 1.0 });
    }
}

// Google Street View & Satellite Tactical Panorama Controller
let streetViewPanoramaInstance = null;

function openStreetViewPanorama(lat = 20.2648, lng = 85.8394, title = "Master Canteen Square ATM Cluster (OD-BBSR-27)") {
    const modal = document.getElementById('streetview-modal');
    const container = document.getElementById('streetview-pano-container');
    const titleEl = document.getElementById('streetview-title');
    const coordsEl = document.getElementById('streetview-coords');

    if (!modal || !container) return;

    if (titleEl) titleEl.innerText = `🛰️ ${title}`;
    if (coordsEl) coordsEl.innerText = `GPS: Lat ${parseFloat(lat).toFixed(5)}, Lng ${parseFloat(lng).toFixed(5)} • Google Maps Platform Satellite & Street View`;

    modal.classList.remove('hidden');

    if (typeof google !== 'undefined' && google.maps) {
        const targetPos = { lat: parseFloat(lat), lng: parseFloat(lng) };
        const svService = new google.maps.StreetViewService();

        svService.getPanorama({ location: targetPos, radius: 250 }, (data, status) => {
            if (status === google.maps.StreetViewStatus.OK && data && data.location) {
                streetViewPanoramaInstance = new google.maps.StreetViewPanorama(container, {
                    position: data.location.latLng,
                    pov: { heading: 165, pitch: 0 },
                    zoom: 1,
                    addressControl: true,
                    linksControl: true,
                    panControl: true,
                    enableCloseButton: false
                });
            } else {
                // If 360 Street View imagery is unavailable, render Google 3D Hybrid Satellite view with markers
                const satMap = new google.maps.Map(container, {
                    center: targetPos,
                    zoom: 18,
                    mapTypeId: 'hybrid',
                    tilt: 45,
                    mapTypeControl: true,
                    streetViewControl: true,
                    fullscreenControl: true
                });
                new google.maps.Marker({
                    position: targetPos,
                    map: satMap,
                    title: title,
                    animation: google.maps.Animation.DROP
                });
            }
        });
    } else {
        container.innerHTML = `
            <div class="flex items-center justify-center h-full text-slate-400 text-xs">
                Google Maps Platform SDK initializing...
            </div>
        `;
    }
}

function closeStreetViewModal() {
    const modal = document.getElementById('streetview-modal');
    if (modal) modal.classList.add('hidden');
}

window.initGisMaps = initGisMaps;
window.renderMapLayers = renderMapLayers;
window.toggleMapLayer = toggleMapLayer;
window.zoomToHotspot = zoomToHotspot;
window.updateHotspotMarker = updateHotspotMarker;
window.setMapBaseLayer = setMapBaseLayer;
window.openStreetViewPanorama = openStreetViewPanorama;
window.closeStreetViewModal = closeStreetViewModal;
