import pandas as pd
import shap

from app.ml.model_loader import load_active_model


class ShipmentExplainer:
    def __init__(self):
        self.model, self.model_record = load_active_model()

        self.preprocessor = self.model.named_steps["preprocessor"]
        self.classifier = self.model.named_steps["model"]

        self.explainer = shap.TreeExplainer(self.classifier)

    def _clean_feature_name(self, name: str) -> str:
        return (
            name.replace("num__", "")
            .replace("cat__", "")
            .replace("_", " ")
        )

    def explain(self, features: dict, top_n: int = 5) -> dict:
        data = pd.DataFrame([features])

        transformed_data = self.preprocessor.transform(data)

        shap_values = self.explainer.shap_values(transformed_data)

        if isinstance(shap_values, list):
            values = shap_values[1][0]
        else:
            values = shap_values[0]

        feature_names = self.preprocessor.get_feature_names_out()

        contributions = []

        for name, value in zip(feature_names, values):
            value = float(value)

            if abs(value) < 1e-9:
                continue

            contributions.append(
                {
                    "feature": self._clean_feature_name(name),
                    "impact": round(value, 6),
                    "direction": (
                        "increases_delay_risk"
                        if value > 0
                        else "decreases_delay_risk"
                    ),
                }
            )

        contributions.sort(
            key=lambda item: abs(item["impact"]),
            reverse=True,
        )

        return {
            "model_version": self.model_record.version,
            "top_features": contributions[:top_n],
        }


explainer = ShipmentExplainer()