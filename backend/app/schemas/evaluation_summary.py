from pydantic import BaseModel


class EvaluationSummaryResponse(BaseModel):
    total_decisions: int
    executed_decisions: int
    outcomes_recorded: int

    successful_decisions: int
    decision_success_rate: float

    correct_delay_predictions: int
    prediction_accuracy: float

    delayed_shipments: int
    on_time_shipments: int

    average_cost_variance_usd: float
    total_estimated_savings_usd: float
    average_roi_percent: float