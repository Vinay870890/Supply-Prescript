from datetime import datetime

from pydantic import BaseModel, Field


class DecisionCreateRequest(BaseModel):
    shipment_id: int = Field(gt=0)

    predicted_delay_probability: float = Field(
        ge=0,
        le=1,
    )

    predicted_risk_level: str

    recommended_action: str

    selected_action: str

    recommendation_score: float

    estimated_cost_usd: float = Field(
        ge=0,
    )

    expected_delay_risk: float = Field(
        ge=0,
        le=1,
    )

    notes: str | None = None


class DecisionResponse(BaseModel):
    id: int
    shipment_id: int
    predicted_delay_probability: float
    predicted_risk_level: str
    recommended_action: str
    selected_action: str
    recommendation_score: float
    estimated_cost_usd: float
    expected_delay_risk: float
    decision_status: str
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True