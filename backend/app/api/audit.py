from fastapi import APIRouter
from ..database.repository import data_repository

router = APIRouter(prefix="/api/audit", tags=["Audit Trail & Incident Log"])

@router.get("/logs")
def get_audit_trail():
    """
    Returns complete chronological audit log of all predictions, alerts,
    interventions, emergency escalations, and outcome feedback.
    """
    return {
        "status": "success",
        "total_events": len(data_repository.audit_logs),
        "logs": data_repository.audit_logs
    }
