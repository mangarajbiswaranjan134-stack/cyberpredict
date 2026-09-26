from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime
from datetime import datetime
from .config import Base

class ComplaintModel(Base):
    __tablename__ = "complaints"

    id = Column(String(64), primary_key=True, index=True)
    case_reference = Column(String(64), index=True, default="CYB-2026-004821")
    complaint_timestamp = Column(String(64), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    crime_category = Column(String(128), index=True, nullable=False)
    victim_name = Column(String(128), nullable=False)
    victim_mobile = Column(String(32), nullable=True)
    victim_account = Column(String(64), nullable=True)
    victim_bank = Column(String(128), nullable=True)
    loss_amount = Column(Float, nullable=False, default=0.0)
    beneficiary_account = Column(String(64), index=True, nullable=True)
    beneficiary_bank = Column(String(128), nullable=True)
    beneficiary_upi = Column(String(128), nullable=True)
    beneficiary_ifsc = Column(String(32), nullable=True)
    state = Column(String(64), index=True, nullable=False)
    district = Column(String(64), index=True, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    risk_level = Column(String(32), default="HIGH")
    status = Column(String(32), default="Reported")
    nearest_predicted_hotspot_id = Column(String(64), nullable=True)
    is_synthetic = Column(Boolean, default=True)
    data_source = Column(String(64), default="DEMO / SYNTHETIC DATA")

class ClusterModel(Base):
    __tablename__ = "clusters"

    cluster_id = Column(String(64), primary_key=True, index=True)
    cluster_name = Column(String(128), nullable=False)
    locality = Column(String(128), nullable=False)
    district = Column(String(64), index=True, nullable=False)
    state = Column(String(64), index=True, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    historic_incident_count = Column(Integer, default=0)
    historical_exposure_inr = Column(Float, default=0.0)
    primary_modus = Column(String(128), default="UPI Fraud")

class ATMModel(Base):
    __tablename__ = "atms"

    id = Column(String(64), primary_key=True, index=True)
    cluster_id = Column(String(64), index=True, nullable=False)
    bank = Column(String(64), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    address = Column(String(256), nullable=True)
    district = Column(String(64), nullable=False)
    state = Column(String(64), nullable=False)
    status = Column(String(32), default="ACTIVE")
    cash_level = Column(String(32), default="NORMAL")

class PredictionModel(Base):
    __tablename__ = "predictions"

    id = Column(String(64), primary_key=True, index=True)
    cluster_id = Column(String(64), index=True, nullable=False)
    name = Column(String(128), nullable=False)
    locality = Column(String(128), nullable=False)
    district = Column(String(64), nullable=False)
    state = Column(String(64), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(32), nullable=False)
    prediction_probability = Column(Float, nullable=False)
    forecast_window = Column(String(64), nullable=False)
    forecast_horizon = Column(String(16), default="24h")
    estimated_exposure = Column(Float, default=0.0)
    estimated_transactions = Column(Integer, default=0)
    model_confidence = Column(Float, default=0.9)
    rationale_summary = Column(Text, nullable=True)
    factors_json = Column(Text, nullable=True)
    recommended_interventions_json = Column(Text, nullable=True)
    is_future_forecast = Column(Boolean, default=True)
    updated_at = Column(String(64), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class AlertModel(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True, index=True)
    hotspot_id = Column(String(64), index=True, nullable=False)
    cluster_id = Column(String(64), index=True, nullable=False)
    title = Column(String(256), nullable=False)
    timestamp = Column(String(64), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    risk_level = Column(String(32), nullable=False)
    risk_score = Column(Integer, nullable=False)
    location = Column(String(256), nullable=False)
    district = Column(String(64), nullable=False)
    state = Column(String(64), nullable=False)
    predicted_event = Column(Text, nullable=True)
    forecast_window = Column(String(64), nullable=False)
    forecast_horizon = Column(String(16), default="24h")
    estimated_exposure_inr = Column(Float, default=0.0)
    confidence_pct = Column(Integer, default=90)
    status = Column(String(32), default="NEW")
    assigned_authority = Column(String(256), nullable=True)
    recommended_action = Column(Text, nullable=True)
    acknowledged_by = Column(String(128), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    feedback_recorded = Column(Boolean, default=False)
    feedback_outcome = Column(String(64), nullable=True)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, index=True)
    timestamp = Column(String(64), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    actor = Column(String(128), nullable=False)
    action = Column(String(128), nullable=False)
    target_id = Column(String(128), nullable=False)
    details = Column(Text, nullable=True)

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role_id = Column(String(64), nullable=False)
    name = Column(String(128), nullable=False)
    jurisdiction = Column(String(128), nullable=False)
    badge = Column(String(64), nullable=False)
    is_active = Column(Boolean, default=True)

class BankFreezeAdvisoryModel(Base):
    __tablename__ = "bank_freeze_advisories"

    advisory_id = Column(String(64), primary_key=True, index=True)
    account_number = Column(String(64), nullable=False)
    bank_name = Column(String(128), nullable=False)
    status = Column(String(64), default="SIMULATED_HOLD_PLACED")
    requested_by = Column(String(128), nullable=False)
    timestamp = Column(String(64), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    latency_ms = Column(Integer, default=340)
    notice = Column(String(256), nullable=True)

class EmergencyIncidentModel(Base):
    __tablename__ = "emergency_incidents"

    incident_id = Column(String(64), primary_key=True, index=True)
    alert_id = Column(String(64), nullable=False)
    hotspot_id = Column(String(64), nullable=False)
    operator_id = Column(String(64), nullable=False)
    timestamp = Column(String(64), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    location = Column(String(256), nullable=False)
    district = Column(String(64), nullable=False)
    state = Column(String(64), nullable=False)
    jurisdiction_lea = Column(String(256), nullable=False)
    contact_112_dispatched = Column(Boolean, default=True)
    status = Column(String(64), default="Escalation_Initiated")
    confirmation_notes = Column(Text, nullable=True)
    timeline_json = Column(Text, nullable=True)

class InterventionModel(Base):
    __tablename__ = "interventions"

    id = Column(String(64), primary_key=True, index=True)
    alert_id = Column(String(64), nullable=False)
    hotspot_id = Column(String(64), nullable=False)
    target_cluster = Column(String(256), nullable=False)
    intervention_type = Column(String(64), nullable=False)
    status = Column(String(64), default="INTERVENTION ACTIVE")
    initiated_by = Column(String(128), nullable=False)
    initiated_timestamp = Column(String(64), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    affected_banks_json = Column(Text, nullable=True)
    police_stations_json = Column(Text, nullable=True)
    mule_accounts_flagged = Column(Integer, default=0)
    amount_prevented_inr = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    timeline_logs_json = Column(Text, nullable=True)
