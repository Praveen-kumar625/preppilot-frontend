
import pandas as pd
from sklearn.dummy import DummyClassifier

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

file_path = "ml/prepilot_ml_training_dataset_60k - Copy.csv"
df = pd.read_csv(file_path)

target = "interview_readiness"

exclude_columns = [
    "student_id",
    "interview_readiness",
    "placement_probability",
    "primary_skill_gap",
    "academic_performance",
    "target_role_match"
]

X = df.drop(columns=exclude_columns)
y = df[target]

# Identify numeric and categorical features
numeric_features = X.select_dtypes(
    include=["number"]
).columns.tolist()

categorical_features = X.select_dtypes(
    exclude=["number"]
).columns.tolist()

print("Numeric features:", len(numeric_features))
print("Categorical features:", len(categorical_features))
print("Total features:", X.shape[1])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Handle missing numeric values
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median"))
])

# Handle missing categorical values and convert text to numbers
categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

# Combine both preprocessing pipelines
preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features)
])

print("\nTraining rows:", X_train.shape[0])
print("Testing rows:", X_test.shape[0])

print("\nPreprocessing pipeline created successfully!")

# Train a Random Forest classifier
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    ))
])

print("\nTraining Random Forest model...")
model.fit(X_train, y_train)

# Make predictions on unseen test data
y_pred = model.predict(X_test)

# Evaluate model separately for each job role


# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))
# Compare against a simple baseline
baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_train, y_train)

baseline_pred = baseline.predict(X_test)
baseline_accuracy = accuracy_score(y_test, baseline_pred)

print("\nBaseline Accuracy:", round(baseline_accuracy * 100, 2), "%")
print("Random Forest Accuracy:", round(accuracy * 100, 2), "%")
print(
    "Improvement over baseline:",
    round((accuracy - baseline_accuracy) * 100, 2),
    "percentage points"
)