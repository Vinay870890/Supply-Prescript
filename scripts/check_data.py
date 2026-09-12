from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "shipments_clean.csv"


def main():
    print("=" * 60)
    print("SUPPLY PRESCRIPT - DATA QUALITY CHECK")
    print("=" * 60)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Processed dataset not found:\n{INPUT_FILE}\n"
            "Run prepare_data.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    print(f"\nRows    : {len(df):,}")
    print(f"Columns : {len(df.columns)}")

    # Missing values
    print("\n--- Missing Values ---")
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        print("No missing values.")
    else:
        print(missing)

    # Duplicate IDs
    print("\n--- Duplicate Shipment IDs ---")
    duplicate_ids = df["id"].duplicated().sum()
    print(f"Duplicate IDs: {duplicate_ids}")

    # Target distribution
    print("\n--- Target Distribution ---")

    delay_counts = df["delay_flag"].value_counts().sort_index()

    print(
        f"On-time (0): "
        f"{delay_counts.get(0, 0):,}"
    )

    print(
        f"Delayed (1): "
        f"{delay_counts.get(1, 0):,}"
    )

    print(
        f"Delay rate: "
        f"{df['delay_flag'].mean() * 100:.2f}%"
    )

    # Delay statistics
    print("\n--- Delay Statistics ---")

    print(
        df["actual_delay_days"].describe()
        .to_string()
    )

    # Categorical distributions
    print("\n--- Shipment Modes ---")
    print(df["shipment mode"].value_counts())

    print("\n--- Product Groups ---")
    print(df["product group"].value_counts())

    print("\n--- Countries ---")
    print(df["country"].value_counts().head(10))

    # Numerical sanity checks
    print("\n--- Numerical Sanity Checks ---")

    checks = {
        "negative quantity":
            (df["line item quantity"] < 0).sum(),

        "negative value":
            (df["line item value"] < 0).sum(),

        "negative weight":
            (df["weight (kilograms)"] < 0).sum(),

        "negative freight":
            (df["freight cost (usd)"] < 0).sum(),

        "negative delay":
            (df["actual_delay_days"] < 0).sum(),
    }

    for name, count in checks.items():
        print(f"{name}: {count}")

    print("\n" + "=" * 60)
    print("DATA QUALITY CHECK COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()