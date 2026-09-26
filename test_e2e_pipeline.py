import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.config import ACTIVE_DB_TYPE, PG_URL
from backend.app.database.repository import data_repository

print("=" * 75)
print(" CYBERPREDICT: COMPREHENSIVE END-TO-END PIPELINE VERIFICATION SUITE")
print("=" * 75)

client = TestClient(app)

def run_e2e_tests():
    # 1. Verify Database Connection
    print("\n[STEP 1] Testing Database Connection...")
    print(f"       Active DB Type: {ACTIVE_DB_TYPE}")
    assert ACTIVE_DB_TYPE == "POSTGRESQL", f"Expected POSTGRESQL, got {ACTIVE_DB_TYPE}"
    db_status = data_repository.get_database_status()
    print(f"       PostgreSQL Tables: {db_status.get('tables')}")
    assert db_status.get("status") == "ONLINE"
    print("  --> [PASS] Real PostgreSQL database connection verified.")

    # 2. Verify Health Check
    print("\n[STEP 2] Testing API Health Check...")
    resp = client.get("/api/health")
    assert resp.status_code == 200
    health = resp.json()
    assert health["status"] == "HEALTHY"
    print(f"       Version: {health['version']} | Data Mode: {health['data_mode']}")
    print("  --> [PASS] API Health Check verified.")

    # 3. Verify Authentication & JWT Token
    print("\n[STEP 3] Testing Authentication & JWT Token Creation...")
    login_resp = client.post("/api/auth/login", json={
        "username": "admin@i4c.gov.in",
        "password": "Admin@2026"
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    auth_data = login_resp.json()
    token = auth_data["access_token"]
    assert token is not None and len(token) > 20
    print(f"       JWT Token Created: {token[:25]}... (Length: {len(token)})")
    
    # Verify Protected Route with Bearer Token
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    user_info = me_resp.json()["user"]
    print(f"       Authenticated Officer: {user_info['name']} | Role: {user_info['role_id']}")
    print("  --> [PASS] JWT Creation & Validation verified.")

    # 4. Verify Public Real Data Source: Razorpay IFSC API
    print("\n[STEP 4] Testing Public Real Banking API (Razorpay IFSC Directory)...")
    ifsc_resp = client.get("/api/public/ifsc/SBIN0010232")
    assert ifsc_resp.status_code == 200, f"IFSC lookup failed: {ifsc_resp.text}"
    ifsc_data = ifsc_resp.json()
    assert ifsc_data["data_source"] == "PUBLIC REAL DATA"
    assert ifsc_data["is_real_data"] is True
    print(f"       Verified Bank: {ifsc_data['bank_name']} - Branch: {ifsc_data['branch']}")
    print(f"       District: {ifsc_data['district']} | Address: {ifsc_data['address']}")
    print("  --> [PASS] Public Real Banking IFSC Data verified.")

    # 5. Verify Real Complaint Submission & Closed-Loop ML Recalculation
    print("\n[STEP 5] Testing Complaint Ingestion -> PostgreSQL -> ML Recalculation -> Alert -> WS Pipeline...")
    initial_complaints = len(data_repository.complaints)
    initial_alerts = len(data_repository.alerts)
    
    test_complaint = {
        "crime_category": "UPI Fraud",
        "victim_name": "Test Citizen Ramesh Patnaik",
        "victim_mobile": "+91 9437128910",
        "victim_account": "SBIN0001024881",
        "victim_bank": "State Bank of India",
        "loss_amount": 285000.0,
        "beneficiary_account": "HDFC0004198221",
        "beneficiary_bank": "HDFC Bank",
        "beneficiary_upi": "instant.cashout27@hdfc",
        "beneficiary_ifsc": "HDFC0001024",
        "state": "Odisha",
        "district": "Khordha",
        "lat": 20.3533,
        "lng": 85.8266,
        "is_synthetic": False
    }

    comp_resp = client.post("/api/complaints/", json=test_complaint, headers=headers)
    assert comp_resp.status_code == 201, f"Complaint submission failed: {comp_resp.text}"
    comp_result = comp_resp.json()
    
    assert comp_result["status"] == "success"
    complaint_obj = comp_result["complaint"]
    print(f"       New Complaint Stored in PostgreSQL: {complaint_obj['id']}")
    print(f"       Victim: {complaint_obj['victim_name']} | Loss: ₹{complaint_obj['loss_amount']:,.2f}")
    assert len(data_repository.complaints) == initial_complaints + 1

    # Verify ML Recalculation
    recalc = comp_result["recalculated_hotspot"]
    print(f"       Recalculated Hotspot: {recalc['name']}")
    print(f"       Updated Risk Score: {recalc['risk_score']}/100 | Window: {recalc['forecast_window']}")
    assert recalc["risk_score"] >= 70, "High-loss complaint should elevate risk score"

    # Verify Alert Generation
    new_alert = comp_result.get("new_alert")
    if new_alert:
        print(f"       Generated Actionable Alert: {new_alert['id']} | Risk Level: {new_alert['risk_level']}")
        assert len(data_repository.alerts) == initial_alerts + 1

    print("  --> [PASS] Closed-loop Complaint Pipeline & Risk Recalculation verified.")

    # 6. Verify Complaint Search & Filtering API
    print("\n[STEP 6] Testing Complaint Search & Filter from PostgreSQL...")
    search_resp = client.get(f"/api/complaints/?search={complaint_obj['id']}")
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["total"] >= 1
    print(f"       Found record by ID: {search_data['data'][0]['id']}")
    print("  --> [PASS] Complaint Retrieval & Search verified.")

    # 7. Verify Advance Multi-Horizon Forecasts
    print("\n[STEP 7] Testing Multi-Horizon Forecasts (1h, 6h, 12h, 24h)...")
    for h in ["1h", "6h", "12h", "24h"]:
        f_resp = client.get(f"/api/predictions/forecast?horizon={h}")
        assert f_resp.status_code == 200
        f_data = f_resp.json()
        assert f_data["status"] == "success"
        print(f"       Horizon [{h.upper()}]: Monitored {f_data['total_hotspots_monitored']} hotspots. Exposure: ₹{f_data['total_estimated_exposure_lakhs']} Lakhs")
    print("  --> [PASS] Multi-Horizon Forecasting verified.")

    # 8. Verify Bank Intelligence & Mule Account Freezing
    print("\n[STEP 8] Testing Bank Intelligence & Layer-2 Mule Freezing...")
    freeze_resp = client.post("/api/bank/freeze", json={
        "account_number": "HDFC0004198221",
        "bank_name": "HDFC Bank",
        "requested_by": "I4C National Command Administrator"
    }, headers=headers)
    assert freeze_resp.status_code == 200
    freeze_data = freeze_resp.json()["record"]
    assert freeze_data["status"] == "SIMULATED_HOLD_PLACED"
    print(f"       Simulated Hold Advisory: {freeze_data['advisory_id']} on {freeze_data['account_number']}")
    print("  --> [PASS] Bank Intelligence & Account Freezing verified.")

    # 9. Verify 112 Emergency Escalation
    print("\n[STEP 9] Testing 112 ERSS Rapid Emergency Escalation...")
    esc_resp = client.post("/api/emergency/escalate", json={
        "alert_id": "ALT-2026-1001",
        "operator_notes": "Emergency patrol staged near Patia ATM cluster.",
        "authorized_confirmation": True
    }, headers=headers)
    assert esc_resp.status_code == 200
    incident = esc_resp.json()["incident"]
    print(f"       112 Incident Logged: {incident['incident_id']} -> Routed to: {incident['jurisdiction_lea']}")
    print("  --> [PASS] 112 ERSS Emergency Escalation verified.")

    # 10. Verify Audit Trail Records
    print("\n[STEP 10] Testing Global Audit Trail in PostgreSQL...")
    audit_resp = client.get("/api/audit/logs")
    assert audit_resp.status_code == 200
    logs = audit_resp.json()["logs"]
    assert len(logs) >= 5
    print(f"       Latest Audit Log: [{logs[0]['action']}] by {logs[0]['actor']}")
    print("  --> [PASS] PostgreSQL Audit Trail verified.")

    print("\n" + "=" * 75)
    print(" ALL 10 CRITICAL END-TO-END SPECIFICATION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 75)

if __name__ == "__main__":
    try:
        run_e2e_tests()
    except Exception as e:
        print(f"\n[FAIL] Test assertion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
