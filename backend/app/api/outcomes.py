from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.decision import Decision
from app.models.outcome import DecisionOutcome
from app.schemas.outcome import (
    OutcomeCreateRequest,
    OutcomeResponse,
)


router = APIRouter(
    prefix="/api/outcomes",
    tags=["Outcomes"],
)


@router.post(
    "",
    response_model=OutcomeResponse,
)
def create_outcome(
    request: OutcomeCreateRequest,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # Verify decision exists
    # ---------------------------------------------------------

    decision = (
        db.query(Decision)
        .filter(Decision.id == request.decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found",
        )

    # ---------------------------------------------------------
    # Verify decision was executed
    # ---------------------------------------------------------

    if decision.decision_status != "EXECUTED":
        raise HTTPException(
            status_code=400,
            detail="Outcome can only be recorded for an executed decision",
        )

    # ---------------------------------------------------------
    # Prevent duplicate outcome
    # ---------------------------------------------------------

    existing_outcome = (
        db.query(DecisionOutcome)
        .filter(
            DecisionOutcome.decision_id
            == request.decision_id
        )
        .first()
    )

    if existing_outcome is not None:
        raise HTTPException(
            status_code=400,
            detail="Outcome already recorded for this decision",
        )

    # ---------------------------------------------------------
    # Verify shipment consistency
    # ---------------------------------------------------------

    if decision.shipment_id != request.shipment_id:
        raise HTTPException(
            status_code=400,
            detail="Shipment ID does not match the decision",
        )

    # ---------------------------------------------------------
    # Create outcome
    # ---------------------------------------------------------

    outcome = DecisionOutcome(
        decision_id=request.decision_id,
        shipment_id=request.shipment_id,
        actual_delay_days=request.actual_delay_days,
        actual_delay_flag=request.actual_delay_flag,
        actual_cost_usd=request.actual_cost_usd,
        outcome_status=request.outcome_status,
        outcome_notes=request.outcome_notes,
    )

    db.add(outcome)

    # ---------------------------------------------------------
    # Update decision status
    # ---------------------------------------------------------

    decision.decision_status = "OUTCOME_RECORDED"

    db.commit()
    db.refresh(outcome)

    return outcome