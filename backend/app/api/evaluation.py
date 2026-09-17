from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.decision import Decision
from app.models.outcome import DecisionOutcome
from app.schemas.evaluation import EvaluationResponse


router = APIRouter(
    prefix="/api/evaluations",
    tags=["Evaluation"],
)


@router.get(
    "/decision/{decision_id}",
    response_model=EvaluationResponse,
)
def evaluate_decision(
    decision_id: int,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # Get decision
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Get actual outcome
    # ---------------------------------------------------------

    outcome = (
        db.query(DecisionOutcome)
        .filter(
            DecisionOutcome.decision_id == decision_id
        )
        .first()
    )

    if outcome is None:
        raise HTTPException(
            status_code=400,
            detail="Outcome has not been recorded for this decision",
        )

    # ---------------------------------------------------------
    # Predicted delay classification
    # ---------------------------------------------------------

    predicted_delay = (
        decision.predicted_delay_probability >= 0.55
    )

    actual_delay = (
        outcome.actual_delay_flag == 1
    )

    delay_prediction_correct = (
        predicted_delay == actual_delay
    )

    # ---------------------------------------------------------
    # Cost variance
    # ---------------------------------------------------------

    cost_variance = (
        outcome.actual_cost_usd
        - decision.estimated_cost_usd
    )

    # ---------------------------------------------------------
    # Decision success
    # ---------------------------------------------------------

    decision_success = (
        outcome.actual_delay_flag == 0
        and outcome.actual_cost_usd
        <= decision.estimated_cost_usd
    )

    # ---------------------------------------------------------
    # Savings
    # ---------------------------------------------------------

    estimated_savings = max(
        0.0,
        decision.estimated_cost_usd
        - outcome.actual_cost_usd,
    )

    # ---------------------------------------------------------
    # ROI
    # ---------------------------------------------------------

    if decision.estimated_cost_usd > 0:
        roi_percent = (
            estimated_savings
            / decision.estimated_cost_usd
        ) * 100
    else:
        roi_percent = 0.0

    return EvaluationResponse(
        decision_id=decision.id,
        shipment_id=decision.shipment_id,

        predicted_delay_probability=round(
            decision.predicted_delay_probability,
            4,
        ),

        actual_delay_flag=outcome.actual_delay_flag,

        predicted_delay_risk=round(
            decision.expected_delay_risk,
            4,
        ),

        actual_delay_days=round(
            outcome.actual_delay_days,
            2,
        ),

        estimated_cost_usd=round(
            decision.estimated_cost_usd,
            2,
        ),

        actual_cost_usd=round(
            outcome.actual_cost_usd,
            2,
        ),

        cost_variance_usd=round(
            cost_variance,
            2,
        ),

        delay_prediction_correct=(
            delay_prediction_correct
        ),

        decision_success=(
            decision_success
        ),

        estimated_savings_usd=round(
            estimated_savings,
            2,
        ),

        roi_percent=round(
            roi_percent,
            2,
        ),
    )