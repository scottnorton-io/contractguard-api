from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from contractguard.services.analyzer import ComplianceAnalyzer
from contractguard.services.audit import AuditService

router = APIRouter()

class ProposedActivity(BaseModel):
    type: str
    location: Optional[str] = None
    dates: Optional[List[str]] = None
    marketing_as: Optional[str] = None
    sponsors: Optional[List[str]] = None
    compensation: Optional[float] = None
    description: Optional[str] = None

class ComplianceCheckRequest(BaseModel):
    contract_id: str
    proposed_activity: ProposedActivity

class TriggeredClause(BaseModel):
    clause_id: str
    clause_text: str
    violation_type: str
    severity: str

class ComplianceCheckResponse(BaseModel):
    verdict: str
    risk_level: Optional[str] = None
    triggered_clauses: List[TriggeredClause]
    required_actions: List[str]
    approval_workflow: Optional[Dict[str, Any]] = None
    precedent_cases: List[Dict[str, Any]]
    audit_id: str
    timestamp: str

@router.post("/check", response_model=ComplianceCheckResponse)
async def check_compliance(
    request: Request,
    body: ComplianceCheckRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """
    Check proposed activity against contract for compliance.
    
    P0-002: Emits audit event for every query.
    """
    tenant_id = request.state.tenant_id
    actor_id = request.state.actor_id
    trace_id = request.state.request_id
    
    # Analyze compliance
    analyzer = ComplianceAnalyzer()
    result = await analyzer.analyze(
        tenant_id=tenant_id,
        contract_id=body.contract_id,
        proposed_activity=body.proposed_activity.dict()
    )
    
    # P0-002: Emit audit event
    audit = AuditService()
    audit_id = await audit.log_compliance_query(
        tenant_id=tenant_id,
        actor_id=actor_id,
        contract_id=body.contract_id,
        query_payload=body.dict(),
        verdict=result["verdict"],
        risk_level=result.get("risk_level"),
        triggered_clauses=result["triggered_clauses"],
        response_payload=result,
        trace_id=trace_id,
        source_ip=request.client.host if request.client else None
    )
    
    result["audit_id"] = audit_id
    
    return result
