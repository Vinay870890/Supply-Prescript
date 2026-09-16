from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.decision import Decision
from app.schemas.decision import (
    DecisionCreateRequest,
    DecisionResponse,
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