from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "shipments_features.csv"
)

DATABASE_URL = (
    "postgresql+psycopg2://"
    "supply_user:supply_password@localhost:5433/"
    "supply_prescript"
)

TABLE_NAME = "shipments"


def main():
    print("=" * 60)
    print("SUPPLY PRESCRIPT - LOAD SHIPMENTS INTO POSTGRESQL")
    print("=" * 60)

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATA_FILE}\n"
            "Run feature_engineering.py first."
        )

    print("\n[1/4] Reading processed dataset...")

    df = pd.read_csv(DATA_FILE)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\n[2/4] Connecting to PostgreSQL...")

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )

    # Test connection
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    print("PostgreSQL connection successful.")

    print("\n[3/4] Loading data...")

    df.to_sql(
        TABLE_NAME,
        engine,
        if_exists="replace",
        index=False,
        chunksize=1000,
        method="multi",
    )

    print(f"Loaded {len(df):,} rows into '{TABLE_NAME}'.")

    print("\n[4/4] Verifying database...")

    with engine.connect() as connection:
        result = connection.execute(
            text(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        )

        count = result.scalar()

    print(f"Database row count: {count:,}")

    if count != len(df):
        raise RuntimeError(
            "Row count mismatch between CSV and PostgreSQL."
        )

    print("\n" + "=" * 60)
    print("DATABASE LOAD SUCCESSFUL")
    print("=" * 60)


if __name__ == "__main__":
    main()