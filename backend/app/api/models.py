from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.model_registry import ModelRegistry
from app.services.model_registry import get_active_model, get_all_models

router = APIRouter(
    prefix="/api/models",
    tags=["Model Registry"],
)


def model_to_dict(model: ModelRegistry):
    return {
        "id": model.id,
        "model_name": model.model_name,
        "version": model.version,
        "model_type": model.model_type,
        "model_path": model.model_path,
        "status": model.status,
        "accuracy": model.accuracy,
        "precision": model.precision,
        "recall": model.recall,
        "f1_score": model.f1_score,
        "roc_auc": model.roc_auc,
        "feature_count": model.feature_count,
        "description": model.description,
        "created_at": model.created_at,
    }


@router.get("")
def list_models(db: Session = Depends(get_db)):
    models = get_all_models(db)

    return {
        "success": True,
        "count": len(models),
        "models": [model_to_dict(model) for model in models],
    }


@router.get("/active")
def active_model(db: Session = Depends(get_db)):
    model = get_active_model(db)

    if not model:
        raise HTTPException(
            status_code=404,
            detail="No active model found",
        )

    return {
        "success": True,
        "model": model_to_dict(model),
    }
from pydantic import BaseModel


class ModelRegistrationRequest(BaseModel):
    model_name: str
    version: str
    model_type: str
    model_path: str
    status: str = "CANDIDATE"

    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1_score: float | None = None
    roc_auc: float | None = None
    feature_count: int | None = None
    description: str | None = None


@router.post("")
def register_model(
    payload: ModelRegistrationRequest,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(ModelRegistry)
        .filter(
            ModelRegistry.version == payload.version,
            ModelRegistry.model_name == payload.model_name,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Model version already registered",
        )

    model = ModelRegistry(
        model_name=payload.model_name,
        version=payload.version,
        model_type=payload.model_type,
        model_path=payload.model_path,
        status=payload.status,
        accuracy=payload.accuracy,
        precision=payload.precision,
        recall=payload.recall,
        f1_score=payload.f1_score,
        roc_auc=payload.roc_auc,
        feature_count=payload.feature_count,
        description=payload.description,
    )

    db.add(model)
    db.commit()
    db.refresh(model)

    return {
        "success": True,
        "model": model_to_dict(model),
    }
@router.post("/{model_id}/promote")
def promote_model(
    model_id: int,
    db: Session = Depends(get_db),
):
    candidate = (
        db.query(ModelRegistry)
        .filter(ModelRegistry.id == model_id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    if candidate.status != "CANDIDATE":
        raise HTTPException(
            status_code=400,
            detail="Only CANDIDATE models can be promoted",
        )

    active = get_active_model(db)

    if not active:
        raise HTTPException(
            status_code=404,
            detail="No active model found",
        )

    required_metrics = {
        "accuracy": candidate.accuracy,
        "precision": candidate.precision,
        "recall": candidate.recall,
        "f1_score": candidate.f1_score,
        "roc_auc": candidate.roc_auc,
    }

    if any(value is None for value in required_metrics.values()):
        raise HTTPException(
            status_code=400,
            detail="Candidate model is missing evaluation metrics",
        )

    if any(
        value is None
        for value in [
            active.accuracy,
            active.precision,
            active.recall,
            active.f1_score,
            active.roc_auc,
        ]
    ):
        raise HTTPException(
            status_code=400,
            detail="Active model is missing evaluation metrics",
        )

    comparison = {
        "accuracy": round(
            candidate.accuracy - active.accuracy,
            4,
        ),
        "precision": round(
            candidate.precision - active.precision,
            4,
        ),
        "recall": round(
            candidate.recall - active.recall,
            4,
        ),
        "f1_score": round(
            candidate.f1_score - active.f1_score,
            4,
        ),
        "roc_auc": round(
            candidate.roc_auc - active.roc_auc,
            4,
        ),
    }

    active.status = "ARCHIVED"
    candidate.status = "ACTIVE"

    db.commit()
    db.refresh(candidate)

    return {
        "success": True,
        "message": "Candidate model promoted successfully",
        "previous_active_version": active.version,
        "new_active_version": candidate.version,
        "comparison": comparison,
        "model": model_to_dict(candidate),
    }
@router.get("/comparison")
def compare_models(db: Session = Depends(get_db)):
    active = get_active_model(db)

    candidate = (
        db.query(ModelRegistry)
        .filter(ModelRegistry.status == "CANDIDATE")
        .order_by(ModelRegistry.created_at.desc())
        .first()
    )

    if not active:
        raise HTTPException(
            status_code=404,
            detail="No active model found",
        )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="No candidate model found",
        )

    metrics = [
        ("accuracy", active.accuracy, candidate.accuracy),
        ("precision", active.precision, candidate.precision),
        ("recall", active.recall, candidate.recall),
        ("f1_score", active.f1_score, candidate.f1_score),
        ("roc_auc", active.roc_auc, candidate.roc_auc),
    ]

    comparison = []

    for metric, active_value, candidate_value in metrics:
        comparison.append(
            {
                "metric": metric,
                "active": active_value,
                "candidate": candidate_value,
                "difference": round(
                    candidate_value - active_value,
                    4,
                ),
            }
        )

    return {
        "success": True,
        "active_model": {
            "id": active.id,
            "version": active.version,
            "status": active.status,
        },
        "candidate_model": {
            "id": candidate.id,
            "version": candidate.version,
            "status": candidate.status,
        },
        "comparison": comparison,
    }