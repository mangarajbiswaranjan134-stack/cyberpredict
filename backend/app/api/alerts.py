from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database.repository import data_repository
from ..schemas.models import FeedbackSubmission

router = APIRouter(prefix="/api/alerts", tags=["Real-Time Actionable Alerts"])

class AlertStatusUpdate(BaseModel):
    status: str  # NEW, UNDER REVIEW, ACKNOWLEDGED, ESCALATED, INTERVENTION ACTIVE, RESOLVED, FALSE POSITIVE
    acknowledged_by: Optional[str] = "Authorized Cyber Ops Officer"
    notes: Optional[str] = None

@router.get("/")
def get_alerts(
    risk_level: Optional[str] = None,
    status: Optional[str] = None
):
    alerts = data_repository.alerts

    if risk_level and risk_level != "All":
        alerts = [a for a in alerts if a["risk_level"].upper() == risk_level.upper()]

    if status and status != "All":
        alerts = [a for a in alerts if a["status"].upper() == status.upper()]

    counts = {
        "CRITICAL": sum(1 for a in data_repository.alerts if a["risk_level"] == "CRITICAL"),
        "HIGH": sum(1 for a in data_repository.alerts if a["risk_level"] == "HIGH"),
        "MEDIUM": sum(1 for a in data_repository.alerts if a["risk_level"] == "MEDIUM"),
        "LOW": sum(1 for a in data_repository.alerts if a["risk_level"] == "LOW"),
        "NEW_UNRESOLVED": sum(1 for a in data_repository.alerts if a["status"] in ["NEW", "UNDER REVIEW"]),
        "RESOLVED": sum(1 for a in data_repository.alerts if a["status"] in ["RESOLVED", "FALSE POSITIVE"])
    }

    return {
        "status": "success",
        "counts": counts,
        "total": len(alerts),
        "alerts": alerts
    }

@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str, update: AlertStatusUpdate):
    alert = next((a for a in data_repository.alerts if a["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    old_status = alert["status"]
    alert["status"] = update.status.upper()
    alert["acknowledged_by"] = update.acknowledged_by
    if update.notes:
        alert["resolution_notes"] = update.notes

    # Add to Audit Trail
    data_repository.add_audit_log(
        actor=update.acknowledged_by,
        action="ALERT_STATUS_UPDATED",
        target_id=alert_id,
        details=f"Alert status transitioned from [{old_status}] to [{update.status.upper()}]. Notes: {update.notes or 'None'}"
    )

    return {
        "status": "success",
        "message": f"Alert {alert_id} updated to {update.status}",
        "alert": alert
    }

@router.post("/{alert_id}/feedback")
def submit_alert_feedback(alert_id: str, feedback: FeedbackSubmission):
    """
    Feedback Loop: Submits real-world incident outcome and feeds back into the ML predictive engine.
    """
    result = data_repository.record_incident_feedback(alert_id=alert_id, feedback_data=feedback.dict())
    return result
