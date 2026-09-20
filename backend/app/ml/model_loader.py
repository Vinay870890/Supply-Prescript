from pathlib import Path

import joblib
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.model_registry import ModelRegistry


BASE_DIR = Path(__file__).resolve().parents[3]


def get_active_model_record(db: Session):
    model = (
        db.query(ModelRegistry)
        .filter(ModelRegistry.status == "ACTIVE")
        .order_by(ModelRegistry.created_at.desc())
        .first()
    )

    if not model:
        raise RuntimeError("No ACTIVE model found in model registry.")

    return model


def load_active_model():
    db = SessionLocal()

    try:
        model_record = get_active_model_record(db)

        model_path = BASE_DIR / model_record.model_path

        if not model_path.exists():
            raise FileNotFoundError(
                f"Active model file not found: {model_path}"
            )

        model = joblib.load(model_path)

        return model, model_record

    finally:
        db.close()