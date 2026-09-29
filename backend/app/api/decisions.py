from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from app.models.decision import Decision
from app.schemas.decision import (
    DecisionCreateRequest,
    DecisionResponse,
    DecisionUpdateRequest,
)


router = APIRouter(
    prefix="/api/decisions",
    tags=["Decisions"],
)


@router.post(
    "",
    response_model=DecisionResponse,
)
def create_decision(
    request: DecisionCreateRequest,
    db: Session = Depends(get_db),
):
    decision = Decision(
        shipment_id=request.shipment_id,
        predicted_delay_probability=(
            request.predicted_delay_probability
        ),
        predicted_risk_level=request.predicted_risk_level,
        recommended_action=request.recommended_action,
        selected_action=request.selected_action,
        recommendation_score=request.recommendation_score,
        estimated_cost_usd=request.estimated_cost_usd,
        expected_delay_risk=request.expected_delay_risk,
        decision_status="SELECTED",
        notes=request.notes,
    )

    db.add(decision)
    db.commit()
    db.refresh(decision)

    return decision
@router.patch(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def update_decision(
    decision_id: int,
    request: DecisionUpdateRequest,
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
            detail="Executed decisions cannot be modified",
        )

    if request.decision_status is not None:
        allowed_statuses = {
            "SELECTED",
            "APPROVED",
            "REJECTED",
            "MODIFIED",
        }

        if request.decision_status not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail="Invalid decision status",
            )

        decision.decision_status = request.decision_status

    if request.selected_action is not None:
        decision.selected_action = request.selected_action

    if request.notes is not None:
        decision.notes = request.notes

    db.commit()
    db.refresh(decision)

    return decision