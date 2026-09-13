from fastapi import APIRouter

from app.ml.predictor import predictor
from app.ml.explainer import explainer
from app.schemas.prediction import ShipmentPredictionRequest


router = APIRouter(
    prefix="/api/predictions",
    tags=["Predictions"],
)


@router.post("")
def predict_shipment(
    request: ShipmentPredictionRequest,
):
    features = request.model_dump(by_alias=True)

    # Prediction
    prediction_result = predictor.predict(features)

    # SHAP explanation
    explanation_result = explainer.explain(
        features,
        top_n=5,
    )

    return {
        "success": True,
        "prediction": prediction_result,
        "explanation": explanation_result,
    }