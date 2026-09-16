from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.decision import Decision
from app.schemas.execution import (
    DecisionExecutionRequest,
    DecisionExecutionResponse,
)


router = APIRouter(
    prefix="/api/decisions",
    tags=["Decision Execution"],
)


@router.post(
    "/{decision_id}/execute",
    response_model=DecisionExecutionResponse,
)
def execute_decision(
    decision_id: int,
    request: DecisionExecutionRequest,
    db: Session = Depends(get_db),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found",
        )

    if decision.decision_status == "EXECUTED":
        raise HTTPException(
            status_code=400,
            detail="Decision has already been executed",
        )

    decision.decision_status = "EXECUTED"
    decision.executed_at = datetime.utcnow()
    decision.execution_notes = request.execution_notes

    db.commit()
    db.refresh(decision)

    return decision