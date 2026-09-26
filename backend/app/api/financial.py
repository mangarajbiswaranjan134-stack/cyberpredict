from fastapi import APIRouter
from ..database.repository import data_repository

router = APIRouter(prefix="/api/financial", tags=["Financial Intelligence"])

@router.get("/metrics")
def get_financial_intelligence():
    """Returns financial fraud intelligence and fund recovery metrics."""
    complaints = data_repository.complaints
    total_reported = sum(c["loss_amount"] for c in complaints)
    
    # Financial cyber fraud metrics based on Indian banking pattern
    potentially_recoverable = total_reported * 0.42
    blocked_amount = total_reported * 0.28
    recovered_amount = total_reported * 0.16
    pending_amount = total_reported - (blocked_amount + recovered_amount)

    high_risk_accounts = [
        {"account": "SBINXXXXXX8932", "bank": "SBI", "mule_layer": "Layer 1", "linked_cases": 18, "inflow_inr": 4250000, "status": "FROZEN_NODAL"},
        {"account": "HDFCXXXXXX4198", "bank": "HDFC Bank", "mule_layer": "Layer 2", "linked_cases": 12, "inflow_inr": 3100000, "status": "MONITORED_GEOFENCE"},
        {"account": "ICICXXXXXX7812", "bank": "ICICI Bank", "mule_layer": "Layer 2", "linked_cases": 9, "inflow_inr": 2850000, "status": "FLAGGED_I4C"},
        {"account": "PUNBXXXXXX9014", "bank": "PNB", "mule_layer": "Layer 1", "linked_cases": 14, "inflow_inr": 3600000, "status": "FROZEN_NODAL"},
        {"account": "BARBXXXXXX3321", "bank": "Bank of Baroda", "mule_layer": "Layer 3", "linked_cases": 7, "inflow_inr": 1900000, "status": "ACTIVE_INVESTIGATION"}
    ]

    bank_breakdown = [
        {"bank": "State Bank of India", "reported_crores": 5.4, "blocked_crores": 1.9, "recovery_rate": "35.2%"},
        {"bank": "HDFC Bank", "reported_crores": 4.1, "blocked_crores": 1.4, "recovery_rate": "34.1%"},
        {"bank": "ICICI Bank", "reported_crores": 3.6, "blocked_crores": 1.1, "recovery_rate": "30.5%"},
        {"bank": "Punjab National Bank", "reported_crores": 3.2, "blocked_crores": 0.9, "recovery_rate": "28.1%"},
        {"bank": "Axis Bank", "reported_crores": 2.4, "blocked_crores": 0.8, "recovery_rate": "33.3%"}
    ]

    # Money flow stages for Sankey / Bar visualization
    flow_stages = [
        {"stage": "1. Citizen Loss Reported", "amount_inr": round(total_reported, 2), "amount_cr": round(total_reported / 10000000.0, 2)},
        {"stage": "2. Layer-1 Mule Deposit", "amount_inr": round(total_reported * 0.85, 2), "amount_cr": round((total_reported * 0.85) / 10000000.0, 2)},
        {"stage": "3. Layer-2 Inter-Bank Split", "amount_inr": round(total_reported * 0.65, 2), "amount_cr": round((total_reported * 0.65) / 10000000.0, 2)},
        {"stage": "4. Proactively Blocked Funds", "amount_inr": round(blocked_amount, 2), "amount_cr": round(blocked_amount / 10000000.0, 2)},
        {"stage": "5. Forecasted Cashout Exposure", "amount_inr": round(potentially_recoverable, 2), "amount_cr": round(potentially_recoverable / 10000000.0, 2)}
    ]

    return {
        "status": "success",
        "total_reported_inr": round(total_reported, 2),
        "total_reported_crores": round(total_reported / 10000000.0, 2),
        "potentially_recoverable_crores": round(potentially_recoverable / 10000000.0, 2),
        "blocked_amount_crores": round(blocked_amount / 10000000.0, 2),
        "recovered_amount_crores": round(recovered_amount / 10000000.0, 2),
        "pending_exposure_crores": round(pending_amount / 10000000.0, 2),
        "high_risk_accounts": high_risk_accounts,
        "bank_breakdown": bank_breakdown,
        "flow_stages": flow_stages
    }
