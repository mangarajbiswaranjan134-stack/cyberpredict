import os
import asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List

from .api.auth import router as auth_router
from .api.complaints import router as complaints_router
from .api.predictions import router as predictions_router
from .api.hotspots import router as hotspots_router
from .api.alerts import router as alerts_router
from .api.interventions import router as interventions_router
from .api.investigations import router as investigations_router
from .api.financial import router as financial_router
from .api.bank import router as bank_router
from .api.audit import router as audit_router
from .api.emergency import router as emergency_router
from .api.simulation import router as simulation_router
from .api.reports import router as reports_router
from .api.system import router as system_router
from .api.public_data import router as public_data_router
from .api.aai_copilot import router as aai_copilot_router
from .database.repository import data_repository
from .database.config import ACTIVE_DB_TYPE

app = FastAPI(
    title="CYBERPREDICT API",
    description="National Cybercrime Predictive Intelligence & Intervention Platform (SIH 2026)",
    version="3.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API Routers
app.include_router(auth_router)
app.include_router(complaints_router)
app.include_router(predictions_router)
app.include_router(hotspots_router)
app.include_router(alerts_router)
app.include_router(interventions_router)
app.include_router(investigations_router)
app.include_router(financial_router)
app.include_router(bank_router)
app.include_router(audit_router)
app.include_router(emergency_router)
app.include_router(simulation_router)
app.include_router(reports_router)
app.include_router(system_router)
app.include_router(public_data_router)
app.include_router(aai_copilot_router)

# WebSocket Connection Manager for Real-Time Streaming
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.loop = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.loop = asyncio.get_running_loop()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        for dc in dead_connections:
            self.disconnect(dc)

    def broadcast_sync(self, message: dict):
        if self.loop and self.loop.is_running():
            try:
                asyncio.run_coroutine_threadsafe(self.broadcast(message), self.loop)
                return
            except Exception:
                pass
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.broadcast(message))
        except Exception:
            pass

ws_manager = ConnectionManager()

# Register the WebSocket broadcast hook with the DataRepository
data_repository.set_ws_broadcast_callback(ws_manager.broadcast_sync)

@app.on_event("startup")
async def startup_event():
    ws_manager.loop = asyncio.get_running_loop()

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial handshake message with database status
        db_stat = data_repository.get_database_status()
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "system": "CYBERPREDICT",
            "database": db_stat.get("database_type", "POSTGRESQL"),
            "data_mode": data_repository.system_metrics["dataset_notice"],
            "active_clients": len(ws_manager.active_connections)
        })
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "type": "HEARTBEAT_ACK",
                "status": "LIVE",
                "database": ACTIVE_DB_TYPE
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.get("/api/health")
def health_check():
    db_stat = data_repository.get_database_status()
    return {
        "status": "HEALTHY",
        "system": "CYBERPREDICT",
        "version": "2.2.0",
        "database": db_stat,
        "data_mode": data_repository.system_metrics["dataset_notice"],
        "platform": "Smart India Hackathon 2026 Edition",
        "realtime_active_clients": len(ws_manager.active_connections),
        "problem_statement_aligned": "10/10 Complete Closed-Loop Intelligence"
    }

@app.get("/api/system/database")
def get_database_telemetry():
    return {
        "status": "success",
        "telemetry": data_repository.get_database_status()
    }

# Mount Frontend Static Directory
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_root():
        index_path = frontend_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "CYBERPREDICT API Online."}
