from sqlalchemy.orm import Session

from app.models.model_registry import ModelRegistry


def register_model(
    db: Session,
    model_name: str,
    version: str,
    model_type: str,
    model_path: str,
    status: str = "CANDIDATE",
    accuracy: float | None = None,
    precision: float | None = None,
    recall: float | None = None,
    f1_score: float | None = None,
    roc_auc: float | None = None,
    feature_count: int | None = None,
    description: str | None = None,
):
    model = ModelRegistry(
        model_name=model_name,
        version=version,
        model_type=model_type,
        model_path=model_path,
        status=status,
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        roc_auc=roc_auc,
        feature_count=feature_count,
        description=description,
    )

    db.add(model)
    db.commit()
    db.refresh(model)

    return model


def get_all_models(db: Session):
    return (
        db.query(ModelRegistry)
        .order_by(ModelRegistry.created_at.desc())
        .all()
    )


def get_active_model(db: Session):
    return (
        db.query(ModelRegistry)
        .filter(ModelRegistry.status == "ACTIVE")
        .order_by(ModelRegistry.created_at.desc())
        .first()
    )