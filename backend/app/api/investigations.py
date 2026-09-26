from fastapi import APIRouter, HTTPException
from ..database.repository import data_repository

router = APIRouter(prefix="/api/investigations", tags=["Investigator Workspace & Case Intelligence"])

@router.get("/")
def list_investigations():
    cases = list(data_repository.investigations.values())
    return {
        "status": "success",
        "total": len(cases),
        "cases": cases
    }

@router.get("/{case_id}")
def get_case_detail(case_id: str):
    case = data_repository.investigations.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Investigation case not found")
    
    return {
        "status": "success",
        "case": case
    }

@router.get("/{case_id}/graph")
def get_case_relationship_graph(case_id: str):
    """Returns nodes and edges formatted for Vis.js interactive network graph."""
    case = data_repository.investigations.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Investigation case not found")

    return {
        "status": "success",
        "case_id": case["case_id"],
        "title": case["title"],
        "nodes": case["nodes"],
        "edges": case["edges"]
    }
