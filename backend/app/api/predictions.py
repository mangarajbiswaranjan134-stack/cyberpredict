from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..database.repository import data_repository
from ..ml.predictive_engine import predictive_engine

router = APIRouter(prefix="/api/predictions", tags=["Predictive Intelligence"])

@router.get("/forecast")
def get_withdrawal_forecast(horizon: str = Query("24h", pattern="^(1h|6h|12h|24h)$")):
    """
    Returns advance predictive cash withdrawal forecasts across all ATM clusters
    for the selected time horizon (Next 1h, 6h, 12h, 24h).
    Answers: 'Where is suspicious cash withdrawal activity most likely to occur next?'
    """
    preds = data_repository.get_predictions_by_horizon(horizon=horizon)
    critical_count = sum(1 for p in preds if p["risk_score"] >= 90)
    high_count = sum(1 for p in preds if 75 <= p["risk_score"] < 90)
    total_exposure = sum(p["estimated_exposure"] for p in preds)
    total_txns = sum(p.get("estimated_transactions", 12) for p in preds)

    return {
        "status": "success",
        "forecast_horizon": horizon,
        "forecast_horizon_label": f"Next {horizon.replace('h', ' Hours') if horizon != '1h' else '1 Hour'}",
        "forecast_statement": "This is a forecast of future risk, not a report of an event that has already occurred.",
        "total_hotspots_monitored": len(preds),
        "critical_zones": critical_count,
        "high_risk_zones": high_count,
        "total_estimated_exposure_lakhs": round(total_exposure, 1),
        "total_estimated_exposure_crores": round(total_exposure / 100.0, 2),
        "total_estimated_transactions": total_txns,
        "predictions": preds
    }

@router.get("/metrics")
def get_model_evaluation_metrics():
    """Returns ML model performance metrics, exact 7-factor feature importances, and feedback metrics."""
    feature_importance = [
        {"feature": "Historical Withdrawal Frequency", "importance": 0.20, "rank": 1, "weight_pct": 20},
        {"feature": "Recent Complaint Density (48h)", "importance": 0.20, "rank": 2, "weight_pct": 20},
        {"feature": "Temporal Risk Pattern Alignment", "importance": 0.15, "rank": 3, "weight_pct": 15},
        {"feature": "Geographic Proximity & Corridor Drift", "importance": 0.15, "rank": 4, "weight_pct": 15},
        {"feature": "Fraud Category Similarity", "importance": 0.10, "rank": 5, "weight_pct": 10},
        {"feature": "Transaction Velocity (Multi-Hop)", "importance": 0.10, "rank": 6, "weight_pct": 10},
        {"feature": "Linked Account / Network Signals", "importance": 0.10, "rank": 7, "weight_pct": 10}
    ]

    # Time-interval risk forecast (00:00 - 23:00)
    interval_curve = [
        {"hour": "00:00", "predicted_risk_level": 22, "risk_category": "LOW", "historical_baseline": 20},
        {"hour": "03:00", "predicted_risk_level": 15, "risk_category": "LOW", "historical_baseline": 18},
        {"hour": "06:00", "predicted_risk_level": 38, "risk_category": "MEDIUM", "historical_baseline": 30},
        {"hour": "09:00", "predicted_risk_level": 55, "risk_category": "MEDIUM", "historical_baseline": 48},
        {"hour": "12:00", "predicted_risk_level": 72, "risk_category": "HIGH", "historical_baseline": 62},
        {"hour": "15:00", "predicted_risk_level": 78, "risk_category": "HIGH", "historical_baseline": 68},
        {"hour": "18:00", "predicted_risk_level": 94, "risk_category": "CRITICAL", "historical_baseline": 80},
        {"hour": "21:00", "predicted_risk_level": 86, "risk_category": "HIGH", "historical_baseline": 74},
        {"hour": "00:00", "predicted_risk_level": 48, "risk_category": "MEDIUM", "historical_baseline": 40}
    ]

    return {
        "status": "success",
        "metrics": predictive_engine.model_metrics,
        "feature_importance": feature_importance,
        "temporal_forecast_curve": interval_curve,
        "evaluation_notice": "Prototype Evaluation — Synthetic Dataset Benchmark. Live Closed-Loop Feedback Active."
    }

@router.get("/{cluster_id}/explain")
def get_hotspot_explanation(cluster_id: str, horizon: str = "24h"):
    """
    Answers: 'WHY THIS LOCATION?'
    Provides Explainable AI (XAI) breakdown with exact 7-factor weights and visual meters.
    """
    preds = data_repository.get_predictions_by_horizon(horizon=horizon)
    pred = next((p for p in preds if p["cluster_id"] == cluster_id or p["id"] == cluster_id), None)
    if not pred:
        # Fallback to default predictions
        pred = next((p for p in data_repository.predictions if p["cluster_id"] == cluster_id or p["id"] == cluster_id), None)
    
    if not pred:
        raise HTTPException(status_code=404, detail="Hotspot not found")

    return {
        "status": "success",
        "hotspot_id": pred["id"],
        "cluster_name": pred["name"],
        "locality": pred["locality"],
        "district": pred["district"],
        "state": pred["state"],
        "risk_score": pred["risk_score"],
        "risk_level": pred["risk_level"],
        "probability_pct": int(pred["prediction_probability"] * 100),
        "forecast_window": pred["forecast_window"],
        "forecast_horizon": pred.get("forecast_horizon", horizon),
        "is_future_forecast": True,
        "forecast_statement": "This is a forecast of future risk, not a report of an event that has already occurred.",
        "rationale_summary": pred["rationale_summary"],
        "factors": pred["factors"],
        "recommended_interventions": pred["recommended_interventions"],
        "evidence_signals": [
            {"label": "Correlated Complaints", "value": f"{pred['linked_complaints_count']} complaints in 48h"},
            {"label": "Estimated Future Txns", "value": f"{pred.get('estimated_transactions', 18)} attempts forecast"},
            {"label": "Linked Mule Accounts", "value": f"{pred['linked_mule_accounts_count']} beneficiary cards"},
            {"label": "Nearby Teller Terminals", "value": f"{pred['nearby_atms_count']} active ATMs"},
            {"label": "Potential Fund Exposure", "value": f"₹{pred['estimated_exposure']} Lakhs"},
            {"label": "Model Certainty", "value": f"{int(pred['model_confidence'] * 100)}% High Confidence"}
        ]
    }
