from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class GeoLocation(BaseModel):
    lat: float
    lng: float
    state: str
    district: str
    locality: str
    pincode: Optional[str] = None

class ATMNode(BaseModel):
    id: str
    name: str
    bank: str
    lat: float
    lng: float
    cluster_id: str
    cluster_name: str
    district: str
    state: str
    historical_withdrawal_volume: float
    surveillance_rating: str  # High, Medium, Low
    is_active: bool = True

class Complaint(BaseModel):
    id: str
    case_reference: str
    complaint_timestamp: str
    crime_category: str  # UPI Fraud, Phishing, Investment Scam, OTP Fraud, SIM Swap, Impersonation
    victim_name: str  # Anonymized / Synthetic
    victim_mobile: str  # Masked e.g. XXXXXX4821
    victim_account: str  # Masked e.g. XXXXXX1294
    victim_bank: str
    loss_amount: float
    beneficiary_account: str  # Masked e.g. XXXXXX8932
    beneficiary_bank: str
    beneficiary_upi: Optional[str] = None
    state: str
    district: str
    lat: float
    lng: float
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    status: str  # Reported, Layer_1_Frozen, Pending_Investigation, Escalated
    nearest_predicted_hotspot_id: Optional[str] = None

class RiskFactorAttribution(BaseModel):
    factor_name: str
    contribution_weight: float  # e.g. 0.20 (20%)
    impact_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    bar_meter: str  # e.g. "█████████" for visual horizontal indicator

class HotspotPrediction(BaseModel):
    id: str
    name: str
    cluster_id: str
    state: str
    district: str
    locality: str
    lat: float
    lng: float
    risk_score: int  # 0 - 100
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    prediction_probability: float  # 0.0 - 1.0
    forecast_window: str  # e.g. "18:00–21:00"
    forecast_horizon: str  # "1h", "6h", "12h", "24h"
    forecast_date: str
    is_future_forecast: bool = True
    estimated_exposure: float  # INR Lakhs
    estimated_transactions: int
    linked_complaints_count: int
    linked_mule_accounts_count: int
    nearby_atms_count: int
    bank_branch_name: Optional[str] = None
    model_confidence: float  # 0.0 - 1.0
    primary_crime_category: str
    rationale_summary: str
    factors: List[RiskFactorAttribution]
    recommended_interventions: List[str]
    last_updated: str
    anomaly_detected: bool = False
    feedback_outcome: Optional[str] = None

class HistoricalWithdrawalEvent(BaseModel):
    id: str
    cluster_id: str
    cluster_name: str
    lat: float
    lng: float
    district: str
    state: str
    amount_withdrawn_inr: float
    timestamp: str
    atm_id: str
    bank: str
    mule_account: str

class AlertRecord(BaseModel):
    id: str
    hotspot_id: str
    cluster_id: str
    title: str
    timestamp: str
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    risk_score: int
    location: str
    district: str
    state: str
    predicted_event: str
    forecast_window: str
    forecast_horizon: str = "24h"
    estimated_exposure_inr: float
    confidence_pct: int
    status: str  # NEW, UNDER REVIEW, ACKNOWLEDGED, ESCALATED, INTERVENTION ACTIVE, RESOLVED, FALSE POSITIVE
    assigned_authority: str
    recommended_action: str
    acknowledged_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    feedback_recorded: bool = False
    feedback_outcome: Optional[str] = None

class ProactiveIntervention(BaseModel):
    id: str
    alert_id: str
    hotspot_id: str
    target_cluster: str
    intervention_type: str  # LEA_PATROL, BANK_FREEZE_NOTICE, ATM_GEO_FENCE, I4C_COORDINATION
    status: str  # PREDICTED, VERIFIED, DISPATCHED, INTERCEPTED, RESOLVED
    initiated_by: str
    initiated_timestamp: str
    affected_banks: List[str]
    police_stations_notified: List[str]
    mule_accounts_flagged: int
    amount_prevented_inr: float
    notes: Optional[str] = None
    timeline_logs: List[Dict[str, str]]

class FeedbackSubmission(BaseModel):
    alert_id: str
    outcome_type: str  # INTERCEPTED_CONFIRMED, PARTIAL_RECOVERY, FALSE_POSITIVE, LOCATION_SHIFTED
    actual_location: Optional[str] = None
    actual_time_window: Optional[str] = None
    amount_recovered_inr: float = 0.0
    officer_notes: str

class AuditLogEntry(BaseModel):
    id: str
    timestamp: str
    actor: str
    action: str  # PREDICTION_GENERATED, ALERT_REVIEWED, INTERVENTION_DISPATCHED, BANK_FREEZE_SENT, OUTCOME_LOGGED
    target_id: str
    details: str

class CaseEntityNode(BaseModel):
    id: str
    label: str
    type: str  # victim, mobile, account, mule_account, atm, location, lea
    details: Dict[str, Any]

class CaseEntityEdge(BaseModel):
    from_node: str
    to_node: str
    label: str
    amount: Optional[float] = None
    timestamp: Optional[str] = None

class InvestigationCase(BaseModel):
    case_id: str
    title: str
    crime_category: str
    total_fraud_amount: float
    status: str
    lead_investigator: str
    assigned_unit: str
    registration_date: str
    last_updated: str
    priority: str
    nodes: List[CaseEntityNode]
    edges: List[CaseEntityEdge]
    timeline: List[Dict[str, str]]

class EmergencyEscalation(BaseModel):
    incident_id: str
    alert_id: str
    hotspot_id: str
    operator_id: str
    timestamp: str
    location: str
    district: str
    state: str
    jurisdiction_lea: str
    contact_112_dispatched: bool
    status: str
    confirmation_notes: str
    timeline: List[Dict[str, str]]

class UserSession(BaseModel):
    username: str
    role: str  # I4C_ADMIN, STATE_LEA, DISTRICT_OFFICER, BANK_ANALYST, INVESTIGATOR
    organization: str
    jurisdiction: str
    badge_number: str
    session_token: str
