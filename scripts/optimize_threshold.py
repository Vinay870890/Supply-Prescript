from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)


BASE_DIR = Path(__file__).resolve().parent.parent

ML_DIR = BASE_DIR / "data" / "processed" / "ml_v2"
MODEL_FILE = BASE_DIR / "models" / "delay_model_v2.joblib"


def evaluate_thresholds(model, X_val, y_val):

    probabilities = model.predict_proba(X_val)[:, 1]

    results = []

    thresholds = [
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
    ]

    for threshold in thresholds:

        predictions = (
            probabilities >= threshold
        ).astype(int)

        results.append(
            {
                "threshold": threshold,
                "accuracy": accuracy_score(
                    y_val,
                    predictions,
                ),
                "precision": precision_score(
                    y_val,
                    predictions,
                    zero_division=0,
                ),
                "recall": recall_score(
                    y_val,
                    predictions,
                    zero_division=0,
                ),
                "f1": f1_score(
                    y_val,
                    predictions,
                    zero_division=0,
                ),
            }
        )

    return pd.DataFrame(results)


def main():

    print("=" * 60)
    print("SUPPLY PRESCRIPT - THRESHOLD OPTIMIZATION")
    print("=" * 60)

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Model not found:\n{MODEL_FILE}"
        )

    X_val_file = ML_DIR / "X_val.csv"
    y_val_file = ML_DIR / "y_val.csv"

    if not X_val_file.exists():
        raise FileNotFoundError(
            f"Validation data not found:\n{X_val_file}"
        )

    print("\nLoading model and validation data...")

    model = joblib.load(MODEL_FILE)

    X_val = pd.read_csv(X_val_file)
    y_val = pd.read_csv(y_val_file).iloc[:, 0]

    print(
        f"Validation rows: {len(X_val):,}"
    )

    print("\nEvaluating thresholds...")

    results = evaluate_thresholds(
        model,
        X_val,
        y_val,
    )

    # Best F1
    best_f1 = results.loc[
        results["f1"].idxmax()
    ]

    # Best recall while maintaining precision >= 0.35
    precision_filtered = results[
        results["precision"] >= 0.35
    ]

    if not precision_filtered.empty:
        best_business = precision_filtered.loc[
            precision_filtered["recall"].idxmax()
        ]
    else:
        best_business = best_f1

    print("\n" + "-" * 60)
    print("THRESHOLD RESULTS")
    print("-" * 60)

    print(
        results.to_string(
            index=False,
            formatters={
                "threshold": "{:.2f}".format,
                "accuracy": "{:.4f}".format,
                "precision": "{:.4f}".format,
                "recall": "{:.4f}".format,
                "f1": "{:.4f}".format,
            },
        )
    )

    print("\n" + "-" * 60)
    print("BEST F1 THRESHOLD")
    print("-" * 60)

    print(
        f"Threshold : {best_f1['threshold']:.2f}"
    )
    print(
        f"Precision : {best_f1['precision']:.4f}"
    )
    print(
        f"Recall    : {best_f1['recall']:.4f}"
    )
    print(
        f"F1        : {best_f1['f1']:.4f}"
    )

    print("\n" + "-" * 60)
    print("BUSINESS-ORIENTED THRESHOLD")
    print("-" * 60)

    print(
        "Constraint: precision >= 0.35"
    )

    print(
        f"Threshold : "
        f"{best_business['threshold']:.2f}"
    )

    print(
        f"Precision : "
        f"{best_business['precision']:.4f}"
    )

    print(
        f"Recall    : "
        f"{best_business['recall']:.4f}"
    )

    print(
        f"F1        : "
        f"{best_business['f1']:.4f}"
    )

    print("\n" + "=" * 60)
    print("THRESHOLD ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()