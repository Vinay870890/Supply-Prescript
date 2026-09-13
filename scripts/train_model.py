from pathlib import Path
import json
import joblib
import pandas as pd

from xgboost import XGBClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)


BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = BASE_DIR / "data" / "processed" / "ml"
MODEL_DIR = BASE_DIR / "models"

MODEL_FILE = MODEL_DIR / "delay_model.joblib"
METRICS_FILE = MODEL_DIR / "model_metrics.json"


def load_data():
    X_train = pd.read_csv(ML_DIR / "X_train.csv")
    X_val = pd.read_csv(ML_DIR / "X_val.csv")
    X_test = pd.read_csv(ML_DIR / "X_test.csv")

    y_train = pd.read_csv(ML_DIR / "y_train.csv").iloc[:, 0]
    y_val = pd.read_csv(ML_DIR / "y_val.csv").iloc[:, 0]
    y_test = pd.read_csv(ML_DIR / "y_test.csv").iloc[:, 0]

    return X_train, X_val, X_test, y_train, y_val, y_test


def build_pipeline(X_train):
    categorical_features = X_train.select_dtypes(
        include=["object"]
    ).columns.tolist()

    numerical_features = X_train.select_dtypes(
        include=["number"]
    ).columns.tolist()

    print("\nCategorical features:")
    for col in categorical_features:
        print(f"  - {col}")

    print("\nNumerical features:")
    for col in numerical_features:
        print(f"  - {col}")

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            )
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                numeric_pipeline,
                numerical_features,
            ),
            (
                "cat",
                categorical_pipeline,
                categorical_features,
            ),
        ]
    )

    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipeline


def evaluate(model, X, y, dataset_name):
    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    metrics = {
        "accuracy": accuracy_score(y, predictions),
        "precision": precision_score(
            y,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y,
            predictions,
            zero_division=0,
        ),
        "roc_auc": roc_auc_score(
            y,
            probabilities,
        ),
    }

    print(f"\n{dataset_name} Results")
    print("-" * 40)

    for name, value in metrics.items():
        print(f"{name:<12}: {value:.4f}")

    return metrics


def main():
    print("=" * 60)
    print("SUPPLY PRESCRIPT - XGBOOST DELAY PREDICTION")
    print("=" * 60)

    X_train, X_val, X_test, y_train, y_val, y_test = load_data()

    print("\nDataset sizes:")
    print(f"Train      : {len(X_train):,}")
    print(f"Validation : {len(X_val):,}")
    print(f"Test       : {len(X_test):,}")

    pipeline = build_pipeline(X_train)

    print("\nTraining XGBoost...")
    pipeline.fit(X_train, y_train)

    print("\nTraining complete.")

    train_metrics = evaluate(
        pipeline,
        X_train,
        y_train,
        "TRAIN",
    )

    val_metrics = evaluate(
        pipeline,
        X_val,
        y_val,
        "VALIDATION",
    )

    test_metrics = evaluate(
        pipeline,
        X_test,
        y_test,
        "TEST",
    )

    # Save model
    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        pipeline,
        MODEL_FILE,
    )

    metrics = {
        "model": "XGBClassifier",
        "target": "delay_flag",
        "random_state": 42,
        "train": train_metrics,
        "validation": val_metrics,
        "test": test_metrics,
    }

    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )

    print("\nModel saved:")
    print(MODEL_FILE)

    print("\nMetrics saved:")
    print(METRICS_FILE)

    print("\n" + "=" * 60)
    print("MODEL TRAINING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()