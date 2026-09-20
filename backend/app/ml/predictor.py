import pandas as pd

from app.ml.model_loader import load_active_model


THRESHOLD = 0.55


class ShipmentPredictor:

    def __init__(self):
        self.model, self.model_record = load_active_model()

    def predict(self, features: dict):

        data = pd.DataFrame([features])

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

        prediction = int(probability >= THRESHOLD)

        return {
            "delay_probability": round(probability, 4),
            "delay_prediction": prediction,
            "risk_level": risk_level,
            "threshold": THRESHOLD,
            "model_version": self.model_record.version,
        }


predictor = ShipmentPredictor()