import os
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from .security import hash_password, verify_password, create_access_token, require_auth, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication & RBAC"])

AVAILABLE_ROLES = [
    {
        "role_id": "I4C_ADMIN",
        "name": "I4C National Command Administrator",
        "jurisdiction": "National (All India)",
        "badge": "I4C-HQ-001",
        "description": "Full access to national predictive intelligence, inter-state corridors, and strategic advisories."
    },
    {
        "role_id": "STATE_LEA",
        "name": "State Cyber Command Officer (Odisha CID)",
        "jurisdiction": "State Level (Odisha)",
        "badge": "OD-CID-782",
        "description": "State-wide predictive maps, multi-district task force coordination, and LEA alerts."
    },
    {
        "role_id": "DISTRICT_OFFICER",
        "name": "District Cyber Cell Officer (Bhubaneswar)",
        "jurisdiction": "Khordha District",
        "badge": "BBSR-CP-419",
        "description": "Local ATM hotspot surveillance, Quick Response Team (QRT) staging, and 112 escalation."
    },
    {
        "role_id": "BANK_ANALYST",
        "name": "Financial Institution Fraud Risk Analyst",
        "jurisdiction": "Participating Banks & FIs",
        "badge": "FIU-BNK-881",
        "description": "Citizen Financial Cyber Fraud Reporting System, mule account freeze alerts, transaction velocity."
    },
    {
        "role_id": "INVESTIGATOR",
        "name": "Lead Cybercrime Investigator",
        "jurisdiction": "Cyber Operations & Cases",
        "badge": "INV-CYB-094",
        "description": "Forensic case intelligence, multi-hop mule link analysis, and evidence documentation."
    }
]

# Preconfigured user database with salted password hashes
DEFAULT_USERS = {
    "admin@i4c.gov.in": {
        "username": "admin@i4c.gov.in",
        "password_hash": hash_password("Admin@2026"),
        "role_id": "I4C_ADMIN",
        "name": "Insp. Gen. Rajesh Sharma (I4C Admin)",
        "jurisdiction": "National (All India)",
        "badge": "I4C-HQ-001"
    },
    "odisha.lea@gov.in": {
        "username": "odisha.lea@gov.in",
        "password_hash": hash_password("Police@2026"),
        "role_id": "STATE_LEA",
        "name": "DIG Sanjeev Pattnaik (Odisha CID-CB)",
        "jurisdiction": "Odisha State",
        "badge": "OD-CID-782"
    },
    "district.officer@khordha.gov.in": {
        "username": "district.officer@khordha.gov.in",
        "password_hash": hash_password("District@2026"),
        "role_id": "DISTRICT_OFFICER",
        "name": "ACP Manas Behera (Bhubaneswar Cyber Cell)",
        "jurisdiction": "Khordha District",
        "badge": "BBSR-CP-419"
    },
    "bank.fraud@sbi.co.in": {
        "username": "bank.fraud@sbi.co.in",
        "password_hash": hash_password("Bank@2026"),
        "role_id": "BANK_ANALYST",
        "name": "Pooja Mishra (SBI Nodal Fraud Officer)",
        "jurisdiction": "SBI & Partner Banks",
        "badge": "FIU-BNK-881"
    },
    "investigator.od@cid.gov.in": {
        "username": "investigator.od@cid.gov.in",
        "password_hash": hash_password("Investigate@2026"),
        "role_id": "INVESTIGATOR",
        "name": "Inspector Ramesh Nayak (Forensic Lead)",
        "jurisdiction": "State Cyber Cell",
        "badge": "INV-CYB-094"
    }
}

class LoginRequest(BaseModel):
    username: str
    password: str

class RoleSwitchRequest(BaseModel):
    role_id: str

@router.post("/login")
def login(req: LoginRequest):
    user = DEFAULT_USERS.get(req.username.strip().lower())
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please check username and password."
        )

    token_data = {
        "sub": user["username"],
        "username": user["username"],
        "role_id": user["role_id"],
        "name": user["name"],
        "jurisdiction": user["jurisdiction"],
        "badge": user["badge"]
    }
    access_token = create_access_token(token_data)

    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "role_id": user["role_id"],
            "name": user["name"],
            "jurisdiction": user["jurisdiction"],
            "badge": user["badge"]
        }
    }

@router.get("/me")
def get_current_user_profile(user: dict = Depends(require_auth)):
    return {
        "status": "success",
        "user": user,
        "authenticated": True
    }

@router.get("/roles")
def get_roles():
    return {
        "status": "success",
        "roles": AVAILABLE_ROLES
    }

@router.get("/demo-users")
def get_demo_users():
    """Returns preconfigured accounts and credentials for evaluation convenience."""
    users_list = []
    default_passwords = {
        "admin@i4c.gov.in": "Admin@2026",
        "odisha.lea@gov.in": "Police@2026",
        "district.officer@khordha.gov.in": "District@2026",
        "bank.fraud@sbi.co.in": "Bank@2026",
        "investigator.od@cid.gov.in": "Investigate@2026"
    }
    for u, data in DEFAULT_USERS.items():
        users_list.append({
            "username": data["username"],
            "name": data["name"],
            "role_id": data["role_id"],
            "jurisdiction": data["jurisdiction"],
            "badge": data["badge"],
            "demo_password": default_passwords.get(u, "Admin@2026")
        })
    return {
        "status": "success",
        "users": users_list
    }

@router.post("/switch-role")
def switch_role(req: RoleSwitchRequest):
    role = next((r for r in AVAILABLE_ROLES if r["role_id"] == req.role_id), None)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Find matching demo user for this role
    target_user = next((u for u in DEFAULT_USERS.values() if u["role_id"] == req.role_id), None)
    if not target_user:
        target_user = {
            "username": f"{req.role_id.lower()}@i4c.gov.in",
            "role_id": role["role_id"],
            "name": role["name"],
            "jurisdiction": role["jurisdiction"],
            "badge": role["badge"]
        }

    token_data = {
        "sub": target_user["username"],
        "role_id": target_user["role_id"],
        "name": target_user["name"],
        "jurisdiction": target_user["jurisdiction"],
        "badge": target_user["badge"]
    }
    new_token = create_access_token(token_data)

    return {
        "status": "success",
        "message": f"Switched context to {role['name']}",
        "access_token": new_token,
        "token_type": "bearer",
        "user": target_user
    }
