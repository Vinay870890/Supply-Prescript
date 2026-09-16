from datetime import datetime

from pydantic import BaseModel


class DecisionExecutionRequest(BaseModel):
    execution_notes: str | None = None


class DecisionExecutionResponse(BaseModel):
    id: int
    shipment_id: int
    selected_action: str
    decision_status: str
    executed_at: datetime
    execution_notes: str | None

    class Config:
        from_attributes = True