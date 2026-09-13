from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


BASE_DIR = Path(__file__).resolve().parent.parent

ML_DIR = BASE_DIR / "data" / "processed" / "ml_v2"
MODEL_FILE = BASE_DIR / "models" / "delay_model_v2.joblib"

THRESHOLD = 0.55


def main():

    print("=" * 60)
    print("SUPPLY PRESCRIPT - FINAL MODEL EVALUATION")
    print("=" * 60)

    model = joblib.load(MODEL_FILE)

    X_test = pd.read_csv(
        ML_DIR / "X_test.csv"
    )

    y_test = pd.read_csv(
        ML_DIR / "y_test.csv"
    ).iloc[:, 0]

    print(f"\nTest rows: {len(X_test):,}")
    print(f"Threshold: {THRESHOLD}")

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    predictions = (
        probabilities >= THRESHOLD
    ).astype(int)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities,
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
    )

    print("\nFINAL TEST RESULTS")
    print("-" * 40)

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    print(matrix)

    tn, fp, fn, tp = matrix.ravel()

    print("\nBusiness interpretation:")
    print(f"True Negatives  : {tn}")
    print(f"False Positives : {fp}")
    print(f"False Negatives : {fn}")
    print(f"True Positives  : {tp}")

    print("\n" + "=" * 60)
    print("FINAL MODEL EVALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()