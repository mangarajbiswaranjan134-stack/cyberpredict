from fastapi import APIRouter, Query, HTTPException, Depends, status
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any
from ..database.repository import data_repository
from .security import get_current_user

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

class ComplaintCreateRequest(BaseModel):
    crime_category: str = Field(..., example="UPI Fraud")
    victim_name: str = Field(..., example="Sunil K. Patnaik")
    victim_mobile: Optional[str] = Field("+91 98XXXX2314", example="+91 98XXXX2314")
    victim_phone: Optional[str] = None
    victim_city: Optional[str] = "Bhubaneswar"
    victim_account: Optional[str] = Field("SBINXXXXXX9921", example="SBINXXXXXX9921")
    victim_bank: Optional[str] = Field("State Bank of India", example="State Bank of India")
    loss_amount: Optional[float] = None
    amount_lost_inr: Optional[float] = None
    loss_type: Optional[str] = "Direct Transfer"
    beneficiary_account: Optional[str] = Field("HDFCXXXXXX4198", example="HDFCXXXXXX4198")
    beneficiary_bank: Optional[str] = Field("HDFC Bank", example="HDFC Bank")
    beneficiary_upi: Optional[str] = Field("instant.mule27@hdfc", example="instant.mule27@hdfc")
    beneficiary_ifsc: Optional[str] = Field("HDFC0001024", example="HDFC0001024")
    state: str = Field("Odisha", example="Odisha")
    district: str = Field("Khordha", example="Khordha")
    lat: Optional[float] = None
    latitude: Optional[float] = None
    lng: Optional[float] = None
    longitude: Optional[float] = None
    is_synthetic: Optional[bool] = Field(False, example=False)

    @model_validator(mode="before")
    @classmethod
    def reconcile_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "loss_amount" not in values or values["loss_amount"] is None:
                values["loss_amount"] = values.get("amount_lost_inr", 100000.0)
            if "lat" not in values or values["lat"] is None:
                values["lat"] = values.get("latitude", 20.3533)
            if "lng" not in values or values["lng"] is None:
                values["lng"] = values.get("longitude", 85.8266)
            if "victim_mobile" not in values or values["victim_mobile"] is None:
                values["victim_mobile"] = values.get("victim_phone", "+91 98XXXX2314")
        return values

@router.get("/")
def get_complaints(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    crime_category: Optional[str] = None,
    risk_level: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    search: Optional[str] = None
):
    filtered = data_repository.complaints

    if crime_category and crime_category != "All":
        filtered = [c for c in filtered if c["crime_category"].lower() == crime_category.lower()]

    if risk_level and risk_level != "All":
        filtered = [c for c in filtered if c["risk_level"].upper() == risk_level.upper()]

    if state and state != "All":
        filtered = [c for c in filtered if c["state"].lower() == state.lower()]

    if district and district != "All":
        filtered = [c for c in filtered if c["district"].lower() == district.lower()]

    if search:
        s = search.lower()
        filtered = [
            c for c in filtered
            if s in c["id"].lower()
            or s in c.get("case_reference", "").lower()
            or s in c.get("victim_name", "").lower()
            or s in c.get("victim_account", "").lower()
            or s in c.get("beneficiary_account", "").lower()
            or s in c.get("state", "").lower()
            or s in c.get("district", "").lower()
        ]

    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    items = filtered[start:end]

    return {
        "status": "success",
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "data": items
    }

@router.get("/summary")
def get_complaints_summary():
    complaints = data_repository.complaints
    total_count = len(complaints)
    total_loss = sum(c["loss_amount"] for c in complaints)
    
    by_category = {}
    by_risk = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    by_state = {}

    for c in complaints:
        cat = c["crime_category"]
        by_category[cat] = by_category.get(cat, 0) + 1
        
        r = c["risk_level"]
        if r in by_risk:
            by_risk[r] += 1
            
        st = c["state"]
        by_state[st] = by_state.get(st, 0) + 1

    return {
        "status": "success",
        "total_complaints": total_count,
        "total_loss_inr": round(total_loss, 2),
        "total_loss_crores": round(total_loss / 10000000.0, 2),
        "by_risk": by_risk,
        "by_category": by_category,
        "by_state": by_state
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
def submit_complaint(req: ComplaintCreateRequest, user: dict = Depends(get_current_user)):
    """
    Submits a new cybercrime complaint into the system:
    1. Validates input fields
    2. Stores in PostgreSQL database
    3. Triggers predictive ML engine risk recalculation
    4. Updates advance cashout forecasts and alerts
    5. Dispatches real-time WebSocket event
    """
    try:
        c_dict = req.model_dump()
        result = data_repository.create_complaint(c_dict)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing complaint: {str(e)}"
        )

@router.get("/{complaint_id}")
def get_complaint_by_id(complaint_id: str):
    complaint = next((c for c in data_repository.complaints if c["id"] == complaint_id), None)
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint '{complaint_id}' not found")
    return {
        "status": "success",
        "complaint": complaint
    }
