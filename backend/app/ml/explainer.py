from pathlib import Path

import joblib
import pandas as pd
import shap


BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_FILE = BASE_DIR / "models" / "delay_model_v2.joblib"


class ShipmentExplainer:
    def __init__(self):
        if not MODEL_FILE.exists():
            raise FileNotFoundError(f"Model not found: {MODEL_FILE}")

        self.model = joblib.load(MODEL_FILE)

        self.preprocessor = self.model.named_steps["preprocessor"]
        self.classifier = self.model.named_steps["model"]

        self.explainer = shap.TreeExplainer(self.classifier)

    def _clean_feature_name(self, feature_name: str) -> str:
        """
        Convert sklearn transformed feature names into
        human-readable feature names.
        """

        name = feature_name

        if name.startswith("num__"):
            name = name.replace("num__", "", 1)

        elif name.startswith("cat__"):
            name = name.replace("cat__", "", 1)

        return name

    def explain(self, features: dict, top_n: int = 5) -> dict:
        data = pd.DataFrame([features])

        transformed = self.preprocessor.transform(data)

        if hasattr(transformed, "toarray"):
            transformed = transformed.toarray()

        shap_values = self.explainer.shap_values(transformed)

        values = shap_values[0]

        feature_names = self.preprocessor.get_feature_names_out()

        explanations = []

        for name, value in zip(feature_names, values):

            # Ignore inactive one-hot categories.
            # A categorical feature is only relevant when
            # its encoded value is actually 1.
            if name.startswith("cat__"):

                transformed_index = list(feature_names).index(name)

                if transformed[0][transformed_index] == 0:
                    continue

            clean_name = self._clean_feature_name(name)

            explanations.append(
                {
                    "feature": clean_name,
                    "impact": round(float(value), 6),
                    "direction": (
                        "increases_delay_risk"
                        if value > 0
                        else "decreases_delay_risk"
                    ),
                }
            )

        explanations.sort(
            key=lambda x: abs(x["impact"]),
            reverse=True,
        )

        return {
            "top_features": explanations[:top_n],
        }


explainer = ShipmentExplainer()