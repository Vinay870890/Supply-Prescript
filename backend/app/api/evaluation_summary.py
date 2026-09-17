from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.decision import Decision
from app.models.outcome import DecisionOutcome
from app.schemas.evaluation_summary import (
    EvaluationSummaryResponse,
)


router = APIRouter(
    prefix="/api/evaluations",
    tags=["Evaluation"],
)


@router.get(
    "/summary",
    response_model=EvaluationSummaryResponse,
)
def get_evaluation_summary(
    db: Session = Depends(get_db),
):
    decisions = (
        db.query(Decision)
        .all()
    )

    outcomes = (
        db.query(DecisionOutcome)
        .all()
    )

    total_decisions = len(decisions)

    executed_decisions = sum(
        1
        for decision in decisions
        if decision.decision_status
        in {
            "EXECUTED",
            "OUTCOME_RECORDED",
        }
    )

    outcomes_recorded = len(outcomes)

    outcome_by_decision = {
        outcome.decision_id: outcome
        for outcome in outcomes
    }

    successful_decisions = 0
    correct_predictions = 0
    delayed_shipments = 0
    on_time_shipments = 0

    total_cost_variance = 0.0
    total_savings = 0.0
    total_roi = 0.0

    evaluated_count = 0

    for decision in decisions:

        outcome = outcome_by_decision.get(
            decision.id
        )

        if outcome is None:
            continue

        evaluated_count += 1

        # -----------------------------------------------------
        # Prediction accuracy
        # -----------------------------------------------------

        predicted_delay = (
            decision.predicted_delay_probability
            >= 0.55
        )

        actual_delay = (
            outcome.actual_delay_flag == 1
        )

        if predicted_delay == actual_delay:
            correct_predictions += 1

        # -----------------------------------------------------
        # Shipment outcome
        # -----------------------------------------------------

        if outcome.actual_delay_flag == 1:
            delayed_shipments += 1
        else:
            on_time_shipments += 1

        # -----------------------------------------------------
        # Decision success
        # -----------------------------------------------------

        decision_success = (
            outcome.actual_delay_flag == 0
            and outcome.actual_cost_usd
            <= decision.estimated_cost_usd
        )

        if decision_success:
            successful_decisions += 1

        # -----------------------------------------------------
        # Cost variance
        # -----------------------------------------------------

        cost_variance = (
            outcome.actual_cost_usd
            - decision.estimated_cost_usd
        )

        total_cost_variance += cost_variance

        # -----------------------------------------------------
        # Savings
        # -----------------------------------------------------

        savings = max(
            0.0,
            decision.estimated_cost_usd
            - outcome.actual_cost_usd,
        )

        total_savings += savings

        # -----------------------------------------------------
        # ROI
        # -----------------------------------------------------

        if decision.estimated_cost_usd > 0:
            roi = (
                savings
                / decision.estimated_cost_usd
            ) * 100
        else:
            roi = 0.0

        total_roi += roi

    # ---------------------------------------------------------
    # Rates
    # ---------------------------------------------------------

    if evaluated_count > 0:
        decision_success_rate = (
            successful_decisions
            / evaluated_count
        ) * 100

        prediction_accuracy = (
            correct_predictions
            / evaluated_count
        ) * 100

        average_cost_variance = (
            total_cost_variance
            / evaluated_count
        )

        average_roi = (
            total_roi
            / evaluated_count
        )
    else:
        decision_success_rate = 0.0
        prediction_accuracy = 0.0
        average_cost_variance = 0.0
        average_roi = 0.0

    return EvaluationSummaryResponse(
        total_decisions=total_decisions,
        executed_decisions=executed_decisions,
        outcomes_recorded=outcomes_recorded,

        successful_decisions=successful_decisions,
        decision_success_rate=round(
            decision_success_rate,
            2,
        ),

        correct_delay_predictions=correct_predictions,
        prediction_accuracy=round(
            prediction_accuracy,
            2,
        ),

        delayed_shipments=delayed_shipments,
        on_time_shipments=on_time_shipments,

        average_cost_variance_usd=round(
            average_cost_variance,
            2,
        ),

        total_estimated_savings_usd=round(
            total_savings,
            2,
        ),

        average_roi_percent=round(
            average_roi,
            2,
        ),
    )