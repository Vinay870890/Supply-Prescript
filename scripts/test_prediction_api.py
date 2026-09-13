import pandas as pd
import requests

CSV_PATH = "data/processed/shipments_features.csv"
API_URL = "http://localhost:8001/api/predictions"

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

# Use one real shipment
row = df.iloc[0]

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
response = requests.post(API_URL, json=payload, timeout=30)

print("HTTP STATUS:", response.status_code)
print("RESPONSE:")
print(response.json())

print("\nTEST SHIPMENT:")
print(payload)