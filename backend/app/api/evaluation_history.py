from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.decision import Decision
from app.models.outcome import DecisionOutcome


router = APIRouter(
    prefix="/api/evaluations",
    tags=["Evaluation"],
)


@router.get("/history")
def get_evaluation_history(
    db: Session = Depends(get_db),
):
    decisions = (
        db.query(Decision)
        .order_by(Decision.created_at.desc())
        .all()
    )

    outcomes = (
        db.query(DecisionOutcome)
        .all()
    )

    outcome_map = {
        outcome.decision_id: outcome
        for outcome in outcomes
    }

    results = []

    for decision in decisions:
        outcome = outcome_map.get(decision.id)

        if outcome is None:
            continue

        predicted_delay = (
            decision.predicted_delay_probability >= 0.55
        )

        actual_delay = (
            outcome.actual_delay_flag == 1
        )

        prediction_correct = (
            predicted_delay == actual_delay
        )

        cost_variance = (
            outcome.actual_cost_usd
            - decision.estimated_cost_usd
        )

        savings = max(
            0.0,
            decision.estimated_cost_usd
            - outcome.actual_cost_usd,
        )

        if decision.estimated_cost_usd > 0:
            roi = (
                savings
                / decision.estimated_cost_usd
            ) * 100
        else:
            roi = 0.0

        decision_success = (
            outcome.actual_delay_flag == 0
            and outcome.actual_cost_usd
            <= decision.estimated_cost_usd
        )

        results.append(
            {
                "decision_id": decision.id,
                "shipment_id": decision.shipment_id,
                "recommended_action": (
                    decision.recommended_action
                ),
                "selected_action": (
                    decision.selected_action
                ),
                "predicted_delay_probability": round(
                    decision.predicted_delay_probability,
                    4,
                ),
                "actual_delay_flag": (
                    outcome.actual_delay_flag
                ),
                "actual_delay_days": round(
                    outcome.actual_delay_days,
                    2,
                ),
                "estimated_cost_usd": round(
                    decision.estimated_cost_usd,
                    2,
                ),
                "actual_cost_usd": round(
                    outcome.actual_cost_usd,
                    2,
                ),
                "cost_variance_usd": round(
                    cost_variance,
                    2,
                ),
                "prediction_correct": (
                    prediction_correct
                ),
                "decision_success": (
                    decision_success
                ),
                "estimated_savings_usd": round(
                    savings,
                    2,
                ),
                "roi_percent": round(
                    roi,
                    2,
                ),
                "outcome_status": (
                    outcome.outcome_status
                ),
                "recorded_at": (
                    outcome.recorded_at
                ),
            }
        )

    return {
        "success": True,
        "count": len(results),
        "results": results,
    }