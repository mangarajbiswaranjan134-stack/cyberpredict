import sys
import json
import urllib.request
import urllib.parse
import psycopg2
import asyncio
import websockets

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8000"

def test_http_endpoint(name, url, method="GET", headers=None, data=None, expected_status=200):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            body = resp.read().decode('utf-8')
            assert status == expected_status, f"Expected {expected_status}, got {status}"
            print(f"  [PASS] {name} (HTTP {status})")
            try:
                return json.loads(body)
            except Exception:
                return body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"  [FAIL] {name} (HTTP {e.code}): {body}")
        raise

def test_database_persistence(complaint_id):
    print("\n--- Verifying Direct PostgreSQL 16 Persistence ---")
    conn = psycopg2.connect("postgresql://postgres@127.0.0.1:5432/cyberpredict")
    cur = conn.cursor()
    cur.execute("SELECT id, victim_name, crime_category, loss_amount, state, district FROM complaints WHERE id = %s", (complaint_id,))
    row = cur.fetchone()
    assert row is not None, f"Complaint {complaint_id} was NOT found in PostgreSQL database!"
    print(f"  [PASS] Verified row in PostgreSQL 'complaints' table:")
    print(f"         ID: {row[0]}")
    print(f"         Victim: {row[1]}")
    print(f"         Category: {row[2]}")
    print(f"         Amount: INR {row[3]:,.2f}")
    print(f"         District/State: {row[5]}, {row[4]}")
    
    # Check audit log
    cur.execute("SELECT id, action, target_id, details FROM audit_logs WHERE target_id = %s ORDER BY timestamp DESC LIMIT 1", (complaint_id,))
    audit_row = cur.fetchone()
    if audit_row:
        print(f"  [PASS] Verified corresponding audit log in PostgreSQL:")
        print(f"         Audit ID: {audit_row[0]} | Action: {audit_row[1]} | Details: {audit_row[3]}")
    
    cur.close()
    conn.close()

async def test_websocket_broadcast():
    print("\n--- Verifying Real-Time WebSocket Telemetry Pipeline ---")
    ws_url = "ws://127.0.0.1:8000/ws/live"
    async with websockets.connect(ws_url) as ws:
        print("  [PASS] WebSocket connected successfully to /ws/live")
        
        # 1. Receive initial handshake message
        handshake_raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
        handshake = json.loads(handshake_raw)
        print(f"  [PASS] WebSocket Handshake received: {handshake.get('type')} (Database: {handshake.get('database')})")
        assert handshake.get('type') == 'CONNECTION_ESTABLISHED', "Handshake type mismatch!"

        # 2. Post a complaint while listening on the WebSocket
        token_data = test_http_endpoint("JWT Auth for WS Test", f"{BASE_URL}/api/auth/login", method="POST", data={
            "username": "admin@i4c.gov.in",
            "password": "Admin@2026"
        })
        token = token_data["access_token"]
        
        complaint_payload = {
            "victim_name": "Siddharth Patnaik",
            "victim_phone": "+91 98619 00122",
            "victim_city": "Bhubaneswar",
            "crime_category": "UPI Fraud",
            "amount_lost_inr": 350000.0,
            "loss_type": "Direct Transfer",
            "beneficiary_account": "HDFC0009988112",
            "beneficiary_upi": "telemetry.mule@hdfc",
            "beneficiary_ifsc": "HDFC0000060",
            "state": "Odisha",
            "district": "Khordha",
            "latitude": 20.3533,
            "longitude": 85.8266,
            "is_synthetic": True
        }
        
        # Trigger complaint via HTTP
        resp = test_http_endpoint("Ingest Complaint for WS Trigger", f"{BASE_URL}/api/complaints/", method="POST",
                                  headers={"Authorization": f"Bearer {token}"}, data=complaint_payload, expected_status=201)
        new_id = resp["complaint"]["id"]
        
        # 3. Receive real-time WebSocket broadcast event
        msg_raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
        msg = json.loads(msg_raw)
        print(f"  [PASS] WebSocket broadcast received:")
        print(f"         Event: {msg.get('event')}")
        print(f"         Complaint ID: {msg.get('payload', {}).get('complaint_id')}")
        print(f"         Recalculated Risk Score: {msg.get('payload', {}).get('recalculated_risk_score')}/100")
        assert msg.get('payload', {}).get('complaint_id') == new_id, "Broadcast ID mismatch!"
        return new_id

