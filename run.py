import sys
import os
import uvicorn

# Ensure UTF-8 output encoding for Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    print("=" * 72)
    print(" CYBERPREDICT: National Cybercrime Predictive Intelligence Platform")
    print(" Smart India Hackathon (SIH 2026) Prototype System")
    print(" Data Mode: Synthetic / Demonstration Data")
    print("=" * 72)
    print("[INFO] Starting Command Center on http://localhost:8000 ...")
    print("[INFO] Press Ctrl+C to terminate.")

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
