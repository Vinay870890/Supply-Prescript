from fastapi import APIRouter

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
    # 5. Return complete decision
    # ---------------------------------------------------------

    return {
        "success": True,

        "prediction": prediction,

        "explanation": explanation,

        "recommendation": recommendation,
    }