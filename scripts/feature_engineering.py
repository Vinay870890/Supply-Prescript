from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "shipments_clean.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "shipments_features.csv"


def main():

    print("=" * 60)
    print("SUPPLY PRESCRIPT - FEATURE ENGINEERING")
    print("=" * 60)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {INPUT_FILE}\n"
            "Run prepare_data.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    # --------------------------------------------------
    # Date features
    # --------------------------------------------------

    date_columns = [
        "scheduled delivery date",
        "delivered to client date",
        "delivery recorded date",
    ]

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )

    df["scheduled_year"] = (
        df["scheduled delivery date"].dt.year
    )

    df["scheduled_month"] = (
        df["scheduled delivery date"].dt.month
    )

    df["scheduled_day_of_week"] = (
        df["scheduled delivery date"].dt.dayofweek
    )

    # --------------------------------------------------
    # Shipment value features
    # --------------------------------------------------

    df["total_shipment_value"] = (
        df["line item value"].fillna(0)
    )

    df["freight_cost_ratio"] = np.where(
        df["line item value"] > 0,
        df["freight cost (usd)"]
        / df["line item value"],
        0,
    )

    df["insurance_cost_ratio"] = np.where(
        df["line item value"] > 0,
        df["line item insurance (usd)"]
        / df["line item value"],
        0,
    )

    # --------------------------------------------------
    # Weight / quantity features
    # --------------------------------------------------

    df["weight_per_unit"] = np.where(
        df["line item quantity"] > 0,
        df["weight (kilograms)"]
        / df["line item quantity"],
        0,
    )

    # --------------------------------------------------
    # Logistics features
    # --------------------------------------------------

    # Shipping mode risk proxy.
    # This is NOT the prediction target.
    mode_risk_map = {
        "Air": 0.20,
        "Air Charter": 0.15,
        "Ocean": 0.65,
        "Truck": 0.45,
        "Rail": 0.40,
    }

    df["transport_risk_score"] = (
        df["shipment mode"]
        .map(mode_risk_map)
        .fillna(0.50)
    )

    # --------------------------------------------------
    # Business value / criticality proxy
    # --------------------------------------------------

    # Higher-value shipments have greater business impact.
    value_quantile = df["total_shipment_value"].quantile(
        0.75
    )

    df["high_value_shipment"] = (
        df["total_shipment_value"] >= value_quantile
    ).astype(int)

    # --------------------------------------------------
    # Shipment complexity
    # --------------------------------------------------

    df["shipment_complexity_score"] = (
        df["transport_risk_score"]
        + df["high_value_shipment"] * 0.25
        + (
            df["freight_cost_ratio"]
            .clip(0, 1)
        )
    )

    # --------------------------------------------------
    # Clean infinities
    # --------------------------------------------------

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------
    # Report
    # --------------------------------------------------

    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    new_features = [
        "scheduled_year",
        "scheduled_month",
        "scheduled_day_of_week",
        "total_shipment_value",
        "freight_cost_ratio",
        "insurance_cost_ratio",
        "weight_per_unit",
        "transport_risk_score",
        "high_value_shipment",
        "shipment_complexity_score",
    ]

    print("\nNew features:")
    for feature in new_features:
        print(f"  ✓ {feature}")

    print(f"\nSaved to:")
    print(OUTPUT_FILE)

    print("\nSample:")
    print(
        df[
            [
                "id",
                "shipment mode",
                "total_shipment_value",
                "transport_risk_score",
                "high_value_shipment",
                "shipment_complexity_score",
                "delay_flag",
            ]
        ].head(5).to_string(index=False)
    )

    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()