from pydantic import BaseModel


class EvaluationResponse(BaseModel):
    decision_id: int
    shipment_id: int

    predicted_delay_probability: float
    actual_delay_flag: int

    predicted_delay_risk: float
    actual_delay_days: float

    estimated_cost_usd: float
    actual_cost_usd: float

    cost_variance_usd: float
    delay_prediction_correct: bool

    decision_success: bool

    estimated_savings_usd: float
    roi_percent: float