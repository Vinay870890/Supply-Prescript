from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.decision import Decision

from app.ml.predictor import predictor
from app.ml.explainer import explainer

from app.optimization.optimizer import optimizer
from app.optimization.schemas import OptimizationRequest

from app.schemas.prediction import ShipmentPredictionRequest


router = APIRouter(
    prefix="/api/decision",
    tags=["Decision"],
)


@router.post("")
def make_decision(
    request: ShipmentPredictionRequest,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # 1. Prepare features
    # ---------------------------------------------------------

    features = request.model_dump(by_alias=True)

    # ---------------------------------------------------------
    # 2. Predict delay risk
    # ---------------------------------------------------------

    prediction = predictor.predict(features)

    # ---------------------------------------------------------
    # 3. Explain prediction
    # ---------------------------------------------------------

    explanation = explainer.explain(
        features,
        top_n=5,
    )

    # ---------------------------------------------------------
    # 4. Optimize business action
    # ---------------------------------------------------------

    optimization_request = OptimizationRequest(
        delay_probability=prediction["delay_probability"],
        freight_cost_usd=request.freight_cost_usd,
        shipment_value_usd=request.line_item_value,
        transport_risk_score=request.transport_risk_score,
        shipment_complexity_score=request.shipment_complexity_score,
        shipment_mode=request.shipment_mode,
    )

    recommendation = optimizer.optimize(
        optimization_request
    )

    # ---------------------------------------------------------
    # 5. Find recommended option
    # ---------------------------------------------------------

    recommended_option = next(
        (
            option
            for option in recommendation.alternatives
            if option.recommended
        ),
        None,
    )

    if recommended_option is None:
        recommended_option = next(
            (
                option
                for option in recommendation.alternatives
                if option.action == recommendation.recommended_action
            ),
            None,
        )

    if recommended_option is None:
        raise ValueError(
            "Recommended action not found in optimization alternatives."
        )

    # ---------------------------------------------------------
    # 6. Create database decision
    # ---------------------------------------------------------

    decision = Decision(
        shipment_id=request.shipment_id,

        predicted_delay_probability=prediction[
            "delay_probability"
        ],

        predicted_risk_level=prediction[
            "risk_level"
        ],

        recommended_action=recommendation.recommended_action,

        selected_action=recommendation.recommended_action,

        recommendation_score=recommended_option.objective_score,

        estimated_cost_usd=recommended_option.estimated_cost_usd,

        expected_delay_risk=recommended_option.expected_delay_risk,

        decision_status="SELECTED",

        notes=(
            "Decision selected after reviewing "
            "prediction and optimization recommendation."
        ),
    )

    db.add(decision)
    db.commit()
    db.refresh(decision)

    # ---------------------------------------------------------
    # 7. Return complete decision
    # ---------------------------------------------------------

    return {
        "success": True,

        "decision_id": decision.id,

        "shipment_id": decision.shipment_id,

        "prediction": prediction,

        "explanation": explanation,

        "recommendation": recommendation.model_dump(),

        "decision": {
            "id": decision.id,
            "status": decision.decision_status,
            "selected_action": decision.selected_action,
            "recommendation_score": decision.recommendation_score,
            "estimated_cost_usd": decision.estimated_cost_usd,
            "expected_delay_risk": decision.expected_delay_risk,
        },
    }