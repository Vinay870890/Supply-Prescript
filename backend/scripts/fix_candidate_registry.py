import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.models.model_registry import ModelRegistry

def main():
    db = SessionLocal()

    try:
        model = (
            db.query(ModelRegistry)
            .filter(
                ModelRegistry.version == "v2.1-candidate"
            )
            .first()
        )

        if not model:
            raise RuntimeError(
                "v2.1-candidate model not found in registry"
            )

        model.model_path = (
            "models/delay_model_v2_1_candidate.joblib"
        )

        model.status = "ACTIVE"

        model.accuracy = 0.7883777239709443
        model.precision = 0.3275862068965517
        model.recall = 0.8016877637130801
        model.f1_score = 0.46511627906976744
        model.roc_auc = 0.8712399246600007

        model.description = (
            "Candidate XGBoost model retrained and evaluated "
            "using the Supply Prescript ML pipeline."
        )

        db.commit()
        db.refresh(model)

        print("Candidate registry updated successfully.")
        print(f"ID: {model.id}")
        print(f"Version: {model.version}")
        print(f"Status: {model.status}")
        print(f"Model path: {model.model_path}")
        print(f"Accuracy: {model.accuracy:.4f}")
        print(f"Precision: {model.precision:.4f}")
        print(f"Recall: {model.recall:.4f}")
        print(f"F1: {model.f1_score:.4f}")
        print(f"ROC-AUC: {model.roc_auc:.4f}")

    finally:
        db.close()


if __name__ == "__main__":
    main()