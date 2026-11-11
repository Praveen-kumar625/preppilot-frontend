import json
import time
from datetime import datetime
from pathlib import Path
import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import sklearn

def train_and_export():
    print("=" * 80)
    print("PREPILOT PHASE 1: MODEL TRAINING & PERSISTENCE")
    print("=" * 80)

    dataset_path = Path("ml/prepilot_ml_training_dataset_60k - Copy.csv")
    model_output_path = Path("ml/preppilot_readiness_model.joblib")
    metadata_output_path = Path("ml/model_metadata.json")

    print(f"Loading dataset from: {dataset_path}")
    start_load = time.time()
    df = pd.read_csv(dataset_path)
    print(f"Loaded {len(df)} records in {time.time() - start_load:.2f} seconds.")

    target = "interview_readiness"
    exclude_columns = [
        "student_id",
        "interview_readiness",
        "placement_probability",
        "primary_skill_gap",
        "academic_performance"
    ]

    X = df.drop(columns=exclude_columns)
    y = df[target]

    numeric_features = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=["number"]).columns.tolist()

    print(f"Numeric features ({len(numeric_features)}): {numeric_features}")
    print(f"Categorical features ({len(categorical_features)}): {categorical_features}")

    # Stratified 80/20 train/test split (exact same seed & split as train_readiness.py)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median"))
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ])

    model_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1
        ))
    ])

    print("\nFitting Random Forest pipeline on 48,000 training records...")
    start_fit = time.time()
    model_pipeline.fit(X_train, y_train)
    fit_duration = time.time() - start_fit
    print(f"Pipeline fitted successfully in {fit_duration:.2f} seconds.")

    # Evaluate on unseen held-out test data
    print("\nEvaluating model on 12,000 held-out test records...")
    y_pred = model_pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    # Baseline comparison
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X_train, y_train)
    baseline_pred = baseline.predict(X_test)
    baseline_accuracy = accuracy_score(y_test, baseline_pred)

    print(f"Held-out Test Accuracy: {accuracy * 100:.2f}%")
    print(f"Baseline (Most Frequent) Accuracy: {baseline_accuracy * 100:.2f}%")
    print(f"Net Improvement over Baseline: {(accuracy - baseline_accuracy) * 100:.2f} percentage points")
    print("\nClassification Report Summary:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Save fitted pipeline with joblib
    print(f"\nPersisting fitted pipeline to: {model_output_path}")
    start_save = time.time()
    joblib.dump(model_pipeline, model_output_path, compress=3)
    save_duration = time.time() - start_save
    file_size_mb = model_output_path.stat().st_size / (1024 * 1024)
    print(f"Saved {file_size_mb:.2f} MB pipeline in {save_duration:.2f} seconds.")

    # Calculate numeric feature default medians for inference imputation reference
    medians = df[numeric_features].median().round(2).to_dict()

    # Save model metadata
    metadata = {
        "model_name": "PrePilot Interview Readiness Classifier",
        "model_version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "algorithm": "RandomForestClassifier",
        "framework": f"scikit-learn {sklearn.__version__}",
        "dataset_information": {
            "source_file": dataset_path.name,
            "total_records": len(df),
            "train_records": len(X_train),
            "test_records": len(X_test),
            "target_variable": target,
            "classes": sorted(list(model_pipeline.classes_))
        },
        "feature_specifications": {
            "total_features": len(numeric_features) + len(categorical_features),
            "numeric_count": len(numeric_features),
            "categorical_count": len(categorical_features),
            "numeric_features": numeric_features,
            "categorical_features": categorical_features,
            "numeric_medians": medians,
            "supported_target_roles": sorted(df["target_role_match"].unique().tolist()),
            "supported_degrees": sorted(df["degree"].unique().tolist()),
            "supported_years": sorted(df["university_year"].unique().tolist()),
            "supported_specializations": sorted(df["specialization"].unique().tolist())
        },
        "training_configuration": {
            "test_size": 0.2,
            "random_state": 42,
            "stratified": True,
            "n_estimators": 100,
            "class_weight": "balanced",
            "n_jobs": -1
        },
        "evaluation_metrics": {
            "test_accuracy": round(accuracy * 100, 2),
            "baseline_accuracy": round(baseline_accuracy * 100, 2),
            "improvement_percentage_points": round((accuracy - baseline_accuracy) * 100, 2),
            "macro_f1": round(report_dict["macro avg"]["f1-score"] * 100, 2),
            "weighted_f1": round(report_dict["weighted avg"]["f1-score"] * 100, 2),
            "class_metrics": {
                cls: {
                    "precision": round(report_dict[cls]["precision"], 3),
                    "recall": round(report_dict[cls]["recall"], 3),
                    "f1_score": round(report_dict[cls]["f1-score"], 3),
                    "support": report_dict[cls]["support"]
                }
                for cls in model_pipeline.classes_
            }
        }
    }

    with open(metadata_output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Model metadata saved to: {metadata_output_path}")
    print("=" * 80)
    print("PHASE 1 EXPORT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    train_and_export()
