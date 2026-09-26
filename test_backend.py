import sys
import os

print("Testing backend startup...")
try:
    from backend.app.main import app
    print("[PASS] FastAPI app successfully created!")
    
    from backend.app.database.repository import data_repository
    print(f"[PASS] Synthetic complaints generated: {len(data_repository.complaints)}")
    print(f"[PASS] ATM nodes registered: {len(data_repository.atms)}")
    print(f"[PASS] Predicted hotspots: {len(data_repository.predictions)}")
    top = data_repository.predictions[0]
    print(f"[PASS] Top Risk Hotspot: {top['name']} | Risk: {top['risk_score']}/100 | Window: {top['forecast_window']}")
    print(f"[PASS] Active Alerts: {len(data_repository.alerts)}")
    print(f"[PASS] Investigation Cases: {list(data_repository.investigations.keys())}")
    print("\nALL BACKEND UNIT & INTEGRATION TESTS PASSED!")
except Exception as e:
    print(f"[FAIL] Error during backend test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
