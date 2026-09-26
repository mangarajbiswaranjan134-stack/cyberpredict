from fastapi import APIRouter, Query
from typing import Optional
from ..database.repository import data_repository

router = APIRouter(prefix="/api/hotspots", tags=["GIS Hotspots"])

@router.get("/")
def get_all_hotspots(
    horizon: str = Query("24h", pattern="^(1h|6h|12h|24h)$"),
    risk_level: Optional[str] = None,
    state: Optional[str] = None
):
    preds = data_repository.get_predictions_by_horizon(horizon=horizon)

    if risk_level and risk_level != "All":
        preds = [p for p in preds if p["risk_level"].upper() == risk_level.upper()]

    if state and state != "All":
        preds = [p for p in preds if p["state"].lower() == state.lower()]

    # Format for Leaflet heat layer: [lat, lng, intensity]
    predicted_heat_points = []
    for p in preds:
        intensity = p["risk_score"] / 100.0
        predicted_heat_points.append([p["lat"], p["lng"], round(intensity, 2)])

    # Historical withdrawal heat points (past 7 days)
    historical_heat_points = []
    for h in data_repository.historical_withdrawals:
        historical_heat_points.append([h["lat"], h["lng"], 0.65])

    # Inter-state cyber corridors for GIS polyline overlay
    corridors = [
        {
            "id": "CORR-01",
            "name": "Eastern Coastal Cyber Corridor (BBSR-CTC)",
            "start": [20.3168, 85.8234],
            "end": [20.4625, 85.8828],
            "risk": "CRITICAL",
            "description": "Rapid mule account layering between Bhubaneswar & Cuttack"
        },
        {
            "id": "CORR-02",
            "name": "NCR-Mewat Trans-Border Transit Axis",
            "start": [28.6312, 77.2798],
            "end": [28.1065, 77.0042],
            "risk": "CRITICAL",
            "description": "Sim-box operation base linking East Delhi to Nuh-Alwar border"
        },
        {
            "id": "CORR-03",
            "name": "Jamtara-Deoghar Cash Extraction Arc",
            "start": [23.9632, 86.8014],
            "end": [24.4826, 86.6976],
            "risk": "HIGH",
            "description": "Tri-border rural ATM cashout network"
        }
    ]

    return {
        "status": "success",
        "horizon": horizon,
        "total_predicted_hotspots": len(preds),
        "predicted_hotspots": preds,
        "predicted_heat_points": predicted_heat_points,
        "total_historical_events": len(data_repository.historical_withdrawals),
        "historical_clusters": data_repository.historical_withdrawals,
        "historical_heat_points": historical_heat_points,
        "corridors": corridors
    }

@router.get("/atms")
def get_atm_terminals(cluster_id: Optional[str] = None):
    atms = data_repository.atms
    if cluster_id and cluster_id != "All":
        atms = [a for a in atms if a["cluster_id"] == cluster_id]
    
    return {
        "status": "success",
        "total": len(atms),
        "atms": atms
    }
