from fastapi import APIRouter

from app.optimization.optimizer import optimizer
from app.optimization.schemas import (
    OptimizationRequest,
    OptimizationResponse,
)


router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"],
)


@router.post("", response_model=OptimizationResponse)
def recommend_action(
    request: OptimizationRequest,
):
    return optimizer.optimize(request)