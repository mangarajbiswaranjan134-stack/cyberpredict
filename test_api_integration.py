import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.app.main import app
from backend.app.database.repository import data_repository
from backend.app.ml.predictive_engine import predictive_engine

print("Running 10/10 SIH Problem-Statement-Aligned Automated Verification Suite...\n")

def run_tests():
    # 1. Test Advance Multi-Horizon Forecasting (1h, 6h, 12h, 24h)
    horizons = ["1h", "6h", "12h", "24h"]
    for h in horizons:
        preds = data_repository.get_predictions_by_horizon(horizon=h)
        assert len(preds) > 0, f"Predictions for horizon {h} should not be empty"
        top = preds[0]
        assert top["forecast_horizon"] == h
        assert top["is_future_forecast"] is True
        print(f"[PASS] Horizon [{h.upper()}] Advance Forecast: {top['name']} | Risk: {top['risk_score']}/100 | Txns: {top['estimated_transactions']}")

    # 2. Test Exact 7-Factor Explainable AI Formula
    top_pred = data_repository.predictions[0]
    factors = top_pred.get("factors", [])
    assert len(factors) == 7, f"Expected exactly 7 explainability factors, got {len(factors)}"
    total_weight = sum(f["contribution_weight"] for f in factors)
    assert abs(total_weight - 1.0) < 0.01, f"Total factor weight should equal 1.0, got {total_weight}"
    print(f"[PASS] 7-Factor Explainability Formula verified (Sum = {total_weight:.2f}):")
    for f in factors:
        print(f"       * {f['factor_name']}: {int(f['contribution_weight']*100)}% ({f['impact_level']})")

    # 3. Test Historical vs. Predicted Separation
    assert len(data_repository.historical_withdrawals) > 0, "Historical withdrawal events must exist"
    print(f"[PASS] Historical withdrawal events (Past 7 Days): {len(data_repository.historical_withdrawals)} events recorded for GIS layering.")

    # 4. Test Bank / FI Intelligence & Simulated Mule Hold
    freeze_record = data_repository.simulate_bank_freeze_advisory(
        account_number="HDFCXXXXXX4198",
        bank_name="HDFC Bank",
        requested_by="Nodal Cyber Officer"
    )
    assert freeze_record["status"] == "SIMULATED_HOLD_PLACED"
    assert len(data_repository.bank_freeze_advisories) > 0
    print(f"[PASS] Simulated Bank Freeze Advisory placed on {freeze_record['account_number']} in {freeze_record['latency_ms']}ms.")

    # 5. Test Closed-Loop Outcome Feedback & Model Learning
    alert_target = data_repository.alerts[0]
    orig_acc = predictive_engine.model_metrics["accuracy"]
    orig_prec = predictive_engine.model_metrics["precision"]
    
    feedback_result = data_repository.record_incident_feedback(
        alert_id=alert_target["id"],
        feedback_data={
            "outcome_type": "INTERCEPTED_CONFIRMED",
            "amount_recovered_inr": 1840000.0,
            "officer_notes": "Patrol intercepted suspect before card insertion at ATM."
        }
    )
    assert feedback_result["status"] == "success"
    assert alert_target["status"] == "RESOLVED"
    assert alert_target["feedback_recorded"] is True
    assert predictive_engine.model_metrics["feedback_iterations"] >= 1
    assert predictive_engine.model_metrics["precision"] >= orig_prec
    print(f"[PASS] Closed-Loop Feedback Loop: Incident {alert_target['id']} resolved as [{feedback_result['outcome_type']}].")
    print(f"       Model Accuracy: {orig_acc:.3f} -> {predictive_engine.model_metrics['accuracy']:.3f} | Precision: {orig_prec:.3f} -> {predictive_engine.model_metrics['precision']:.3f}")

    # 6. Test Global Operational Audit Trail
    assert len(data_repository.audit_logs) >= 5, "Audit logs should record operational history"
    latest_log = data_repository.audit_logs[0]
    print(f"[PASS] Global Audit Trail: {len(data_repository.audit_logs)} logs. Latest: [{latest_log['action']}] by {latest_log['actor']}")

    # 7. Test Complete 15-Step Surge Simulation
    sim_res = data_repository.simulate_surge_event()
    assert sim_res["status"] == "SURGE_SIMULATED"
    assert sim_res["boosted_cluster"]["risk_score"] >= 94
    print(f"[PASS] 15-Step Demo Simulation: Injected {sim_res['new_complaints_count']} complaints. Elevated Risk Score: {sim_res['boosted_cluster']['risk_score']}/100")

    # 8. Test Agentic AI (AAI) Multi-Agent Reasoning Pipeline
    from backend.app.api.aai_copilot import handle_copilot_chat, CopilotQueryRequest
    chat_resp = handle_copilot_chat(CopilotQueryRequest(query="Autonomous Investigation: Analyze Bhubaneswar Cluster #27"))
    assert chat_resp["status"] == "SUCCESS"
    assert len(chat_resp["reasoning_steps"]) >= 4, "Expected multi-agent reasoning steps"
    assert len(chat_resp["suggested_actions"]) >= 2
    print(f"[PASS] Agentic AI Copilot: Autonomous reasoning completed ({len(chat_resp['reasoning_steps'])} agentic steps, {len(chat_resp['suggested_actions'])} proactive actions).")

    # 9. Test Google Stitch Entity & Cashout Flow Graph
    from backend.app.api.aai_copilot import get_stitch_graph
    stitch_resp = get_stitch_graph("CYB-2026-004821")
    assert stitch_resp["status"] == "SUCCESS"
    assert len(stitch_resp["nodes"]) >= 5, "Expected multi-hop nodes in Stitch Graph"
    assert len(stitch_resp["edges"]) >= 4, "Expected multi-hop edges in Stitch Graph"
    print(f"[PASS] Google Stitch Canvas: Resolved {len(stitch_resp['nodes'])} nodes and {len(stitch_resp['edges'])} edges across victim-to-ATM trail.")

    # 10. Test Autonomous Statutory Directive Drafting (Section 102 BNSS)
    from backend.app.api.aai_copilot import draft_proactive_action, ActionDraftRequest
    draft_resp = draft_proactive_action(ActionDraftRequest(action_type="BANK_FREEZE_102", target_id="9182374619"))
    assert draft_resp["status"] == "SUCCESS"
    assert "Section 102" in draft_resp["legal_mandate"]
    print(f"[PASS] Statutory Directive Drafter: Generated {draft_resp['document_id']} under {draft_resp['legal_mandate']}.")

    # 11. Test Google Maps Platform Integration
    from backend.app.api.system import get_maps_config
    maps_cfg = get_maps_config()
    assert maps_cfg["status"] == "CONFIGURED"
    assert maps_cfg["provider"] == "GOOGLE_MAPS_PLATFORM"
    assert len(maps_cfg["api_key"]) > 10
    print(f"[PASS] Google Maps Platform: Connected with API key ({maps_cfg['api_key'][:8]}...) and {len(maps_cfg['features'])} geospatial tactical layers.")

    print("\n" + "="*70)
    print("ALL 11/11 SIH PS-ALIGNED TEST SUITES PASSED WITH ZERO ERRORS!")
    print("="*70)

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n[FAIL] Test assertion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
