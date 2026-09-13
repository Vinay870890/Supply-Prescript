from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

MODEL_FILE = (
    BASE_DIR
    / "models"
    / "delay_model_v2.joblib"
)

THRESHOLD = 0.55


class ShipmentPredictor:

    def __init__(self):
        if not MODEL_FILE.exists():
            raise FileNotFoundError(
                f"Model not found: {MODEL_FILE}"
            )

        self.model = joblib.load(MODEL_FILE)

    def predict(self, features: dict) -> dict:

        data = pd.DataFrame(
            [features]
        )

        probability = float(
            self.model.predict_proba(data)[0][1]
        )

        if probability < 0.30:
            risk_level = "LOW"

        elif probability < 0.60:
            risk_level = "MEDIUM"

        elif probability < 0.80:
            risk_level = "HIGH"

        else:
            risk_level = "CRITICAL"

        prediction = int(
            probability >= THRESHOLD
        )

        return {
            "delay_probability": round(
                probability,
                4,
            ),
            "delay_prediction": prediction,
            "risk_level": risk_level,
            "threshold": THRESHOLD,
        }


predictor = ShipmentPredictor()