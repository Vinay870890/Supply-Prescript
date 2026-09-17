from datetime import datetime

from pydantic import BaseModel, Field


class OutcomeCreateRequest(BaseModel):
    decision_id: int = Field(gt=0)
    shipment_id: int = Field(gt=0)

    actual_delay_days: float = Field(
        ge=0,
    )

    actual_delay_flag: int = Field(
        ge=0,
        le=1,
    )

    actual_cost_usd: float = Field(
        ge=0,
    )

    outcome_status: str = Field(
        min_length=1,
        max_length=30,
    )

    outcome_notes: str | None = None


class OutcomeResponse(BaseModel):
    id: int
    decision_id: int
    shipment_id: int
    actual_delay_days: float
    actual_delay_flag: int
    actual_cost_usd: float
    outcome_status: str
    outcome_notes: str | None
    recorded_at: datetime

    class Config:
        from_attributes = True