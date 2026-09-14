import sys
from pathlib import Path

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "backend"

API_URL = "http://localhost:8001/api/decision"
CSV_PATH = PROJECT_ROOT / "data/processed/shipments_features.csv"

sys.path.insert(0, str(BACKEND_PATH))


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


def build_payload(row, df):
    payload = {}

    for feature in FEATURES:
        value = row[feature]

        if pd.isna(value):
            if df[feature].dtype == "object":
                value = "Unknown"
            else:
                value = 0

        if hasattr(value, "item"):
            value = value.item()

        payload[feature] = value

    return payload


def main():
    print("Loading shipment data...")

    df = pd.read_csv(CSV_PATH)
    row = df.iloc[0]

    payload = build_payload(row, df)

    print("Calling decision API...")

    response = requests.post(
        API_URL,
        json=payload,
        timeout=60,
    )

    print(f"HTTP STATUS: {response.status_code}")

    response.raise_for_status()

    result = response.json()

    assert result["success"] is True
    assert "prediction" in result
    assert "explanation" in result
    assert "recommendation" in result

    prediction = result["prediction"]
    explanation = result["explanation"]
    recommendation = result["recommendation"]

    assert "delay_probability" in prediction
    assert "risk_level" in prediction
    assert "top_features" in explanation
    assert "recommended_action" in recommendation
    assert "alternatives" in recommendation

    assert len(explanation["top_features"]) > 0
    assert len(recommendation["alternatives"]) == 3

    print("\nDECISION WORKFLOW TEST PASSED")
    print("==============================")

    print(
        f"Delay Probability: "
        f"{prediction['delay_probability']}"
    )

    print(
        f"Risk Level: "
        f"{prediction['risk_level']}"
    )

    print(
        f"Recommended Action: "
        f"{recommendation['recommended_action']}"
    )

    print("\nTop SHAP Reasons:")

    for item in explanation["top_features"]:
        print(
            f"  - {item['feature']}: "
            f"{item['impact']} "
            f"({item['direction']})"
        )

    print("\nAlternatives:")

    for action in recommendation["alternatives"]:
        print(
            f"  - {action['action']}: "
            f"score={action['objective_score']}, "
            f"cost=${action['estimated_cost_usd']}, "
            f"risk={action['expected_delay_risk']}"
        )


if __name__ == "__main__":
    main()