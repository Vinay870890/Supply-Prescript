from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "shipments_features.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "ml"
)


TARGET = "delay_flag"


# These are outcome/leakage columns.
LEAKAGE_COLUMNS = [
    "delay_flag",
    "actual_delay_days",
    "delivered to client date",
    "delivery recorded date",
]


def main():

    print("=" * 60)
    print("SUPPLY PRESCRIPT - ML DATA PREPARATION")
    print("=" * 60)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(f"\nDataset rows    : {len(df):,}")
    print(f"Dataset columns : {len(df.columns):,}")

    # --------------------------------------------------
    # Remove rows without target
    # --------------------------------------------------

    df = df.dropna(subset=[TARGET])

    df[TARGET] = df[TARGET].astype(int)

    # --------------------------------------------------
    # Separate features and target
    # --------------------------------------------------

    X = df.drop(
        columns=LEAKAGE_COLUMNS,
        errors="ignore",
    )

    y = df[TARGET]

    # Remove identifier from ML features
    X = X.drop(
        columns=["id"],
        errors="ignore",
    )

    print(f"\nFeatures: {X.shape[1]}")
    print(f"Target  : {TARGET}")

    print("\nTarget distribution:")
    print(y.value_counts())

    print("\nTarget percentage:")
    print(
        (y.value_counts(normalize=True) * 100)
        .round(2)
    )

    # --------------------------------------------------
    # Train / test split
    # --------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    # --------------------------------------------------
    # Train / validation split
    # --------------------------------------------------

    X_train, X_val, y_train, y_val = train_test_split(
        X_train,
        y_train,
        test_size=0.20,
        random_state=42,
        stratify=y_train,
    )

    print("\nDataset split:")
    print(f"Train      : {len(X_train):,}")
    print(f"Validation : {len(X_val):,}")
    print(f"Test       : {len(X_test):,}")

    # --------------------------------------------------
    # Save splits
    # --------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    X_train.to_csv(
        OUTPUT_DIR / "X_train.csv",
        index=False,
    )

    X_val.to_csv(
        OUTPUT_DIR / "X_val.csv",
        index=False,
    )

    X_test.to_csv(
        OUTPUT_DIR / "X_test.csv",
        index=False,
    )

    y_train.to_csv(
        OUTPUT_DIR / "y_train.csv",
        index=False,
    )

    y_val.to_csv(
        OUTPUT_DIR / "y_val.csv",
        index=False,
    )

    y_test.to_csv(
        OUTPUT_DIR / "y_test.csv",
        index=False,
    )

    print("\nSaved ML datasets to:")
    print(OUTPUT_DIR)

    print("\n" + "=" * 60)
    print("ML DATA PREPARATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()