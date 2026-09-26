from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from ..database.repository import data_repository

router = APIRouter(prefix="/api/interventions", tags=["Proactive Interventions"])

class InterventionDispatchPayload(BaseModel):
    alert_id: str
    intervention_type: str  # LEA_PATROL, BANK_FREEZE_NOTICE, ATM_GEO_FENCE, I4C_COORDINATION
    notes: Optional[str] = "Immediate proactive containment dispatched by authorized operator."

@router.get("/")
def list_interventions():
    """Returns all proactive interventions and containment actions."""
    return {
        "status": "success",
        "total": len(data_repository.interventions),
        "interventions": data_repository.interventions
    }

@router.post("/dispatch")
def dispatch_intervention(payload: InterventionDispatchPayload):
    """Executes a proactive multi-agency intervention (Police + Bank + ATM)."""
    record = data_repository.dispatch_intervention(
        alert_id=payload.alert_id,
        intervention_type=payload.intervention_type,
        notes=payload.notes
    )
    return {
        "status": "success",
        "message": f"Proactive intervention {record['id']} successfully dispatched.",
        "intervention": record
    }
