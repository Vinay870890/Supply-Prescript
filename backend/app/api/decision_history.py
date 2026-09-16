from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.decision import Decision
from app.schemas.decision import DecisionResponse


router = APIRouter(
    prefix="/api/decisions",
    tags=["Decisions"],
)


@router.get(
    "",
    response_model=list[DecisionResponse],
)
def get_decisions(
    db: Session = Depends(get_db),
):
    decisions = (
        db.query(Decision)
        .order_by(Decision.created_at.desc())
        .all()
    )

    return decisions


@router.get(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Decision not found",
        )

    return decision