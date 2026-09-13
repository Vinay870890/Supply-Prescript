import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import pandas as pd

from app.ml.explainer import explainer

CSV_PATH = "data/processed/shipments_features.csv"

FEATURES = [
    "country",
    "shipment mode",
    "product group",
    "sub classification",
    "vendor",
    "manufacturing site",
    "line item quantity",
    "line item value",
    "pack price",
    "unit price",
    "weight (kilograms)",
    "freight cost (usd)",
    "line item insurance (usd)",
    "scheduled_year",
    "scheduled_month",
    "scheduled_day_of_week",
    "freight_cost_ratio",
    "insurance_cost_ratio",
    "weight_per_unit",
    "transport_risk_score",
    "high_value_shipment",
    "shipment_complexity_score",
]


df = pd.read_csv(CSV_PATH)

row = df.iloc[0]

features = {}

for feature in FEATURES:
    value = row[feature]

    if pd.isna(value):
        if df[feature].dtype == "object":
            value = "Unknown"
        else:
            value = 0

    if hasattr(value, "item"):
        value = value.item()

    features[feature] = value


result = explainer.explain(features, top_n=5)

print("\nSHAP EXPLANATION")
print("================")

for item in result["top_features"]:
    print(
        f"{item['feature']}: "
        f"{item['impact']} "
        f"({item['direction']})"
    )