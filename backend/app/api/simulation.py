from fastapi import APIRouter
from ..database.repository import data_repository

router = APIRouter(prefix="/api/simulation", tags=["Demo Simulation Engine"])

@router.post("/trigger-surge")
def trigger_cybercrime_surge():
    """
    Triggers live SIH Hackathon demonstration event:
    1. Simulates sudden cluster of 15 complaints in Bhubaneswar ATM Cluster #27
    2. Recalculates ML predictive risk score (spikes to 94-98/100)
    3. Triggers immediate CRITICAL alert
    4. Elevates ATM cashout forecast
    5. Returns diff for immediate UI visual pulse
    """
    result = data_repository.simulate_surge_event()
    return {
        "status": "success",
        "message": "⚡ Live Cybercrime Event Injected! AI Predictive Engine recalculated cashout risk.",
        "payload": result
    }

@router.post("/reset")
def reset_simulation():
    """Resets repository data back to initial clean synthetic baseline."""
    data_repository.initialize_data()
    return {
        "status": "success",
        "message": "System baseline restored to initial synthetic state."
    }
