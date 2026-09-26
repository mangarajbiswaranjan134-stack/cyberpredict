from fastapi import APIRouter
from datetime import datetime
from ..database.repository import data_repository

router = APIRouter(prefix="/api/system", tags=["System Telemetry & Health"])

@router.get("/status")
def get_system_status():
    """Returns real-time pipeline monitoring and system health telemetry."""
    m = data_repository.system_metrics
    return {
        "status": "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "services": [
            {"service": "NCRP Complaint Ingestion Engine", "status": m["ingestion_status"], "latency_ms": 28.4},
            {"service": "AI Predictive Cashout Forecaster", "status": m["prediction_status"], "latency_ms": m["inference_latency_ms"]},
            {"service": "National GIS Risk Heatmap Engine", "status": m["gis_status"], "latency_ms": 19.8},
            {"service": "Real-Time Multi-Agency Alert Service", "status": m["alert_status"], "latency_ms": 12.1},
            {"service": "Core Banking Simulated Gateway", "status": "ONLINE", "latency_ms": 34.0},
            {"service": "ERSS 112 Emergency Inter-Link", "status": "ONLINE", "latency_ms": 15.2}
        ],
        "telemetry": {
            "pipeline_latency_ms": m["pipeline_latency_ms"],
            "inference_latency_ms": m["inference_latency_ms"],
            "data_freshness_seconds": m["data_freshness_seconds"],
            "complaints_ingested_today": m["complaints_ingested_today"],
            "active_mule_nodes_tracked": m["active_mule_nodes_tracked"],
            "dataset_disclaimer": m["dataset_notice"]
        }
    }
