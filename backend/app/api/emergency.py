from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database.repository import data_repository

router = APIRouter(prefix="/api/emergency", tags=["Emergency Response & 112 Integration"])

class EmergencyEscalationRequest(BaseModel):
    alert_id: str
    operator_notes: Optional[str] = "Immediate threat to public funds. Rapid field interception requested via 112 Emergency System."
    authorized_confirmation: bool = True

@router.get("/contacts")
def get_emergency_contacts():
    """Returns emergency response directory and jurisdiction units."""
    return {
        "emergency_number": "112",
        "emergency_system_name": "Emergency Response Support System (ERSS - 112)",
        "service_status": "AVAILABLE // OPERATIONAL",
        "directory": [
            {
                "category": "National Emergency Command",
                "name": "ERSS 112 National / State Control Room",
                "contact": "112",
                "jurisdiction": "All India Unified Emergency Support",
                "response_time_sla": "< 12 Minutes"
            },
            {
                "category": "Odisha Cyber Operations",
                "name": "Bhubaneswar Police Commissionerate Cyber Cell",
                "contact": "+91 674-XXXX-100",
                "jurisdiction": "Khordha & Cuttack Urban",
                "response_time_sla": "< 15 Minutes"
            },
            {
                "category": "I4C National Coordination",
                "name": "Indian Cyber Crime Coordination Centre (I4C) Desk",
                "contact": "+91 11-XXXX-1930",
                "jurisdiction": "Central & Inter-State",
                "response_time_sla": "Immediate Direct Feed"
            },
            {
                "category": "State Bank of India Fraud Risk",
                "name": "SBI Nodal Cyber Security Incident Response Team (CSIRT)",
                "contact": "+91 22-XXXX-4000",
                "jurisdiction": "Core Banking & ATM Operations",
                "response_time_sla": "< 5 Minutes (Automated Hold)"
            },
            {
                "category": "HDFC Bank Fraud Risk",
                "name": "HDFC Central Cyber Fraud Risk Operations",
                "contact": "+91 22-XXXX-5000",
                "jurisdiction": "Core Banking & ATM Operations",
                "response_time_sla": "< 5 Minutes (Automated Hold)"
            }
        ]
    }

@router.get("/incidents")
def get_emergency_incidents():
    """Returns all 112 emergency escalation records."""
    return {
        "status": "success",
        "total": len(data_repository.emergency_incidents),
        "incidents": data_repository.emergency_incidents
    }

@router.post("/escalate")
def escalate_to_112(req: EmergencyEscalationRequest):
    """
    Authorized human-in-the-loop escalation to 112 ERSS.
    Validates confirmation and creates official incident record.
    """
    if not req.authorized_confirmation:
        raise HTTPException(
            status_code=400,
            detail="Safety Rule Violation: 112 Emergency dispatch requires explicit human operator confirmation."
        )

    incident = data_repository.escalate_emergency_112(
        alert_id=req.alert_id,
        operator_notes=req.operator_notes
    )

    return {
        "status": "success",
        "message": f"Emergency Incident {incident['incident_id']} logged and dispatched to ERSS 112 and District Quick Response Team.",
        "incident": incident
    }
