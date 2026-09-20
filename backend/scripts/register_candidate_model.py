import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

from app.db.session import SessionLocal
from app.models.model_registry import ModelRegistry


BASE_DIR = Path(__file__).resolve().parents[2]

METRICS_FILE = (
    BASE_DIR
    / "models"
    / "model_metrics_v2_1_candidate.json"
)


def main():
    if not METRICS_FILE.exists():
        raise FileNotFoundError(
            f"Metrics file not found: {METRICS_FILE}"
        )

    with open(METRICS_FILE, "r", encoding="utf-8") as file:
        metrics = json.load(file)

    test_metrics = metrics["test"]

    db = SessionLocal()

    try:
        existing = (
            db.query(ModelRegistry)
            .filter(
                ModelRegistry.version == "v2.1-candidate"
            )
            .first()
        )

        if existing:
            print(
                f"Candidate already registered: "
                f"{existing.model_name} {existing.version}"
            )
            return

        model = ModelRegistry(
            model_name="Supply Prescript Delay Predictor",
            version="v2.1-candidate",
            model_type="XGBoost Classifier",
            model_path="models/delay_model_v2_1_candidate.joblib",
            status="CANDIDATE",
            accuracy=test_metrics["accuracy"],
            precision=test_metrics["precision"],
            recall=test_metrics["recall"],
            f1_score=test_metrics["f1"],
            roc_auc=test_metrics["roc_auc"],
            feature_count=22,
            description=(
                "Candidate XGBoost model trained with the "
                "Supply Prescript ML pipeline for evaluation "
                "against active model v2.0."
            ),
        )

        db.add(model)
        db.commit()
        db.refresh(model)

        print(f"Registered candidate model ID: {model.id}")
        print(f"Model: {model.model_name}")
        print(f"Version: {model.version}")
        print(f"Status: {model.status}")
        print(f"Accuracy: {model.accuracy:.4f}")
        print(f"Precision: {model.precision:.4f}")
        print(f"Recall: {model.recall:.4f}")
        print(f"F1: {model.f1_score:.4f}")
        print(f"ROC-AUC: {model.roc_auc:.4f}")

    finally:
        db.close()


if __name__ == "__main__":
    main()