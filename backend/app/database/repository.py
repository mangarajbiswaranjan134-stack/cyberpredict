import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from ..ml.synthetic_generator import generate_synthetic_dataset
from ..ml.predictive_engine import predictive_engine
from .config import engine, SessionLocal, Base, ACTIVE_DB_TYPE, PG_URL, reconnect_db
from .models import (
    ComplaintModel, ClusterModel, ATMModel, PredictionModel, AlertModel,
    AuditLogModel, UserModel, BankFreezeAdvisoryModel, EmergencyIncidentModel,
    InterventionModel
)

logger = logging.getLogger("cyberpredict.repository")

class DataRepository:
    def __init__(self):
        self.complaints: List[Dict[str, Any]] = []
        self.atms: List[Dict[str, Any]] = []
        self.clusters: List[Dict[str, Any]] = []
        self.predictions: List[Dict[str, Any]] = []
        self.historical_withdrawals: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []
        self.interventions: List[Dict[str, Any]] = []
        self.investigations: Dict[str, Any] = {}
        self.emergency_incidents: List[Dict[str, Any]] = []
        self.audit_logs: List[Dict[str, Any]] = []
        self.bank_freeze_advisories: List[Dict[str, Any]] = []
        self.active_horizon: str = "24h"
        self.ws_broadcast_callback: Optional[Callable] = None
        self.system_metrics = {
            "data_freshness_seconds": 1,
            "pipeline_latency_ms": 42.6,
            "inference_latency_ms": 18.2,
            "complaints_ingested_today": 5200,
            "active_mule_nodes_tracked": 1840,
            "ingestion_status": "ONLINE",
            "prediction_status": "ACTIVE",
            "gis_status": "ONLINE",
            "alert_status": "ACTIVE",
            "bank_integration": "SIMULATED_PROD_MODE",
            "dataset_notice": "DEMO / SYNTHETIC DATA"
        }
        self.initialize_data()

    def set_ws_broadcast_callback(self, callback: Callable):
        """Registers WebSocket broadcast callback from main.py."""
        self.ws_broadcast_callback = callback

    def add_audit_log(self, actor: str, action: str, target_id: str, details: str):
        """Appends an immutable audit log entry to memory and PostgreSQL."""
        import uuid
        log_entry = {
            "id": f"AUDIT-{datetime.now().strftime('%H%M%S')}-{uuid.uuid4().hex[:4].upper()}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actor": actor,
            "action": action,
            "target_id": target_id,
            "details": details
        }
        self.audit_logs.insert(0, log_entry)

        # Persist to database
        try:
            with SessionLocal() as session:
                audit_rec = AuditLogModel(
                    id=log_entry["id"],
                    timestamp=log_entry["timestamp"],
                    actor=log_entry["actor"],
                    action=log_entry["action"],
                    target_id=log_entry["target_id"],
                    details=log_entry["details"]
                )
                session.add(audit_rec)
                session.commit()
        except Exception as e:
            logger.error(f"Failed to persist audit log: {e}")

    def initialize_data(self):
        """Seeds initial dataset into PostgreSQL and populates fast in-memory structures."""
        # 1. Create all tables in PostgreSQL
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("[DATABASE] PostgreSQL tables verified and synchronized.")
        except Exception as e:
            logger.error(f"[DATABASE] Schema initialization error: {e}")

        # 2. Generate baseline synthetic data
        data = generate_synthetic_dataset(num_complaints=5200)
        self.clusters = data["clusters"]
        self.atms = data["atms"]
        self.complaints = data["complaints"]

        # 3. Generate Historical Withdrawal Events (Past 7 Days)
        self.historical_withdrawals = []
        now = datetime.now()
        for idx, cluster in enumerate(self.clusters):
            for h_idx in range(4):
                days_ago = (h_idx + 1) * 1.5
                event_time = now - timedelta(days=days_ago, hours=h_idx * 3)
                amt = round(65000 + (idx * 22000) + (h_idx * 15000), 2)
                atm_choice = next((a for a in self.atms if a["cluster_id"] == cluster["cluster_id"]), self.atms[0])
                
                self.historical_withdrawals.append({
                    "id": f"HIST-WDL-{cluster['cluster_id']}-{h_idx+1:02d}",
                    "cluster_id": cluster["cluster_id"],
                    "cluster_name": cluster["cluster_name"],
                    "lat": cluster["lat"] + ((h_idx - 1.5) * 0.004),
                    "lng": cluster["lng"] + ((1.5 - h_idx) * 0.004),
                    "district": cluster["district"],
                    "state": cluster["state"],
                    "amount_withdrawn_inr": amt,
                    "timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "atm_id": atm_choice["id"],
                    "bank": atm_choice["bank"],
                    "mule_account": f"SBINXXXXXX{3000 + idx + h_idx}",
                    "is_historical": True
                })

        # 4. Run predictive engine for default 24h horizon
        self.predictions = predictive_engine.forecast_hotspots(self.clusters, self.complaints, horizon="24h")

        # 5. Generate initial alerts with full 7-status lifecycle
        self.alerts = []
        status_sequence = ["NEW", "UNDER REVIEW", "ACKNOWLEDGED", "ESCALATED", "INTERVENTION ACTIVE", "RESOLVED"]
        for idx, pred in enumerate(self.predictions):
            if pred["risk_score"] >= 72:
                assigned_status = status_sequence[min(idx, len(status_sequence) - 1)]
                self.alerts.append({
                    "id": f"ALT-2026-{1001 + idx}",
                    "hotspot_id": pred["id"],
                    "cluster_id": pred["cluster_id"],
                    "title": f"Future Cashout Threat: {pred['name']}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "risk_level": pred["risk_level"],
                    "risk_score": pred["risk_score"],
                    "location": f"{pred['locality']}, {pred['district']}, {pred['state']}",
                    "district": pred["district"],
                    "state": pred["state"],
                    "predicted_event": f"Forecasted cash withdrawal attempts ({pred['estimated_transactions']} txns) during {pred['forecast_window']}",
                    "forecast_window": pred["forecast_window"],
                    "forecast_horizon": "24h",
                    "estimated_exposure_inr": pred["estimated_exposure"] * 100000.0,
                    "confidence_pct": int(pred["model_confidence"] * 100),
                    "status": assigned_status,
                    "assigned_authority": f"{pred['district']} Cyber Crime Cell & I4C Joint Desk",
                    "recommended_action": pred["recommended_interventions"][0],
                    "acknowledged_by": None if assigned_status == "NEW" else "Insp. S. Pattnaik (Cyber Ops)",
                    "resolution_notes": None,
                    "feedback_recorded": False,
                    "feedback_outcome": None
                })

        # 6. Initialize Investigation Cases & Audit Logs
        self._init_investigation_cases()
        self.audit_logs = [
            {
                "id": "AUDIT-0004",
                "timestamp": (now - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
                "actor": "System AI Ingestion",
                "action": "PREDICTION_GENERATED",
                "target_id": "PRED-OD-BBSR-27",
                "details": "Forecasted Bhubaneswar Cluster #27 as Critical Risk (94/100) for window 20:00–23:00."
            },
            {
                "id": "AUDIT-0003",
                "timestamp": (now - timedelta(minutes=12)).strftime("%Y-%m-%d %H:%M:%S"),
                "actor": "System Engine",
                "action": "ALERT_CREATED",
                "target_id": "ALT-2026-1001",
                "details": "Critical Alert dispatched to Odisha CID Cyber Crime and SBI Nodal Fraud Desk."
            },
            {
                "id": "AUDIT-0002",
                "timestamp": (now - timedelta(minutes=8)).strftime("%Y-%m-%d %H:%M:%S"),
                "actor": "Insp. S. Pattnaik",
                "action": "ALERT_ACKNOWLEDGED",
                "target_id": "ALT-2026-1001",
                "details": "Officer reviewed Explainable AI indicators and approved proactive intervention."
            },
            {
                "id": "AUDIT-0001",
                "timestamp": (now - timedelta(minutes=4)).strftime("%Y-%m-%d %H:%M:%S"),
                "actor": "Officer I4C-9921",
                "action": "INTERVENTION_DISPATCHED",
                "target_id": "INTV-0001",
                "details": "Proactive QRT patrol staged at Patia Tech Corridor; Simulated bank freeze signals sent."
            }
        ]

        # 7. Seed initial records into PostgreSQL if empty
        try:
            with SessionLocal() as session:
                existing_complaints = session.query(ComplaintModel).count()
                if existing_complaints == 0:
                    logger.info("[DATABASE] Seeding initial clusters, atms, and complaints into PostgreSQL...")
                    # Seed clusters
                    for cl in self.clusters:
                        session.merge(ClusterModel(
                            cluster_id=cl["cluster_id"],
                            cluster_name=cl["cluster_name"],
                            locality=cl["locality"],
                            district=cl["district"],
                            state=cl["state"],
                            lat=cl["lat"],
                            lng=cl["lng"],
                            historic_incident_count=cl.get("historic_incident_count", 0),
                            historical_exposure_inr=cl.get("historical_exposure_inr", 0.0),
                            primary_modus=cl.get("primary_modus", "UPI Fraud")
                        ))
                    # Seed atms
                    for atm in self.atms[:50]:
                        session.merge(ATMModel(
                            id=atm["id"],
                            cluster_id=atm["cluster_id"],
                            bank=atm["bank"],
                            lat=atm["lat"],
                            lng=atm["lng"],
                            address=atm.get("address", ""),
                            district=atm["district"],
                            state=atm["state"],
                            status=atm.get("status", "ACTIVE")
                        ))
                    # Seed top complaints
                    for c in self.complaints[:200]:
                        session.merge(ComplaintModel(
                            id=c["id"],
                            case_reference=c.get("case_reference", "CYB-2026-004821"),
                            complaint_timestamp=c.get("complaint_timestamp", now.strftime("%Y-%m-%d %H:%M:%S")),
                            crime_category=c.get("crime_category", "UPI Fraud"),
                            victim_name=c.get("victim_name", "Anonymous"),
                            victim_mobile=c.get("victim_mobile", ""),
                            victim_account=c.get("victim_account", ""),
                            victim_bank=c.get("victim_bank", ""),
                            loss_amount=c.get("loss_amount", 50000.0),
                            beneficiary_account=c.get("beneficiary_account", ""),
                            beneficiary_bank=c.get("beneficiary_bank", ""),
                            beneficiary_upi=c.get("beneficiary_upi", ""),
                            state=c.get("state", "Odisha"),
                            district=c.get("district", "Khordha"),
                            lat=c.get("lat", 20.2961),
                            lng=c.get("lng", 85.8245),
                            risk_level=c.get("risk_level", "HIGH"),
                            status=c.get("status", "Reported"),
                            is_synthetic=True,
                            data_source="DEMO / SYNTHETIC DATA"
                        ))
                    session.commit()
                    logger.info("[DATABASE] PostgreSQL successfully seeded with baseline records.")
        except Exception as e:
            logger.error(f"[DATABASE] Error during database seed: {e}")

    def create_complaint(self, c_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests a real complaint from the API / UI:
        1. Stores in PostgreSQL database
        2. Recalculates predictive risk scores using ML engine
        3. Updates predicted hotspots in DB
        4. Generates alert when risk threshold is crossed
        5. Dispatches real-time WebSocket broadcast event
        """
        now = datetime.now()
        comp_id = c_data.get("id") or f"NCRP-LIVE-{now.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        
        # Calculate nearest cluster based on latitude/longitude
        lat = float(c_data.get("lat", 20.3533))
        lng = float(c_data.get("lng", 85.8266))
        nearest_cluster = min(
            self.clusters,
            key=lambda cl: ((cl["lat"] - lat)**2 + (cl["lng"] - lng)**2)
        )
        
        is_synthetic = c_data.get("is_synthetic", False)
        data_source = "DEMO / SYNTHETIC DATA" if is_synthetic else "PUBLIC REAL DATA"

        complaint = {
            "id": comp_id,
            "case_reference": c_data.get("case_reference", "CYB-2026-LIVE"),
            "complaint_timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "crime_category": c_data.get("crime_category", "UPI Fraud"),
            "victim_name": c_data.get("victim_name", "Citizen Complainant"),
            "victim_mobile": c_data.get("victim_mobile", "+91 98XXXX0000"),
            "victim_account": c_data.get("victim_account", "SBINXXXXXX9999"),
            "victim_bank": c_data.get("victim_bank", "State Bank of India"),
            "loss_amount": float(c_data.get("loss_amount", 75000.0)),
            "beneficiary_account": c_data.get("beneficiary_account", "HDFCXXXXXX4198"),
            "beneficiary_bank": c_data.get("beneficiary_bank", "HDFC Bank"),
            "beneficiary_upi": c_data.get("beneficiary_upi", "mule.beneficiary@upi"),
            "beneficiary_ifsc": c_data.get("beneficiary_ifsc", "HDFC0001024"),
            "state": c_data.get("state", nearest_cluster["state"]),
            "district": c_data.get("district", nearest_cluster["district"]),
            "lat": round(lat, 5),
            "lng": round(lng, 5),
            "risk_level": "CRITICAL" if float(c_data.get("loss_amount", 0)) > 150000 else "HIGH",
            "status": "Under Investigation",
            "nearest_predicted_hotspot_id": nearest_cluster["cluster_id"],
            "is_synthetic": is_synthetic,
            "data_source": data_source
        }

        # 1. Add to in-memory complaints list
        self.complaints.insert(0, complaint)

        # 2. Persist to PostgreSQL
        try:
            with SessionLocal() as session:
                comp_model = ComplaintModel(
                    id=complaint["id"],
                    case_reference=complaint["case_reference"],
                    complaint_timestamp=complaint["complaint_timestamp"],
                    crime_category=complaint["crime_category"],
                    victim_name=complaint["victim_name"],
                    victim_mobile=complaint["victim_mobile"],
                    victim_account=complaint["victim_account"],
                    victim_bank=complaint["victim_bank"],
                    loss_amount=complaint["loss_amount"],
                    beneficiary_account=complaint["beneficiary_account"],
                    beneficiary_bank=complaint["beneficiary_bank"],
                    beneficiary_upi=complaint["beneficiary_upi"],
                    beneficiary_ifsc=complaint["beneficiary_ifsc"],
                    state=complaint["state"],
                    district=complaint["district"],
                    lat=complaint["lat"],
                    lng=complaint["lng"],
                    risk_level=complaint["risk_level"],
                    status=complaint["status"],
                    nearest_predicted_hotspot_id=complaint["nearest_predicted_hotspot_id"],
                    is_synthetic=complaint["is_synthetic"],
                    data_source=complaint["data_source"]
                )
                session.add(comp_model)
                session.commit()
                logger.info(f"[DATABASE] Stored complaint {complaint['id']} in PostgreSQL.")
        except Exception as e:
            logger.error(f"[DATABASE] Error saving complaint to PostgreSQL: {e}")

        # 3. Recalculate predictive risk scores using ML engine
        self.predictions = predictive_engine.forecast_hotspots(
            self.clusters, self.complaints, horizon=self.active_horizon
        )
        
        # Find updated prediction for the affected cluster
        updated_pred = next(
            (p for p in self.predictions if p["cluster_id"] == nearest_cluster["cluster_id"]),
            self.predictions[0]
        )

        # 4. Generate real alert if risk >= 70
        new_alert = None
        if updated_pred["risk_score"] >= 70:
            new_alert = {
                "id": f"ALT-LIVE-{now.strftime('%H%M%S')}-{uuid.uuid4().hex[:4].upper()}",
                "hotspot_id": updated_pred["id"],
                "cluster_id": updated_pred["cluster_id"],
                "title": f"🚨 Elevated Cashout Threat: {updated_pred['name']}",
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "risk_level": updated_pred["risk_level"],
                "risk_score": updated_pred["risk_score"],
                "location": f"{updated_pred['locality']}, {updated_pred['district']}, {updated_pred['state']}",
                "district": updated_pred["district"],
                "state": updated_pred["state"],
                "predicted_event": f"Forecasted cash extraction window: {updated_pred['forecast_window']}. Correlated with new complaint {comp_id}.",
                "forecast_window": updated_pred["forecast_window"],
                "forecast_horizon": self.active_horizon,
                "estimated_exposure_inr": updated_pred["estimated_exposure"] * 100000.0,
                "confidence_pct": int(updated_pred["model_confidence"] * 100),
                "status": "NEW",
                "assigned_authority": f"{updated_pred['district']} Cyber Command Unit",
                "recommended_action": updated_pred["recommended_interventions"][0],
                "acknowledged_by": None,
                "resolution_notes": None,
                "feedback_recorded": False,
                "feedback_outcome": None
            }
            self.alerts.insert(0, new_alert)

            # Persist alert to PostgreSQL
            try:
                with SessionLocal() as session:
                    alert_model = AlertModel(
                        id=new_alert["id"],
                        hotspot_id=new_alert["hotspot_id"],
                        cluster_id=new_alert["cluster_id"],
                        title=new_alert["title"],
                        timestamp=new_alert["timestamp"],
                        risk_level=new_alert["risk_level"],
                        risk_score=new_alert["risk_score"],
                        location=new_alert["location"],
                        district=new_alert["district"],
                        state=new_alert["state"],
                        predicted_event=new_alert["predicted_event"],
                        forecast_window=new_alert["forecast_window"],
                        forecast_horizon=new_alert["forecast_horizon"],
                        estimated_exposure_inr=new_alert["estimated_exposure_inr"],
                        confidence_pct=new_alert["confidence_pct"],
                        status=new_alert["status"],
                        assigned_authority=new_alert["assigned_authority"],
                        recommended_action=new_alert["recommended_action"]
                    )
                    session.add(alert_model)
                    session.commit()
            except Exception as e:
                logger.error(f"[DATABASE] Error saving alert to PostgreSQL: {e}")

        # 5. Add Audit Log
        self.add_audit_log(
            actor="Citizen / Ingestion API",
            action="COMPLAINT_REGISTERED",
            target_id=complaint["id"],
            details=f"Ingested {complaint['crime_category']} (₹{complaint['loss_amount']:,.2f}). Recalculated {updated_pred['name']} risk score to {updated_pred['risk_score']}/100."
        )

        # 6. Broadcast Real-Time WebSocket Event
        ws_payload = {
            "event": "COMPLAINT_CREATED",
            "type": "COMPLAINT_CREATED",
            "payload": {
                "complaint_id": complaint["id"],
                "risk_level": complaint["risk_level"],
                "amount_lost_inr": complaint["loss_amount"],
                "crime_category": complaint["crime_category"],
                "district": complaint["district"],
                "cluster_id": updated_pred.get("cluster_id"),
                "cluster_name": updated_pred.get("name"),
                "recalculated_risk_score": updated_pred.get("risk_score"),
                "alert_created": new_alert is not None,
                "alert_details": new_alert
            },
            "complaint": complaint,
            "recalculated_prediction": updated_pred,
            "new_alert": new_alert,
            "total_complaints": len(self.complaints),
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        if self.ws_broadcast_callback:
            try:
                self.ws_broadcast_callback(ws_payload)
            except Exception as e:
                logger.warning(f"Could not broadcast WS message: {e}")

        return {
            "status": "success",
            "message": "Complaint successfully processed through predictive pipeline",
            "complaint": complaint,
            "recalculated_hotspot": updated_pred,
            "new_alert": new_alert,
            "total_complaints": len(self.complaints)
        }

    def _init_investigation_cases(self):
        nodes = [
            {"id": "node-v1", "label": "Victim: Ramesh Nayak", "type": "victim", "details": {"phone": "+91 94XXXX2819", "reported": "₹4,85,000", "city": "Cuttack"}},
            {"id": "node-v2", "label": "Victim: Sunita Mohanty", "type": "victim", "details": {"phone": "+91 98XXXX9102", "reported": "₹2,50,000", "city": "Bhubaneswar"}},
            {"id": "node-m1", "label": "Mule Phone: +91 88XXXX4821", "type": "mobile", "details": {"carrier": "Airtel", "imei": "8641200XXXX4912", "location": "Patia, BBSR"}},
            {"id": "node-a1", "label": "L1 Mule: SBINXXXXXX8932", "type": "account", "details": {"bank": "SBI", "holder": "Binod K. Sahoo", "balance": "₹32,400"}},
            {"id": "node-a2", "label": "L2 Mule: HDFCXXXXXX4198", "type": "mule_account", "details": {"bank": "HDFC", "holder": "Deepak Jena", "balance": "₹4,12,000"}},
            {"id": "node-a3", "label": "L3 Mule: ICICXXXXXX7812", "type": "mule_account", "details": {"bank": "ICICI", "holder": "M/s Maa Sarala Traders", "balance": "₹2,90,500"}},
            {"id": "node-atm1", "label": "ATM: SBI Chandrasekharpur #02", "type": "atm", "details": {"id": "ATM-OD-BBSR-27-01", "cash_status": "Active", "surveillance": "High"}},
            {"id": "node-atm2", "label": "ATM: HDFC Infocity Gate #01", "type": "atm", "details": {"id": "ATM-OD-BBSR-27-04", "cash_status": "Active", "surveillance": "High"}},
            {"id": "node-loc", "label": "Predicted Hotspot: BBSR #27", "type": "location", "details": {"risk_score": 94, "window": "20:00–23:00", "state": "Odisha"}},
            {"id": "node-lea", "label": "LEA: Odisha CID Cyber Crime", "type": "lea", "details": {"status": "Patrol Dispatched", "officer": "DSP M. Behera"}}
        ]
        edges = [
            {"from": "node-v1", "to": "node-a1", "label": "₹4.85L (UPI Txn)", "amount": 485000},
            {"from": "node-v2", "to": "node-a1", "label": "₹2.50L (UPI Txn)", "amount": 250000},
            {"from": "node-a1", "to": "node-m1", "label": "Registered SIM", "amount": None},
            {"from": "node-a1", "to": "node-a2", "label": "₹3.80L (IMPS Split)", "amount": 380000},
            {"from": "node-a1", "to": "node-a3", "label": "₹3.20L (RTGS Transfer)", "amount": 320000},
            {"from": "node-a2", "to": "node-atm1", "label": "Target Cashout (Forecasted)", "amount": 150000},
            {"from": "node-a3", "to": "node-atm2", "label": "Target Cashout (Forecasted)", "amount": 180000},
            {"from": "node-atm1", "to": "node-loc", "label": "ATM Cluster Node", "amount": None},
            {"from": "node-atm2", "to": "node-loc", "label": "ATM Cluster Node", "amount": None},
            {"from": "node-loc", "to": "node-lea", "label": "Intervention Alert Issued", "amount": None}
        ]
        timeline = [
            {"time": "14:22:10", "event": "Citizen complaint registered on NCRP by Ramesh N. (Loss ₹4.85L via fraudulent investment link)."},
            {"time": "14:45:33", "event": "Correlated complaint registered by Sunita M. targeting identical beneficiary SBINXXXXXX8932."},
            {"time": "16:10:04", "event": "AI Pattern Engine detected rapid multi-hop split to HDFC & ICICI mule accounts."},
            {"time": "17:35:12", "event": "Predictive Engine elevated Bhubaneswar Cluster #27 risk score to 94/100 for advance window 20:00–23:00."},
            {"time": "17:40:00", "event": "Proactive Alert ALT-2026-1001 generated; Nodal bank freezing advisories initiated."},
            {"time": "18:15:20", "event": "Quick Response Team (QRT) assigned from Chandrasekharpur Police Station."}
        ]
        self.investigations["CYB-2026-004821"] = {
            "case_id": "CYB-2026-004821",
            "title": "Operation Chhaya: Organized Multi-Hop Investment & ATM Cashout Syndicate",
            "crime_category": "UPI & Investment Fraud",
            "total_fraud_amount": 735000.0,
            "status": "Action Initiated",
            "lead_investigator": "DSP Manas Behera (Odisha CID-CB)",
            "assigned_unit": "Special Cyber Task Force & I4C Joint Cell",
            "registration_date": "2026-09-08",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "priority": "CRITICAL",
            "nodes": nodes,
            "edges": edges,
            "timeline": timeline
        }

    def get_investigation_case(self, case_id: str = "CYB-2026-004821") -> Dict[str, Any]:
        return self.investigations.get(case_id, self.investigations.get("CYB-2026-004821", {}))

    def get_predictions_by_horizon(self, horizon: str = "24h") -> List[Dict[str, Any]]:
        self.active_horizon = horizon
        return predictive_engine.forecast_hotspots(self.clusters, self.complaints, horizon=horizon)

    def get_all_hotspots(self, horizon: str = "24h") -> List[Dict[str, Any]]:
        return self.get_predictions_by_horizon(horizon)

    def record_incident_feedback(self, alert_id: str, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        alert = next((a for a in self.alerts if a["id"] == alert_id), None)
        outcome_type = feedback_data.get("outcome_type", "INTERCEPTED_CONFIRMED")
        amount_saved = feedback_data.get("amount_recovered_inr", 0.0)
        notes = feedback_data.get("officer_notes", "Resolution confirmed by field officer.")

        if alert:
            if outcome_type == "FALSE_POSITIVE":
                alert["status"] = "FALSE POSITIVE"
            else:
                alert["status"] = "RESOLVED"
            alert["feedback_recorded"] = True
            alert["feedback_outcome"] = outcome_type
            alert["resolution_notes"] = f"Outcome: {outcome_type} — {notes}"

        cluster_id = alert["cluster_id"] if alert else "OD-BBSR-27"
        predictive_engine.apply_feedback_learning(cluster_id, outcome_type, amount_saved)

        self.add_audit_log(
            actor="Lead Cyber Investigator",
            action="OUTCOME_FEEDBACK_LOGGED",
            target_id=alert_id,
            details=f"Incident resolved as [{outcome_type}]. Prevented ₹{amount_saved:,.2f}. Model learning weights updated."
        )

        return {
            "status": "success",
            "alert_id": alert_id,
            "outcome_type": outcome_type,
            "model_updated": True,
            "current_metrics": predictive_engine.model_metrics
        }

    def simulate_bank_freeze_advisory(self, account_number: str, bank_name: str, requested_by: str) -> Dict[str, Any]:
        now = datetime.now()
        record = {
            "advisory_id": f"BNK-FRZ-{now.strftime('%H%M%S')}",
            "account_number": account_number,
            "bank_name": bank_name,
            "status": "SIMULATED_HOLD_PLACED",
            "requested_by": requested_by,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "latency_ms": 340,
            "notice": "Simulated Citizen Financial Cyber Fraud Reporting System (1930 / I4C)"
        }
        self.bank_freeze_advisories.insert(0, record)
        
        # Persist to database
        try:
            with SessionLocal() as session:
                rec = BankFreezeAdvisoryModel(
                    advisory_id=record["advisory_id"],
                    account_number=record["account_number"],
                    bank_name=record["bank_name"],
                    status=record["status"],
                    requested_by=record["requested_by"],
                    timestamp=record["timestamp"],
                    latency_ms=record["latency_ms"],
                    notice=record["notice"]
                )
                session.add(rec)
                session.commit()
        except Exception as e:
            logger.error(f"Failed to persist bank freeze advisory: {e}")

        self.add_audit_log(
            actor=requested_by,
            action="SIMULATED_BANK_FREEZE_ISSUED",
            target_id=account_number,
            details=f"Simulated hold advisory placed on {account_number} at {bank_name}."
        )
        return record

    def simulate_surge_event(self) -> Dict[str, Any]:
        now = datetime.now()
        target_cluster = self.clusters[0]  # OD-BBSR-27
        new_complaints = []

        for idx in range(15):
            comp_id = f"NCRP-BURST-{now.strftime('%H%M%S')}-{idx+1:02d}"
            amt = round(48000 + (idx * 11500), 2)
            c = {
                "id": comp_id,
                "case_reference": "CYB-2026-004821",
                "complaint_timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "crime_category": "UPI Fraud",
                "victim_name": f"Victim {chr(65 + idx)}.",
                "victim_mobile": f"+91 97XXXX{1000 + idx}",
                "victim_account": f"SBINXXXXXX{2000 + idx}",
                "victim_bank": "State Bank of India",
                "loss_amount": amt,
                "beneficiary_account": "HDFCXXXXXX4198",
                "beneficiary_bank": "HDFC Bank",
                "beneficiary_upi": "instant.mule27@hdfc",
                "state": target_cluster["state"],
                "district": target_cluster["district"],
                "lat": round(target_cluster["lat"] + (idx * 0.0008), 5),
                "lng": round(target_cluster["lng"] - (idx * 0.0008), 5),
                "risk_level": "CRITICAL",
                "status": "Reported",
                "nearest_predicted_hotspot_id": target_cluster["cluster_id"],
                "is_synthetic": True,
                "data_source": "DEMO / SYNTHETIC DATA"
            }
            new_complaints.append(c)
            self.complaints.insert(0, c)

        # Re-run ML predictions with simulation boost
        self.predictions = predictive_engine.forecast_hotspots(
            self.clusters, self.complaints, horizon="6h", simulation_boost_cluster_id="OD-BBSR-27"
        )
        
        top_pred = self.predictions[0]

        # Trigger Critical Alert
        new_alert = {
            "id": f"ALT-LIVE-{now.strftime('%H%M%S')}",
            "hotspot_id": top_pred["id"],
            "cluster_id": top_pred["cluster_id"],
            "title": f"🚨 IMMINENT CASHOUT SURGE: {top_pred['name']}",
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "risk_level": "CRITICAL",
            "risk_score": top_pred["risk_score"],
            "location": f"{top_pred['locality']}, {top_pred['district']}, {top_pred['state']}",
            "district": top_pred["district"],
            "state": top_pred["state"],
            "predicted_event": f"HIGH-PROBABILITY CASHOUT ({top_pred['forecast_window']}) — 15 correlated complaints in 12 mins",
            "forecast_window": top_pred["forecast_window"],
            "forecast_horizon": "6h",
            "estimated_exposure_inr": top_pred["estimated_exposure"] * 100000.0,
            "confidence_pct": int(top_pred["model_confidence"] * 100),
            "status": "NEW",
            "assigned_authority": "Odisha CID Cyber Cell & Bhubaneswar Commissionerate QRT",
            "recommended_action": "Execute immediate geofenced ATM hold and dispatch patrol units to Patia & Chandrasekharpur clusters.",
            "acknowledged_by": None,
            "resolution_notes": None,
            "feedback_recorded": False,
            "feedback_outcome": None
        }
        self.alerts.insert(0, new_alert)

        self.add_audit_log(
            actor="Live Simulation Engine",
            action="SIMULATED_SURGE_INGESTED",
            target_id=top_pred["cluster_id"],
            details=f"Injected 15 burst complaints. ML recalculated risk score to {top_pred['risk_score']}/100. Alert {new_alert['id']} generated."
        )

        self.system_metrics["complaints_ingested_today"] += 15
        self.system_metrics["data_freshness_seconds"] = 1

        # Broadcast WebSocket event
        if self.ws_broadcast_callback:
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.ws_broadcast_callback({
                        "type": "SURGE_SIMULATED",
                        "top_prediction": top_pred,
                        "new_alert": new_alert,
                        "new_complaints_count": len(new_complaints)
                    }))
            except Exception:
                pass

        return {
            "status": "SURGE_SIMULATED",
            "boosted_cluster": top_pred,
            "new_alert": new_alert,
            "new_complaints_count": len(new_complaints),
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
        }

    def dispatch_intervention(self, alert_id: str, intervention_type: str, notes: str) -> Dict[str, Any]:
        alert = next((a for a in self.alerts if a["id"] == alert_id), None)
        now = datetime.now()
        
        intervention = {
            "id": f"INTV-{now.strftime('%H%M%S')}",
            "alert_id": alert_id,
            "hotspot_id": alert["hotspot_id"] if alert else "OD-BBSR-27",
            "target_cluster": alert["location"] if alert else "Bhubaneswar ATM Cluster #27",
            "intervention_type": intervention_type,
            "status": "INTERVENTION ACTIVE",
            "initiated_by": "Authorized Cyber Ops Officer",
            "initiated_timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "affected_banks": ["SBI", "HDFC Bank", "ICICI Bank"],
            "police_stations_notified": ["Chandrasekharpur Cyber PS", "Infocity Police Station"],
            "mule_accounts_flagged": 6,
            "amount_prevented_inr": 1840000.0,
            "notes": notes,
            "timeline_logs": [
                {"time": now.strftime("%H:%M:%S"), "log": f"Proactive {intervention_type} authorized and transmitted to field units."},
                {"time": (now + timedelta(seconds=2)).strftime("%H:%M:%S"), "log": "Simulated freeze signals delivered to core banking systems of 3 partner banks."},
                {"time": (now + timedelta(seconds=4)).strftime("%H:%M:%S"), "log": "Local LEA mobile patrol dispatch confirmation received."}
            ]
        }
        self.interventions.insert(0, intervention)
        
        if alert:
            alert["status"] = "INTERVENTION ACTIVE"
            alert["acknowledged_by"] = "Authorized Operator (Cyber Ops)"
            alert["resolution_notes"] = f"Proactive intervention {intervention['id']} initiated: {notes}"

        # Persist intervention
        try:
            with SessionLocal() as session:
                rec = InterventionModel(
                    id=intervention["id"],
                    alert_id=intervention["alert_id"],
                    hotspot_id=intervention["hotspot_id"],
                    target_cluster=intervention["target_cluster"],
                    intervention_type=intervention["intervention_type"],
                    status=intervention["status"],
                    initiated_by=intervention["initiated_by"],
                    initiated_timestamp=intervention["initiated_timestamp"],
                    mule_accounts_flagged=intervention["mule_accounts_flagged"],
                    amount_prevented_inr=intervention["amount_prevented_inr"],
                    notes=intervention["notes"]
                )
                session.add(rec)
                session.commit()
        except Exception as e:
            logger.error(f"Failed to persist intervention: {e}")

        self.add_audit_log(
            actor="Authorized Cyber Ops Officer",
            action="INTERVENTION_DISPATCHED",
            target_id=intervention["id"],
            details=f"Dispatched {intervention_type} for Alert {alert_id}. Target: {intervention['target_cluster']}."
        )

        return intervention

    def escalate_emergency_112(self, alert_id: str, operator_notes: str) -> Dict[str, Any]:
        alert = next((a for a in self.alerts if a["id"] == alert_id), None)
        now = datetime.now()
        
        incident = {
            "incident_id": f"112-INC-{now.strftime('%Y%m%d%H%M%S')}",
            "alert_id": alert_id,
            "hotspot_id": alert["hotspot_id"] if alert else "PRED-OD-BBSR-27",
            "operator_id": "OFFICER-I4C-9921",
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "location": alert["location"] if alert else "Bhubaneswar Patia Cluster, Odisha",
            "district": alert["district"] if alert else "Khordha",
            "state": alert["state"] if alert else "Odisha",
            "jurisdiction_lea": "Bhubaneswar Police Commissionerate Quick Response Team (QRT)",
            "contact_112_dispatched": True,
            "status": "Escalation_Initiated",
            "confirmation_notes": operator_notes or "Human operator confirmed high-probability coordinated ATM cashout attempt.",
            "timeline": [
                {"time": now.strftime("%H:%M:%S"), "event": "Operator verified high risk score (>90) and approved 112 emergency routing."},
                {"time": (now + timedelta(seconds=3)).strftime("%H:%M:%S"), "event": "112 Emergency CAD dispatch packet generated with GPS coordinates."},
                {"time": (now + timedelta(seconds=7)).strftime("%H:%M:%S"), "event": "Jurisdiction Cyber Cell and Field Patrol notified via secure inter-agency link."}
            ]
        }
        self.emergency_incidents.insert(0, incident)

        # Persist to database
        try:
            with SessionLocal() as session:
                rec = EmergencyIncidentModel(
                    incident_id=incident["incident_id"],
                    alert_id=incident["alert_id"],
                    hotspot_id=incident["hotspot_id"],
                    operator_id=incident["operator_id"],
                    timestamp=incident["timestamp"],
                    location=incident["location"],
                    district=incident["district"],
                    state=incident["state"],
                    jurisdiction_lea=incident["jurisdiction_lea"],
                    contact_112_dispatched=incident["contact_112_dispatched"],
                    status=incident["status"],
                    confirmation_notes=incident["confirmation_notes"]
                )
                session.add(rec)
                session.commit()
        except Exception as e:
            logger.error(f"Failed to persist emergency incident: {e}")

        self.add_audit_log(
            actor="OFFICER-I4C-9921",
            action="EMERGENCY_112_ESCALATION",
            target_id=incident["incident_id"],
            details=f"112 ERSS Incident created for Alert {alert_id}. Routed to {incident['jurisdiction_lea']}."
        )

        return incident

    def get_database_status(self) -> Dict[str, Any]:
        """Returns live PostgreSQL database telemetry and table counts."""
        try:
            with SessionLocal() as session:
                comp_count = session.query(ComplaintModel).count()
                cluster_count = session.query(ClusterModel).count()
                atm_count = session.query(ATMModel).count()
                alert_count = session.query(AlertModel).count()
                audit_count = session.query(AuditLogModel).count()
                
                return {
                    "database_type": ACTIVE_DB_TYPE,
                    "status": "ONLINE",
                    "host": "127.0.0.1:5432",
                    "database_name": "cyberpredict",
                    "tables": {
                        "complaints": comp_count,
                        "clusters": cluster_count,
                        "atms": atm_count,
                        "alerts": alert_count,
                        "audit_logs": audit_count
                    },
                    "total_records": comp_count + cluster_count + atm_count + alert_count + audit_count
                }
        except Exception as e:
            return {
                "database_type": ACTIVE_DB_TYPE,
                "status": "DEGRADED",
                "error": str(e),
                "fallback_mode": True
            }

data_repository = DataRepository()
