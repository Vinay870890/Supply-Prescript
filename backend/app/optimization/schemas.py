from pydantic import BaseModel, Field


class OptimizationRequest(BaseModel):
    delay_probability: float = Field(ge=0, le=1)

    freight_cost_usd: float = Field(ge=0)

    shipment_value_usd: float = Field(ge=0)

    transport_risk_score: float = Field(ge=0, le=1)

    shipment_complexity_score: float = Field(ge=0)

    shipment_mode: str


class ActionRecommendation(BaseModel):
    action: str
    description: str

    estimated_cost_usd: float
    expected_delay_risk: float

    speed_score: float = Field(ge=0, le=1)
    risk_score: float = Field(ge=0, le=1)

    objective_score: float

    recommended: bool = False


class OptimizationResponse(BaseModel):
    success: bool
    recommended_action: str
    recommendation_reason: str

    alternatives: list[ActionRecommendation]