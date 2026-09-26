from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from ..database.repository import data_repository

router = APIRouter(prefix="/api/bank", tags=["Bank / Financial-Institution (FI) Intelligence"])

class BankFreezeRequest(BaseModel):
    account_number: str
    bank_name: str
    mule_layer: str = "Layer 2"
    requested_by: str = "Authorized Bank Risk Officer"
    reason: str = "Automated proactive freeze based on predictive cashout hotspot forecast."

@router.get("/dashboard")
def get_bank_intelligence_dashboard():
    """
    Dedicated Bank / FI Intelligence View:
    Provides high-risk withdrawal zones, ATM clusters, suspicious transaction velocity,
    and simulated Citizen Financial Cyber Fraud Reporting System fund recovery metrics.
    """
    preds = data_repository.predictions
    total_exposure = sum(p["estimated_exposure"] for p in preds)

    # Bank-specific risk mapping
    partner_banks = [
        {
            "bank_name": "State Bank of India",
            "active_hotspot_clusters": 5,
            "monitored_atms": 68,
            "estimated_cashout_risk_lakhs": 48.5,
            "simulated_blocked_inr": 1850000.0,
            "nodal_officer": "DGM CSIRT, SBI Global IT Centre",
            "status": "ELEVATED_SURVEILLANCE"
        },
        {
            "bank_name": "HDFC Bank",
            "active_hotspot_clusters": 4,
            "monitored_atms": 42,
            "estimated_cashout_risk_lakhs": 38.2,
            "simulated_blocked_inr": 1400000.0,
            "nodal_officer": "Central Fraud Risk Ops, HDFC Bank",
            "status": "ELEVATED_SURVEILLANCE"
        },
        {
            "bank_name": "ICICI Bank",
            "active_hotspot_clusters": 3,
            "monitored_atms": 34,
            "estimated_cashout_risk_lakhs": 29.0,
            "simulated_blocked_inr": 1100000.0,
            "nodal_officer": "Nodal Fraud Monitoring Unit, ICICI",
            "status": "NORMAL_MONITORING"
        },
        {
            "bank_name": "Punjab National Bank",
            "active_hotspot_clusters": 3,
            "monitored_atms": 28,
            "estimated_cashout_risk_lakhs": 22.4,
            "simulated_blocked_inr": 850000.0,
            "nodal_officer": "Cyber Fraud Cell, PNB Head Office",
            "status": "NORMAL_MONITORING"
        }
    ]

    recovery_metrics = {
        "reported_loss_crores": 18.7,
        "potential_exposure_crores": round(total_exposure / 100.0, 2),
        "flagged_in_transit_crores": 5.2,
        "blocked_simulated_crores": 3.8,
        "recovered_simulated_crores": 1.9,
        "pending_exposure_crores": 7.8,
        "disclaimer": "Prototype / Simulated Integration — Simulated Core Banking Response"
    }

    flagged_accounts = [
        {"account": "SBINXXXXXX8932", "bank": "SBI", "mule_layer": "Layer 1", "cluster": "Bhubaneswar #27", "inflow": 485000, "status": "HOLD_PLACED"},
        {"account": "HDFCXXXXXX4198", "bank": "HDFC Bank", "mule_layer": "Layer 2", "cluster": "Bhubaneswar #27", "inflow": 380000, "status": "HOLD_PENDING"},
        {"account": "ICICXXXXXX7812", "bank": "ICICI Bank", "mule_layer": "Layer 2", "cluster": "Bhubaneswar #27", "inflow": 320000, "status": "FLAGGED_I4C"},
        {"account": "PUNBXXXXXX9014", "bank": "PNB", "mule_layer": "Layer 1", "cluster": "Mewat Corridor", "inflow": 290000, "status": "HOLD_PLACED"},
        {"account": "BARBXXXXXX3321", "bank": "Bank of Baroda", "mule_layer": "Layer 3", "cluster": "Surat Nexus", "inflow": 180000, "status": "MONITORED"}
    ]

    return {
        "status": "success",
        "integration_notice": "Prototype / Simulated Integration — Simulated Core Banking Response",
        "recovery_funnel": recovery_metrics,
        "partner_banks": partner_banks,
        "flagged_accounts": flagged_accounts,
        "active_advisories": data_repository.bank_freeze_advisories
    }

@router.post("/freeze")
def issue_bank_freeze_advisory(req: BankFreezeRequest):
    """
    Simulates sending an automated Layer-2/Layer-3 fund blocking directive
    to the participating bank's Core Banking System.
    """
    record = data_repository.simulate_bank_freeze_advisory(
        account_number=req.account_number,
        bank_name=req.bank_name,
        requested_by=req.requested_by
    )
    return {
        "status": "success",
        "message": f"Simulated fund blocking hold placed on account {req.account_number} ({req.bank_name}).",
        "record": record
    }
