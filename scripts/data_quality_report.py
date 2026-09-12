from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "shipments_features.csv"
REPORT_FILE = BASE_DIR / "data" / "processed" / "data_quality_report.md"


def main():
    print("=" * 60)
    print("SUPPLY PRESCRIPT - DATA QUALITY REPORT")
    print("=" * 60)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    # Basic statistics
    rows = len(df)
    columns = len(df.columns)

    duplicate_rows = int(df.duplicated().sum())
    duplicate_ids = int(df["id"].duplicated().sum())

    missing_cells = int(df.isna().sum().sum())
    total_cells = df.shape[0] * df.shape[1]

    if total_cells > 0:
        missing_percentage = (
            missing_cells / total_cells
        ) * 100
    else:
        missing_percentage = 0

    delay_rate = df["delay_flag"].mean() * 100
    average_delay = df["actual_delay_days"].mean()
    max_delay = df["actual_delay_days"].max()

    # Shipment modes
    shipment_modes = (
        df["shipment mode"]
        .value_counts()
        .to_dict()
    )

    # Product groups
    product_groups = (
        df["product group"]
        .value_counts()
        .to_dict()
    )

    # Countries
    countries = (
        df["country"]
        .value_counts()
        .head(10)
        .to_dict()
    )

    # Numerical statistics
    numeric_columns = [
        "line item quantity",
        "line item value",
        "weight (kilograms)",
        "freight cost (usd)",
        "actual_delay_days",
    ]

    numeric_stats = (
        df[numeric_columns]
        .describe()
        .round(2)
    )

    # Start report
    report = []

    report.append("# Supply Prescript - Data Quality Report")
    report.append("")
    report.append("## Dataset Overview")
    report.append("")
    report.append("| Metric | Value |")
    report.append("|---|---:|")
    report.append(f"| Rows | {rows:,} |")
    report.append(f"| Columns | {columns:,} |")
    report.append(f"| Duplicate Rows | {duplicate_rows:,} |")
    report.append(f"| Duplicate Shipment IDs | {duplicate_ids:,} |")
    report.append(f"| Missing Cells | {missing_cells:,} |")
    report.append(
        f"| Missing Percentage | {missing_percentage:.2f}% |"
    )

    # Delay section
    report.append("")
    report.append("## Delay Target")
    report.append("")
    report.append("| Metric | Value |")
    report.append("|---|---:|")
    report.append(f"| Delay Rate | {delay_rate:.2f}% |")
    report.append(
        f"| Average Delay | {average_delay:.2f} days |"
    )
    report.append(
        f"| Maximum Delay | {max_delay:.0f} days |"
    )

    # Shipment modes
    report.append("")
    report.append("## Shipment Modes")
    report.append("")

    for mode, count in shipment_modes.items():
        report.append(
            f"- **{mode}**: {count:,}"
        )

    # Product groups
    report.append("")
    report.append("## Product Groups")
    report.append("")

    for group, count in product_groups.items():
        report.append(
            f"- **{group}**: {count:,}"
        )

    # Countries
    report.append("")
    report.append("## Top Countries")
    report.append("")

    for country, count in countries.items():
        report.append(
            f"- **{country}**: {count:,}"
        )

    # Numerical statistics
    report.append("")
    report.append("## Numerical Statistics")
    report.append("")

    report.append(
        numeric_stats.to_markdown()
    )

    # ML target definition
    report.append("")
    report.append("## ML Target Definition")
    report.append("")

    report.append("### delay_flag")
    report.append("")

    report.append(
        "A shipment is classified as delayed when:"
    )

    report.append("")
    report.append(
        "`actual delivery date > scheduled delivery date`"
    )

    report.append("")
    report.append(
        "`delay_flag = 1` means delayed."
    )

    report.append(
        "`delay_flag = 0` means on-time."
    )

    # Leakage prevention
    report.append("")
    report.append("## Target Leakage Prevention")
    report.append("")

    report.append(
        "The following outcome columns must NOT be used "
        "as model input features:"
    )

    report.append("")
    report.append("- `actual_delay_days`")
    report.append("- `delay_flag`")
    report.append("- `delivered to client date`")

    report.append("")
    report.append(
        "These values are only known after the shipment outcome."
    )

    # Pipeline
    report.append("")
    report.append("## Data Pipeline")
    report.append("")

    report.append(
        "Kaggle Dataset"
        " -> Data Cleaning"
        " -> Feature Engineering"
        " -> Quality Validation"
        " -> PostgreSQL"
    )

    # Status
    report.append("")
    report.append("## Status")
    report.append("")
    report.append(
        "Dataset preparation is complete and ready "
        "for the Day 3 machine-learning pipeline."
    )

    # Write report
    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("")
    print("Report created successfully:")
    print(REPORT_FILE)

    print("")
    print("=" * 60)
    print("DATA QUALITY REPORT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()