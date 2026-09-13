from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "data" / "processed" / "ml"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "ml_v2"


FEATURE_COLUMNS = [
    # Business / categorical
    "country",
    "shipment mode",
    "product group",
    "sub classification",
    "vendor",
    "manufacturing site",

    # Shipment / financial
    "line item quantity",
    "line item value",
    "pack price",
    "unit price",
    "weight (kilograms)",
    "freight cost (usd)",
    "line item insurance (usd)",

    # Engineered features
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


def main():
    print("=" * 60)
    print("SUPPLY PRESCRIPT - ML FEATURE SELECTION V2")
    print("=" * 60)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for split in ["train", "val", "test"]:

        x_file = INPUT_DIR / f"X_{split}.csv"
        y_file = INPUT_DIR / f"y_{split}.csv"

        if not x_file.exists():
            raise FileNotFoundError(
                f"Missing file: {x_file}"
            )

        X = pd.read_csv(x_file)
        y = pd.read_csv(y_file)

        missing_features = [
            col
            for col in FEATURE_COLUMNS
            if col not in X.columns
        ]

        if missing_features:
            raise ValueError(
                f"Missing features in {split}: "
                f"{missing_features}"
            )

        X_selected = X[FEATURE_COLUMNS].copy()

        X_selected.to_csv(
            OUTPUT_DIR / f"X_{split}.csv",
            index=False,
        )

        y.to_csv(
            OUTPUT_DIR / f"y_{split}.csv",
            index=False,
        )

        print(
            f"{split.capitalize():<6}: "
            f"{len(X_selected):,} rows | "
            f"{len(X_selected.columns)} features"
        )

    print("\nSelected features:")

    for feature in FEATURE_COLUMNS:
        print(f"  ✓ {feature}")

    print("\nSaved to:")
    print(OUTPUT_DIR)

    print("\n" + "=" * 60)
    print("FEATURE SELECTION V2 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()