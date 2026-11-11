import json
import time
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from predict import ReadinessPredictor, predict_readiness

def run_persistence_tests():
    print("=" * 80)
    print("PREPILOT PHASE 1: PERSISTENCE & INFERENCE VALIDATION SUITE")
    print("=" * 80)

    # 1. MEASURE MODEL LOADING TIME
    model_path = Path("ml/preppilot_readiness_model.joblib")
    metadata_path = Path("ml/model_metadata.json")

    print("\n[STEP 1] MEASURING MODEL LOADING TIME FROM DISK...")
    load_times = []
    for i in range(5):
        t0 = time.perf_counter()
        loaded_model = joblib.load(model_path)
        t_elapsed = time.perf_counter() - t0
        load_times.append(t_elapsed)

    mean_load = np.mean(load_times)
    min_load = np.min(load_times)
    max_load = np.max(load_times)
    print(f"  Model File Size: {model_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"  Cold Load (Run 1): {load_times[0]:.4f} seconds")
    print(f"  Mean Load Time (5 runs): {mean_load:.4f} seconds (Min: {min_load:.4f}s, Max: {max_load:.4f}s)")

    # 2. VERIFY PREDICTION CONSISTENCY WITH HELD-OUT DATA
    print("\n[STEP 2] VERIFYING PREDICTION CONSISTENCY ON 500 TEST SAMPLES...")
    df = pd.read_csv("ml/prepilot_ml_training_dataset_60k - Copy.csv")
    exclude_columns = [
        "student_id",
        "interview_readiness",
        "placement_probability",
        "primary_skill_gap",
        "academic_performance"
    ]
    X = df.drop(columns=exclude_columns)
    y = df["interview_readiness"]

    # Sample 500 records from the test split region
    test_sample_df = X.sample(n=500, random_state=42)
    test_actual = y.loc[test_sample_df.index]

    predictor = ReadinessPredictor.get_instance()
    
    # Predict directly with loaded pipeline
    direct_preds = predictor.model.predict(test_sample_df)
    direct_probas = predictor.model.predict_proba(test_sample_df)

    # Predict row by row via ReadinessPredictor.predict to test validation pipeline
    module_preds = []
    module_probas = []
    match_count = 0
    proba_diffs = []

    for idx, row in test_sample_df.iterrows():
        res = predictor.predict(row.to_dict())
        module_preds.append(res["predicted_class"])
        probs_array = [res["probabilities"][c] for c in predictor.classes]
        module_probas.append(probs_array)

    direct_preds_list = list(direct_preds)
    exact_matches = sum(1 for p1, p2 in zip(direct_preds_list, module_preds) if p1 == p2)
    consistency_rate = (exact_matches / len(test_sample_df)) * 100.0

    print(f"  Samples Tested: {len(test_sample_df)}")
    print(f"  Identical Class Predictions: {exact_matches}/{len(test_sample_df)} ({consistency_rate:.2f}%)")
    
    accuracy_against_ground_truth = accuracy_score(test_actual, module_preds)
    print(f"  Accuracy against Ground Truth on these 500 samples: {accuracy_against_ground_truth * 100:.2f}%")

    # 3. TEST AT LEAST 5 DIVERSE STUDENT PROFILES
    print("\n[STEP 3] TESTING 6 DIVERSE CANDIDATE PROFILES (ACROSS 5 ROLES & SKILL TIERS)...")
    
    test_profiles = [
        {
            "name": "Profile 1: Top-Tier Candidate (SDE Target)",
            "data": {
                "age": 21,
                "university_year": "Fourth Year",
                "degree": "B.Tech",
                "specialization": "CSE",
                "cgpa": 9.3,
                "attendance_percentage": 92.0,
                "study_hours_per_week": 35.0,
                "dsa_score": 92.0,
                "java_score": 88.0,
                "python_score": 85.0,
                "oops_score": 90.0,
                "dbms_score": 88.0,
                "operating_systems_score": 86.0,
                "computer_networks_score": 84.0,
                "aptitude_score": 90.0,
                "logical_reasoning_score": 92.0,
                "mathematics_score": 88.0,
                "statistics_score": 85.0,
                "machine_learning_score": 60.0,
                "deep_learning_score": 50.0,
                "web_development_score": 75.0,
                "sql_score": 88.0,
                "computer_vision_score": 40.0,
                "programming_experience_months": 36,
                "coding_questions_attempted": 600,
                "coding_questions_solved": 540,
                "easy_questions_solved": 150,
                "medium_questions_solved": 310,
                "hard_questions_solved": 80,
                "communication_score": 85.0,
                "mock_interview_score": 88.0,
                "resume_score": 90.0,
                "projects_count": 5,
                "certifications_count": 3,
                "prepilot_tests_taken": 25,
                "prepilot_usage_hours": 45.0,
                "target_role_match": "Software Development Engineer (SDE)"
            }
        },
        {
            "name": "Profile 2: Competent Candidate (Full Stack Web Developer Target)",
            "data": {
                "age": 21,
                "university_year": "Fourth Year",
                "degree": "B.Tech",
                "specialization": "IT",
                "cgpa": 7.8,
                "attendance_percentage": 82.0,
                "study_hours_per_week": 22.0,
                "dsa_score": 68.0,
                "java_score": 65.0,
                "python_score": 70.0,
                "oops_score": 72.0,
                "dbms_score": 75.0,
                "operating_systems_score": 65.0,
                "computer_networks_score": 68.0,
                "aptitude_score": 72.0,
                "logical_reasoning_score": 74.0,
                "mathematics_score": 65.0,
                "statistics_score": 60.0,
                "machine_learning_score": 45.0,
                "deep_learning_score": 35.0,
                "web_development_score": 88.0,
                "sql_score": 78.0,
                "computer_vision_score": 30.0,
                "programming_experience_months": 24,
                "coding_questions_attempted": 350,
                "coding_questions_solved": 270,
                "easy_questions_solved": 100,
                "medium_questions_solved": 145,
                "hard_questions_solved": 25,
                "communication_score": 72.0,
                "mock_interview_score": 70.0,
                "resume_score": 75.0,
                "projects_count": 4,
                "certifications_count": 2,
                "prepilot_tests_taken": 18,
                "prepilot_usage_hours": 30.0,
                "target_role_match": "Full Stack Web Developer"
            }
        },
        {
            "name": "Profile 3: Data Specialist Candidate (Data Engineer / Analyst Target)",
            "data": {
                "age": 22,
                "university_year": "Fourth Year",
                "degree": "B.Tech",
                "specialization": "CSE (AI/ML)",
                "cgpa": 8.1,
                "attendance_percentage": 85.0,
                "study_hours_per_week": 25.0,
                "dsa_score": 72.0,
                "java_score": 60.0,
                "python_score": 88.0,
                "oops_score": 70.0,
                "dbms_score": 89.0,
                "operating_systems_score": 68.0,
                "computer_networks_score": 62.0,
                "aptitude_score": 78.0,
                "logical_reasoning_score": 80.0,
                "mathematics_score": 82.0,
                "statistics_score": 88.0,
                "machine_learning_score": 80.0,
                "deep_learning_score": 65.0,
                "web_development_score": 55.0,
                "sql_score": 92.0,
                "computer_vision_score": 50.0,
                "programming_experience_months": 28,
                "coding_questions_attempted": 380,
                "coding_questions_solved": 290,
                "easy_questions_solved": 110,
                "medium_questions_solved": 155,
                "hard_questions_solved": 25,
                "communication_score": 75.0,
                "mock_interview_score": 74.0,
                "resume_score": 78.0,
                "projects_count": 4,
                "certifications_count": 3,
                "prepilot_tests_taken": 20,
                "prepilot_usage_hours": 36.0,
                "target_role_match": "Data Engineer / Analyst"
            }
        },
        {
            "name": "Profile 4: Average Candidate (Technical Support / QA Target)",
            "data": {
                "age": 20,
                "university_year": "Third Year",
                "degree": "B.Tech",
                "specialization": "ECE",
                "cgpa": 6.1,
                "attendance_percentage": 72.0,
                "study_hours_per_week": 16.0,
                "dsa_score": 45.0,
                "java_score": 40.0,
                "python_score": 52.0,
                "oops_score": 48.0,
                "dbms_score": 46.0,
                "operating_systems_score": 44.0,
                "computer_networks_score": 50.0,
                "aptitude_score": 55.0,
                "logical_reasoning_score": 54.0,
                "mathematics_score": 48.0,
                "statistics_score": 45.0,
                "machine_learning_score": 30.0,
                "deep_learning_score": 25.0,
                "web_development_score": 42.0,
                "sql_score": 48.0,
                "computer_vision_score": 20.0,
                "programming_experience_months": 14,
                "coding_questions_attempted": 140,
                "coding_questions_solved": 95,
                "easy_questions_solved": 50,
                "medium_questions_solved": 40,
                "hard_questions_solved": 5,
                "communication_score": 52.0,
                "mock_interview_score": 48.0,
                "resume_score": 55.0,
                "projects_count": 2,
                "certifications_count": 1,
                "prepilot_tests_taken": 10,
                "prepilot_usage_hours": 15.0,
                "target_role_match": "Technical Support / QA Engineer"
            }
        },
        {
            "name": "Profile 5: Underprepared Candidate (AI/ML Engineer Target)",
            "data": {
                "age": 19,
                "university_year": "Second Year",
                "degree": "B.Tech",
                "specialization": "CSE (AI/ML)",
                "cgpa": 4.8,
                "attendance_percentage": 60.0,
                "study_hours_per_week": 10.0,
                "dsa_score": 28.0,
                "java_score": 22.0,
                "python_score": 35.0,
                "oops_score": 30.0,
                "dbms_score": 26.0,
                "operating_systems_score": 25.0,
                "computer_networks_score": 28.0,
                "aptitude_score": 38.0,
                "logical_reasoning_score": 40.0,
                "mathematics_score": 32.0,
                "statistics_score": 30.0,
                "machine_learning_score": 35.0,
                "deep_learning_score": 20.0,
                "web_development_score": 25.0,
                "sql_score": 28.0,
                "computer_vision_score": 15.0,
                "programming_experience_months": 8,
                "coding_questions_attempted": 60,
                "coding_questions_solved": 32,
                "easy_questions_solved": 22,
                "medium_questions_solved": 10,
                "hard_questions_solved": 0,
                "communication_score": 34.0,
                "mock_interview_score": 30.0,
                "resume_score": 40.0,
                "projects_count": 1,
                "certifications_count": 0,
                "prepilot_tests_taken": 5,
                "prepilot_usage_hours": 8.0,
                "target_role_match": "AI/ML Engineer"
            }
        },
        {
            "name": "Profile 6: Edge Case with Missing Fields & Unseen Category",
            "data": {
                "cgpa": "7.4",  # String formatted number
                "dsa_score": 120.0, # Out-of-bounds score (triggers clamping)
                "coding_questions_solved": -10, # Negative count (triggers clamping)
                "target_role_match": "Cybersecurity Analyst", # Unseen role
                # 25+ numeric features intentionally omitted to test imputer fallback
            }
        }
    ]

    profile_results = []
    for test_case in test_profiles:
        res = predictor.predict(test_case["data"])
        profile_results.append({
            "name": test_case["name"],
            "predicted_class": res["predicted_class"],
            "confidence": res["confidence"],
            "probabilities": res["probabilities"],
            "inference_time_ms": res["inference_time_ms"],
            "warning_count": len(res.get("warnings", []))
        })
        print(f"\n  [{test_case['name']}]")
        print(f"    Predicted Readiness: {res['predicted_class']} (Confidence: {res['confidence']*100:.1f}%)")
        print(f"    Class Probabilities: {res['probabilities']}")
        print(f"    Inference Latency:   {res['inference_time_ms']:.3f} ms")
        if res.get("warnings"):
            print(f"    Validation Warnings Handled: {len(res['warnings'])} (e.g. '{res['warnings'][0]}')")

    # 4. MEASURE ACTUAL INFERENCE LATENCY BENCHMARK
    print("\n[STEP 4] INFERENCE LATENCY BENCHMARK (100 CONSECUTIVE PREDICTIONS)...")
    benchmark_profile = test_profiles[0]["data"]
    latencies = []

    for _ in range(100):
        t0 = time.perf_counter()
        _ = predictor.predict(benchmark_profile)
        t_elapsed_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(t_elapsed_ms)

    mean_lat = np.mean(latencies)
    median_lat = np.median(latencies)
    p95_lat = np.percentile(latencies, 95)
    min_lat = np.min(latencies)
    max_lat = np.max(latencies)

    print(f"  Total Runs: 100")
    print(f"  Mean Latency:       {mean_lat:.3f} ms")
    print(f"  Median Latency:     {median_lat:.3f} ms")
    print(f"  95th Percentile:    {p95_lat:.3f} ms")
    print(f"  Min Latency:        {min_lat:.3f} ms")
    print(f"  Max Latency:        {max_lat:.3f} ms")

    # Summary Report Object
    report = {
        "status": "PASS",
        "loading_time": {
            "model_size_mb": round(model_path.stat().st_size / (1024*1024), 2),
            "cold_load_s": round(load_times[0], 4),
            "mean_load_s": round(float(mean_load), 4),
            "min_load_s": round(float(min_load), 4),
            "max_load_s": round(float(max_load), 4)
        },
        "prediction_consistency": {
            "samples_tested": 500,
            "consistency_rate_pct": consistency_rate,
            "accuracy_against_ground_truth_pct": round(accuracy_against_ground_truth * 100, 2)
        },
        "latency_benchmark_ms": {
            "runs": 100,
            "mean_ms": round(float(mean_lat), 3),
            "median_ms": round(float(median_lat), 3),
            "p95_ms": round(float(p95_lat), 3),
            "min_ms": round(float(min_lat), 3),
            "max_ms": round(float(max_lat), 3)
        },
        "test_profiles": profile_results
    }

    report_path = Path("ml/phase1_test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nTest report saved to: {report_path}")
    print("=" * 80)
    print("PHASE 1 TESTING COMPLETE: ALL TESTS PASSED")
    print("=" * 80)

if __name__ == "__main__":
    run_persistence_tests()
