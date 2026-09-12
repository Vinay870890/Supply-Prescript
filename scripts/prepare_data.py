from pathlib import Path
import pandas as pd
import numpy as np


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "shipment_data.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "shipments_clean.csv"


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

REQUIRED_COLUMNS = [
    "id",
    "country",
    "shipment mode",
    "scheduled delivery date",
    "delivered to client date",
    "delivery recorded date",
    "product group",
    "sub classification",
    "vendor",
    "line item quantity",
    "line item value",
    "pack price",
    "unit price",
    "manufacturing site",
    "weight (kilograms)",
    "freight cost (usd)",
    "line item insurance (usd)",
]


# ---------------------------------------------------------
# Main preparation function
# ---------------------------------------------------------

def prepare_data():

    print("=" * 60)
    print("SUPPLY PRESCRIPT - DATA PREPARATION")
    print("=" * 60)

    # Check input file
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"\nDataset not found:\n{INPUT_FILE}\n\n"
            "Put your Kaggle CSV inside data/raw/ and name it:\n"
            "shipment_data.csv"
        )

    print(f"\n[1/7] Reading dataset...")
    df = pd.read_csv(INPUT_FILE)

    print(f"Original rows    : {len(df):,}")
    print(f"Original columns : {len(df.columns)}")

    # -----------------------------------------------------
    # Check required columns
    # -----------------------------------------------------

    print("\n[2/7] Checking required columns...")

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns:\n{missing_columns}"
        )

    print("All required columns are present.")

    # -----------------------------------------------------
    # Remove exact duplicates
    # -----------------------------------------------------

    print("\n[3/7] Removing duplicate records...")

    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    print(f"Duplicates removed: {removed:,}")

    # -----------------------------------------------------
    # Date conversion
    # -----------------------------------------------------

    print("\n[4/7] Converting date columns...")

    date_columns = [
        "pq first sent to client date",
        "po sent to vendor date",
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

    # -----------------------------------------------------
    # Numeric conversion
    # -----------------------------------------------------

    print("\n[5/7] Cleaning numerical columns...")

    numeric_columns = [
        "line item quantity",
        "line item value",
        "pack price",
        "unit price",
        "weight (kilograms)",
        "freight cost (usd)",
        "line item insurance (usd)",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Handle categorical missing values
    # -----------------------------------------------------

    categorical_columns = [
        "country",
        "shipment mode",
        "product group",
        "sub classification",
        "vendor",
        "manufacturing site",
    ]

    for col in categorical_columns:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
            .fillna("Unknown")
        )

    # -----------------------------------------------------
    # Create target variables
    # -----------------------------------------------------

    print("\n[6/7] Creating delay features...")

    valid_dates = (
        df["scheduled delivery date"].notna()
        & df["delivered to client date"].notna()
    )

    # Delay in calendar days.
    # Negative values mean early delivery.
    delay_days = (
        df["delivered to client date"]
        - df["scheduled delivery date"]
    ).dt.days

    df["actual_delay_days"] = delay_days

    # We are predicting whether shipment was delayed.
    df["delay_flag"] = (
        df["actual_delay_days"] > 0
    ).astype(int)

    # If dates are invalid, target cannot be trusted.
    df.loc[~valid_dates, "actual_delay_days"] = np.nan
    df.loc[~valid_dates, "delay_flag"] = np.nan

    # Business-oriented derived features
    df["shipment_value_usd"] = (
        df["line item value"].fillna(0)
    )

    df["freight_cost_ratio"] = np.where(
        df["line item value"] > 0,
        df["freight cost (usd)"] / df["line item value"],
        np.nan,
    )

    df["insurance_cost_ratio"] = np.where(
        df["line item value"] > 0,
        df["line item insurance (usd)"] / df["line item value"],
        np.nan,
    )

    df["quantity_weight_ratio"] = np.where(
        df["weight (kilograms)"] > 0,
        df["line item quantity"] / df["weight (kilograms)"],
        np.nan,
    )

    # -----------------------------------------------------
    # Clean impossible values
    # -----------------------------------------------------

    # Quantity cannot be negative
    df.loc[
        df["line item quantity"] < 0,
        "line item quantity"
    ] = np.nan

    # Financial values cannot be negative
    for col in [
        "line item value",
        "pack price",
        "unit price",
        "freight cost (usd)",
        "line item insurance (usd)",
    ]:
        df.loc[df[col] < 0, col] = np.nan

    # Weight cannot be negative
    df.loc[
        df["weight (kilograms)"] < 0,
        "weight (kilograms)"
    ] = np.nan

    # -----------------------------------------------------
    # Final cleaning
    # -----------------------------------------------------

    # Remove rows where we cannot calculate the target.
    df = df.dropna(
        subset=[
            "scheduled delivery date",
            "delivered to client date",
            "actual_delay_days",
            "delay_flag",
        ]
    )

    # Convert target to integer after dropping invalid rows.
    df["actual_delay_days"] = (
        df["actual_delay_days"]
        .astype(int)
    )

    df["delay_flag"] = (
        df["delay_flag"]
        .astype(int)
    )

    # Sort by scheduled delivery date
    df = df.sort_values(
        "scheduled delivery date"
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # Save processed dataset
    # -----------------------------------------------------

    print("\n[7/7] Saving processed dataset...")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # -----------------------------------------------------
    # Report
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("DATA PREPARATION COMPLETE")
    print("=" * 60)

    print(f"\nFinal rows       : {len(df):,}")
    print(f"Final columns    : {len(df.columns)}")

    print("\nDelay statistics:")
    print(
        f"Delayed shipments : "
        f"{df['delay_flag'].sum():,}"
    )

    print(
        f"On-time shipments : "
        f"{(df['delay_flag'] == 0).sum():,}"
    )

    print(
        f"Delay rate        : "
        f"{df['delay_flag'].mean() * 100:.2f}%"
    )

    print(
        f"Average delay     : "
        f"{df['actual_delay_days'].mean():.2f} days"
    )

    print(
        f"Maximum delay     : "
        f"{df['actual_delay_days'].max()} days"
    )

    print(f"\nOutput:")
    print(OUTPUT_FILE)

    print("\nFirst 5 records:")
    print(
        df[
            [
                "id",
                "country",
                "shipment mode",
                "scheduled delivery date",
                "delivered to client date",
                "actual_delay_days",
                "delay_flag",
            ]
        ].head().to_string(index=False)
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    prepare_data()