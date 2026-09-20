import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

# Raw Kaggle dataset
CSV_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "shipment_data.csv"
)

# Processed dataset containing actual outcomes
PROCESSED_CSV_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "shipments_features.csv"
)

# Prediction batch output
OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "decision_batch_20.json"
)

# Actual outcome mapping
OUTCOME_OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "decision_batch_20_outcomes.json"
)


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
]


NUMERIC_COLUMNS = [
    "line item quantity",
    "line item value",
    "pack price",
    "unit price",
    "weight (kilograms)",
    "freight cost (usd)",
    "line item insurance (usd)",
]


def clean_value(value):
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")

    if hasattr(value, "item"):
        return value.item()

    return value


def main():

    print("=" * 60)
    print("SUPPLY PRESCRIPT - CREATE DECISION BATCH")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Validate input files
    # ---------------------------------------------------------

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Raw dataset not found:\n{CSV_PATH}"
        )

    if not PROCESSED_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Processed dataset not found:\n"
            f"{PROCESSED_CSV_PATH}"
        )

    # ---------------------------------------------------------
    # 2. Load raw and processed datasets
    # ---------------------------------------------------------

    raw_df = pd.read_csv(
        CSV_PATH,
        encoding="utf-8",
    )

    processed_df = pd.read_csv(
        PROCESSED_CSV_PATH,
        encoding="utf-8",
    )

    print(
        f"Loaded raw dataset: "
        f"{len(raw_df):,} rows"
    )

    print(
        f"Loaded processed dataset: "
        f"{len(processed_df):,} rows"
    )

    # ---------------------------------------------------------
    # 3. Validate ID columns
    # ---------------------------------------------------------

    if "id" not in raw_df.columns:
        raise ValueError(
            "Raw dataset does not contain 'id'."
        )

    if "id" not in processed_df.columns:
        raise ValueError(
            "Processed dataset does not contain 'id'."
        )

    outcome_columns = [
        "id",
        "actual_delay_days",
        "delay_flag",
    ]

    missing_outcome_columns = [
        column
        for column in outcome_columns
        if column not in processed_df.columns
    ]

    if missing_outcome_columns:
        raise ValueError(
            "Processed dataset is missing outcome columns:\n"
            + "\n".join(
                f"- {column}"
                for column in missing_outcome_columns
            )
        )

    # ---------------------------------------------------------
    # 4. Merge raw + processed data using shipment ID
    # ---------------------------------------------------------

    outcome_df = processed_df[
        [
            "id",
            "actual_delay_days",
            "delay_flag",
        ]
    ].copy()

    raw_df["id"] = pd.to_numeric(
        raw_df["id"],
        errors="coerce",
    )

    outcome_df["id"] = pd.to_numeric(
        outcome_df["id"],
        errors="coerce",
    )

    df = raw_df.merge(
        outcome_df,
        on="id",
        how="inner",
        validate="one_to_one",
    )

    print(
        f"Merged dataset: "
        f"{len(df):,} rows"
    )

    if len(df) == 0:
        raise ValueError(
            "Raw and processed datasets could not be "
            "matched using 'id'."
        )

    # ---------------------------------------------------------
    # 5. Validate required prediction columns
    # ---------------------------------------------------------

    required_columns = FEATURES + [
        "id",
        "scheduled delivery date",
        "actual_delay_days",
        "delay_flag",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Merged dataset is missing required columns:\n"
            + "\n".join(
                f"- {column}"
                for column in missing_columns
            )
        )

    # ---------------------------------------------------------
    # 6. Convert numeric columns
    # ---------------------------------------------------------

    df["id"] = pd.to_numeric(
        df["id"],
        errors="coerce",
    )

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df["actual_delay_days"] = pd.to_numeric(
        df["actual_delay_days"],
        errors="coerce",
    )

    df["delay_flag"] = pd.to_numeric(
        df["delay_flag"],
        errors="coerce",
    )

    # ---------------------------------------------------------
    # 7. Convert scheduled delivery date
    # ---------------------------------------------------------

    df["scheduled delivery date"] = pd.to_datetime(
        df["scheduled delivery date"],
        errors="coerce",
        format="mixed",
    )

    # ---------------------------------------------------------
    # 8. Remove incomplete rows
    # ---------------------------------------------------------

    df = df.dropna(
        subset=required_columns
    ).copy()

    print(
        f"Valid rows after cleaning: "
        f"{len(df):,}"
    )

    if len(df) < 20:
        raise ValueError(
            f"Only {len(df)} valid rows are available. "
            f"At least 20 are required."
        )

    # ---------------------------------------------------------
    # 9. Date features
    # ---------------------------------------------------------

    df["scheduled_year"] = (
        df["scheduled delivery date"].dt.year
    )

    df["scheduled_month"] = (
        df["scheduled delivery date"].dt.month
    )

    df["scheduled_day_of_week"] = (
        df["scheduled delivery date"].dt.dayofweek
    )

    # ---------------------------------------------------------
    # 10. Derived numeric features
    # ---------------------------------------------------------

    safe_value = df[
        "line item value"
    ].replace(
        0,
        pd.NA,
    )

    safe_quantity = df[
        "line item quantity"
    ].replace(
        0,
        pd.NA,
    )

    df["freight_cost_ratio"] = (
        df["freight cost (usd)"]
        / safe_value
    ).fillna(0)

    df["insurance_cost_ratio"] = (
        df["line item insurance (usd)"]
        / safe_value
    ).fillna(0)

    df["weight_per_unit"] = (
        df["weight (kilograms)"]
        / safe_quantity
    ).fillna(0)

    # ---------------------------------------------------------
    # 11. Transport risk score
    # ---------------------------------------------------------

    transport_risk_map = {
        "Air": 0.20,
        "Air Charter": 0.25,
        "Truck": 0.40,
        "Rail": 0.50,
        "Ocean": 0.65,
    }

    df["transport_risk_score"] = (
        df["shipment mode"]
        .astype(str)
        .str.strip()
        .map(transport_risk_map)
        .fillna(0.50)
    )

    # ---------------------------------------------------------
    # 12. High-value shipment
    # ---------------------------------------------------------

    df["high_value_shipment"] = (
        df["line item value"] >= 10000
    ).astype(int)

    # ---------------------------------------------------------
    # 13. Shipment complexity score
    # ---------------------------------------------------------

    complexity_components = (
        df["shipment mode"]
        .astype(str)
        .ne("")
        .astype(int)
        + df["vendor"]
        .astype(str)
        .ne("")
        .astype(int)
        + df["manufacturing site"]
        .astype(str)
        .ne("")
        .astype(int)
        + df["product group"]
        .astype(str)
        .ne("")
        .astype(int)
        + (
            df["line item quantity"] > 100
        ).astype(int)
    )

    df["shipment_complexity_score"] = (
        complexity_components / 5.0
    )

    # ---------------------------------------------------------
    # 14. Select 20 real shipments
    # ---------------------------------------------------------

    sample = df.sample(
        n=20,
        random_state=42,
    )

    print(
        f"Selected {len(sample)} real CSV shipments."
    )

    records = []
    outcome_records = []

    # ---------------------------------------------------------
    # 15. Build prediction and outcome records
    # ---------------------------------------------------------

    for _, row in sample.iterrows():

        shipment_id = int(
            row["id"]
        )

        quantity = float(
            row["line item quantity"]
        )

        value = float(
            row["line item value"]
        )

        # -----------------------------------------------------
        # Prediction payload
        # -----------------------------------------------------

        record = {
            "shipment_id": shipment_id,

            "country": clean_value(
                row["country"]
            ),

            "shipment mode": clean_value(
                row["shipment mode"]
            ),

            "product group": clean_value(
                row["product group"]
            ),

            "sub classification": clean_value(
                row["sub classification"]
            ),

            "vendor": clean_value(
                row["vendor"]
            ),

            "manufacturing site": clean_value(
                row["manufacturing site"]
            ),

            "line item quantity": quantity,

            "line item value": value,

            "pack price": float(
                row["pack price"]
            ),

            "unit price": float(
                row["unit price"]
            ),

            "weight (kilograms)": float(
                row["weight (kilograms)"]
            ),

            "freight cost (usd)": float(
                row["freight cost (usd)"]
            ),

            "line item insurance (usd)": float(
                row["line item insurance (usd)"]
            ),

            "scheduled_year": int(
                row["scheduled_year"]
            ),

            "scheduled_month": int(
                row["scheduled_month"]
            ),

            "scheduled_day_of_week": int(
                row["scheduled_day_of_week"]
            ),

            "freight_cost_ratio": float(
                row["freight_cost_ratio"]
            ),

            "insurance_cost_ratio": float(
                row["insurance_cost_ratio"]
            ),

            "weight_per_unit": float(
                row["weight_per_unit"]
            ),

            "transport_risk_score": float(
                row["transport_risk_score"]
            ),

            "high_value_shipment": int(
                row["high_value_shipment"]
            ),

            "shipment_complexity_score": float(
                row["shipment_complexity_score"]
            ),
        }

        records.append(record)

        # -----------------------------------------------------
        # Historical actual outcome
        # -----------------------------------------------------

        actual_delay_flag = int(
            row["delay_flag"]
        )

        outcome_records.append(
            {
                "shipment_id": shipment_id,

                "actual_delay_days": float(
                    row["actual_delay_days"]
                ),

                "actual_delay_flag": actual_delay_flag,

                "actual_cost_usd": float(
                    row["freight cost (usd)"]
                ),

                "outcome_status": (
                    "DELAYED"
                    if actual_delay_flag == 1
                    else "ON_TIME"
                ),

                "outcome_notes": (
                    "Actual historical outcome "
                    "from Kaggle shipment dataset."
                ),
            }
        )

    # ---------------------------------------------------------
    # 16. Save prediction batch
    # ---------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # ---------------------------------------------------------
    # 17. Save outcome mapping
    # ---------------------------------------------------------

    with open(
        OUTCOME_OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            outcome_records,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # ---------------------------------------------------------
    # 18. Summary
    # ---------------------------------------------------------

    delayed_count = sum(
        item["actual_delay_flag"] == 1
        for item in outcome_records
    )

    on_time_count = (
        len(outcome_records)
        - delayed_count
    )

    print()
    print("=" * 60)
    print("SUCCESS")
    print("=" * 60)

    print(
        f"Generated prediction records: "
        f"{len(records)}"
    )

    print(
        f"Historical delayed shipments: "
        f"{delayed_count}"
    )

    print(
        f"Historical on-time shipments: "
        f"{on_time_count}"
    )

    print()
    print(
        f"Prediction output:\n{OUTPUT_PATH}"
    )

    print(
        f"Outcome output:\n{OUTCOME_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()