def main():
    print("=" * 72)
    print(" CYBERPREDICT: Complete End-to-End Live Verification")
    print("=" * 72)
    
    # 1. Test frontend HTML
    print("\n--- 1. Frontend & Static Assets ---")
    html = test_http_endpoint("Frontend index.html", f"{BASE_URL}/")
    assert "CYBERPREDICT" in html
    assert "DEMO / SYNTHETIC DATA" in html
    assert "POSTGRESQL 16 (ONLINE)" in html
    
    css = test_http_endpoint("Command Center CSS", f"{BASE_URL}/static/css/command-center.css")
    assert len(css) > 100
    
    js_app = test_http_endpoint("Application Controller JS", f"{BASE_URL}/static/js/app.js")
    assert "handleComplaintSubmit" in js_app
    assert "initWebSocket" in js_app
    
    # 2. Test System & DB Health
    print("\n--- 2. Database & System Health ---")
    sys_status = test_http_endpoint("System Status", f"{BASE_URL}/api/system/status")
    print(f"  [PASS] System Health: {sys_status.get('status')}")
    assert sys_status.get("status") == "healthy"
    
    # 3. Test JWT Authentication
    print("\n--- 3. JWT Authentication & RBAC ---")
    login_res = test_http_endpoint("Officer Login", f"{BASE_URL}/api/auth/login", method="POST", data={
        "username": "admin@i4c.gov.in",
        "password": "Admin@2026"
    })
    token = login_res["access_token"]
    user = login_res["user"]
    print(f"  [PASS] Logged in as: {user['name']} ({user['role_id']})")
    
    me_res = test_http_endpoint("Get Current Officer Profile (JWT Guarded)", f"{BASE_URL}/api/auth/me",
                                headers={"Authorization": f"Bearer {token}"})
    assert (me_res["user"].get("username") or me_res["user"].get("sub")) == "admin@i4c.gov.in"
    
    # 4. Test Public Real Data Gateway (IFSC)
    print("\n--- 4. Public Real Data Gateway (Razorpay/RBI National Directory) ---")
    ifsc_res = test_http_endpoint("IFSC Code Verification (SBIN0010232)", f"{BASE_URL}/api/public/ifsc/SBIN0010232")
    bank_title = ifsc_res.get('bank') or ifsc_res.get('bank_name')
    print(f"  [PASS] Verified Bank: {bank_title} | Branch: {ifsc_res['branch']} | District: {ifsc_res['district']}")
    assert "STATE BANK OF INDIA" in bank_title.upper()
    
    # 5. Ingest complaint via HTTP
    print("\n--- 5. Complaint Ingestion & ML Pipeline ---")
    complaint_data = {
        "victim_name": "Debabrata Routray",
        "victim_phone": "+91 97781 44520",
        "victim_city": "Bhubaneswar",
        "crime_category": "Investment Scam",
        "amount_lost_inr": 1250000.0,
        "loss_type": "Multi-Hop Mule",
        "beneficiary_account": "SBIN0019284819",
        "beneficiary_upi": "fastinvest99@sbi",
        "beneficiary_ifsc": "SBIN0010232",
        "state": "Odisha",
        "district": "Khordha",
        "latitude": 20.3533,
        "longitude": 85.8266,
        "is_synthetic": True
    }
    ingest_res = test_http_endpoint("Ingest Investment Scam Complaint", f"{BASE_URL}/api/complaints/", method="POST",
                                    headers={"Authorization": f"Bearer {token}"}, data=complaint_data, expected_status=201)
    cid = ingest_res["complaint"]["id"]
    print(f"  [PASS] Created Complaint ID: {cid}")
    print(f"  [PASS] Recalculated Cluster: {ingest_res['recalculated_hotspot']['name']}")
    print(f"  [PASS] Updated Risk Score: {ingest_res['recalculated_hotspot']['risk_score']}/100 ({ingest_res['recalculated_hotspot']['risk_level']})")
    
    # 6. Verify directly in PostgreSQL
    test_database_persistence(cid)
    
    # 7. Verify WebSocket broadcast
    ws_cid = asyncio.run(test_websocket_broadcast())
    test_database_persistence(ws_cid)
    
    print("\n" + "=" * 72)
    print(" ALL LIVE VERIFICATION CHECKS PASSED (100% OPERATIONAL)")
    print("=" * 72)

if __name__ == "__main__":
    main()
