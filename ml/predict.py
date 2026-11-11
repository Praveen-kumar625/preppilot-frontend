import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import joblib
import numpy as np
import pandas as pd

class ReadinessPredictor:
    """
    Inference module for PrePilot interview readiness prediction.
    Loads the persistent Scikit-learn Pipeline and provides robust input
    validation, graceful handling of missing/unseen values, and probability estimation.
    """
    _instance: Optional["ReadinessPredictor"] = None

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        metadata_path: Optional[Union[str, Path]] = None
    ):
        base_dir = Path(__file__).resolve().parent

        if model_path is None:
            model_path = base_dir / "preppilot_readiness_model.joblib"
        self.model_path = Path(model_path)

        if metadata_path is None:
            metadata_path = base_dir / "model_metadata.json"
            if not metadata_path.exists():
                metadata_path = base_dir.parent / "model_metadata.json"
        self.metadata_path = Path(metadata_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at: {self.model_path}. "
                "Ensure Phase 1 export has completed."
            )

        # Measure model loading time
        start_load = time.perf_counter()
        self.model = joblib.load(self.model_path)
        self.load_time_seconds = time.perf_counter() - start_load

        # Load metadata
        if self.metadata_path.exists():
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

        self.numeric_features = self.metadata.get(
            "feature_specifications", {}
        ).get("numeric_features", [])

        self.categorical_features = self.metadata.get(
            "feature_specifications", {}
        ).get("categorical_features", [])

        self.medians = self.metadata.get(
            "feature_specifications", {}
        ).get("numeric_medians", {})

        self.supported_roles = self.metadata.get(
            "feature_specifications", {}
        ).get("supported_target_roles", [
            "AI/ML Engineer",
            "Data Engineer / Analyst",
            "Full Stack Web Developer",
            "Software Development Engineer (SDE)",
            "Technical Support / QA Engineer"
        ])

        self.feature_columns = self.numeric_features + self.categorical_features
        self.classes = list(self.model.classes_)

    @classmethod
    def get_instance(cls) -> "ReadinessPredictor":
        """Singleton accessor to prevent reloading the model from disk on every invocation."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def validate_and_sanitize(self, profile: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Validates input dictionary, casts types, bounds values, and imputes missing items.
        Returns: (is_valid, sanitized_profile, warnings_list)
        """
        warnings: List[str] = []
        if not isinstance(profile, dict):
            return False, {}, ["Input profile must be a dictionary."]

        sanitized: Dict[str, Any] = {}

        # 1. Process Numeric Features
        for feat in self.numeric_features:
            val = profile.get(feat, None)
            if val is None or val == "":
                # Impute with training median as fallback
                fallback_val = self.medians.get(feat, 50.0)
                sanitized[feat] = fallback_val
                warnings.append(f"Missing numeric feature '{feat}'; defaulted to benchmark median {fallback_val}.")
                continue

            try:
                num_val = float(val)
            except (ValueError, TypeError):
                fallback_val = self.medians.get(feat, 50.0)
                sanitized[feat] = fallback_val
                warnings.append(f"Invalid non-numeric value for '{feat}'; defaulted to median {fallback_val}.")
                continue

            # Range sanity checks and clamping
            if feat == "cgpa":
                if num_val < 0.0 or num_val > 10.0:
                    clamped = max(0.0, min(10.0, num_val))
                    warnings.append(f"CGPA {num_val} is outside [0.0, 10.0]; clamped to {clamped}.")
                    num_val = clamped
            elif "percentage" in feat or "score" in feat:
                if num_val < 0.0 or num_val > 100.0:
                    clamped = max(0.0, min(100.0, num_val))
                    warnings.append(f"Score '{feat}' {num_val} outside [0.0, 100.0]; clamped to {clamped}.")
                    num_val = clamped
            elif "count" in feat or "solved" in feat or "attempted" in feat or "months" in feat or "hours" in feat or "tests" in feat:
                if num_val < 0.0:
                    warnings.append(f"Negative count for '{feat}' {num_val}; clamped to 0.")
                    num_val = 0.0

            sanitized[feat] = num_val

        # 2. Process Categorical Features
        # target_role_match
        role = profile.get("target_role_match")
        if not role:
            default_role = "Software Development Engineer (SDE)"
            sanitized["target_role_match"] = default_role
            warnings.append(f"Missing 'target_role_match'; defaulted to '{default_role}'.")
        else:
            role_str = str(role).strip()
            if role_str not in self.supported_roles:
                warnings.append(f"Unseen target role '{role_str}'. Will be encoded gracefully by pipeline.")
            sanitized["target_role_match"] = role_str

        # university_year
        year = profile.get("university_year")
        if not year:
            sanitized["university_year"] = "Fourth Year"
            warnings.append("Missing 'university_year'; defaulted to 'Fourth Year'.")
        else:
            sanitized["university_year"] = str(year).strip()

        # degree
        deg = profile.get("degree")
        if not deg:
            sanitized["degree"] = "B.Tech"
            warnings.append("Missing 'degree'; defaulted to 'B.Tech'.")
        else:
            sanitized["degree"] = str(deg).strip()

        # specialization
        spec = profile.get("specialization")
        if not spec:
            sanitized["specialization"] = "CSE"
            warnings.append("Missing 'specialization'; defaulted to 'CSE'.")
        else:
            sanitized["specialization"] = str(spec).strip()

        return True, sanitized, warnings

    def predict(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes prediction without retraining.
        Measures exact inference execution time and returns class label,
        individual probabilities, confidence, and validation status.
        """
        start_time = time.perf_counter()

        is_valid, sanitized_profile, warnings = self.validate_and_sanitize(profile)
        if not is_valid:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "status": "error",
                "error_message": "; ".join(warnings),
                "predicted_class": None,
                "confidence": None,
                "probabilities": None,
                "target_role": None,
                "inference_time_ms": round(latency_ms, 3),
                "warnings": warnings
            }

        try:
            # Build 1-row DataFrame preserving exact column order
            input_df = pd.DataFrame([sanitized_profile])[self.feature_columns]

            # Model inference (transform + predict)
            preds = self.model.predict(input_df)
            probas = self.model.predict_proba(input_df)[0]

            predicted_class = str(preds[0])
            prob_dict = {
                cls: round(float(prob), 4)
                for cls, prob in zip(self.classes, probas)
            }
            confidence = round(float(np.max(probas)), 4)

            latency_ms = (time.perf_counter() - start_time) * 1000.0

            return {
                "status": "success",
                "predicted_class": predicted_class,
                "confidence": confidence,
                "probabilities": prob_dict,
                "target_role": sanitized_profile.get("target_role_match"),
                "inference_time_ms": round(latency_ms, 3),
                "warnings": warnings
            }

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "status": "error",
                "error_message": f"Inference execution failed: {str(e)}",
                "predicted_class": None,
                "confidence": None,
                "probabilities": None,
                "target_role": sanitized_profile.get("target_role_match"),
                "inference_time_ms": round(latency_ms, 3),
                "warnings": warnings
            }

    def predict_batch(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch prediction utility for evaluating multiple student profiles."""
        return [self.predict(p) for p in profiles]


def predict_readiness(profile: Dict[str, Any], model_path: Optional[str] = None) -> Dict[str, Any]:
    """Top-level convenience function for single-profile prediction."""
    predictor = ReadinessPredictor.get_instance() if model_path is None else ReadinessPredictor(model_path=model_path)
    return predictor.predict(profile)


if __name__ == "__main__":
    print("Testing ReadinessPredictor directly from CLI...")
    predictor = ReadinessPredictor()
    print(f"Model loaded successfully in {predictor.load_time_seconds:.4f} seconds.")

    sample = {
        "cgpa": 8.8,
        "target_role_match": "Software Development Engineer (SDE)",
        "dsa_score": 85.0,
        "python_score": 80.0,
        "coding_questions_solved": 420,
        "medium_questions_solved": 210,
        "mock_interview_score": 82.0,
        "communication_score": 78.0
    }

    result = predictor.predict(sample)
    print("\nInference Output:")
    print(json.dumps(result, indent=2))
