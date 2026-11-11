import { useEffect, useState } from "react";
import "./PredictorForm.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:5000";

// These roles match ml/model_metadata.json. They are only used until
// GET /api/roles answers, so the form still shows if the ML server is down.
const FALLBACK_ROLES = [
    "AI/ML Engineer",
    "Data Engineer / Analyst",
    "Full Stack Web Developer",
    "Software Development Engineer (SDE)",
    "Technical Support / QA Engineer",
];

const YEARS = ["First Year", "Second Year", "Third Year", "Fourth Year"];

const SPECIALIZATIONS = [
    "CSE",
    "CSE (AI/ML)",
    "Data Science",
    "ECE",
    "Information Technology",
];

const NUMERIC_FIELDS = [
    { name: "cgpa", label: "CGPA (0 - 10)", min: 0, max: 10, step: 0.1 },
    { name: "attendance_percentage", label: "Attendance %", min: 0, max: 100, step: 1 },
    { name: "study_hours_per_week", label: "Study hours / week", min: 0, max: 168, step: 1 },
    { name: "dsa_score", label: "DSA score (0 - 100)", min: 0, max: 100, step: 1 },
    { name: "python_score", label: "Python score (0 - 100)", min: 0, max: 100, step: 1 },
    { name: "aptitude_score", label: "Aptitude score (0 - 100)", min: 0, max: 100, step: 1 },
    { name: "communication_score", label: "Communication score (0 - 100)", min: 0, max: 100, step: 1 },
    { name: "mock_interview_score", label: "Mock interview score (0 - 100)", min: 0, max: 100, step: 1 },
    { name: "resume_score", label: "Resume score (0 - 100)", min: 0, max: 100, step: 1 },
    { name: "projects_count", label: "Projects completed", min: 0, max: 100, step: 1 },
    { name: "coding_questions_solved", label: "Coding questions solved", min: 0, max: 100000, step: 1 },
];

const CLASS_COLORS = {
    Poor: "#ef4444",
    Average: "#f59e0b",
    Good: "#635bff",
    Excellent: "#10b981",
};

function PredictorForm() {
    const [roles, setRoles] = useState(FALLBACK_ROLES);
    const [values, setValues] = useState({
        target_role_match: FALLBACK_ROLES[3],
        university_year: "Fourth Year",
        degree: "B.Tech",
        specialization: "CSE",
    });
    const [status, setStatus] = useState("idle"); // idle | loading | success | error
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        let cancelled = false;
        fetch(`${API_BASE}/api/roles`)
            .then((res) => (res.ok ? res.json() : null))
            .then((data) => {
                if (!cancelled && data && Array.isArray(data.roles) && data.roles.length > 0) {
                    setRoles(data.roles);
                }
            })
            .catch(() => {
                // Server not reachable: keep the roles from the list above.
            });
        return () => {
            cancelled = true;
        };
    }, []);

    function handleChange(event) {
        const { name, value } = event.target;
        setValues((prev) => ({ ...prev, [name]: value }));
    }

    async function handleSubmit(event) {
        event.preventDefault();
        setStatus("loading");
        setError("");
        setResult(null);

        const payload = { ...values };
        for (const field of NUMERIC_FIELDS) {
            const raw = values[field.name];
            if (raw !== undefined && raw !== "") {
                payload[field.name] = Number(raw);
            } else {
                delete payload[field.name];
            }
        }

        try {
            const response = await fetch(`${API_BASE}/api/predict`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await response.json();
            if (!response.ok || data.status !== "success") {
                throw new Error(data.error_message || `Prediction failed (HTTP ${response.status}).`);
            }
            setResult(data);
            setStatus("success");
        } catch (err) {
            const unreachable = err instanceof TypeError;
            setError(
                unreachable
                    ? `Could not reach the PrePilot ML server at ${API_BASE}. Start it with "python ml/server.py" and try again.`
                    : err.message
            );
            setStatus("error");
        }
    }

    const probabilities = result
        ? Object.entries(result.probabilities ?? {}).sort((a, b) => b[1] - a[1])
        : [];

    return (
        <section className="predictor" id="predictor">
            <div className="container">
                <div className="section-header">
                    <span className="section-label">Readiness Check</span>
                    <h2 className="section-title">How ready are you, honestly?</h2>
                    <p className="section-description">
                        Fill in what you know. The live Random Forest model
                        tells you your readiness class and how sure it is.
                        Fields you leave blank are filled with the model's
                        training middle values, and the API lists every such
                        fill as a warning below the result.
                    </p>
                </div>

                <form className="predictor-form card" onSubmit={handleSubmit}>
                    <div className="predictor-grid">
                        <label>
                            Target role
                            <select
                                name="target_role_match"
                                value={values.target_role_match}
                                onChange={handleChange}
                            >
                                {roles.map((role) => (
                                    <option key={role} value={role}>
                                        {role}
                                    </option>
                                ))}
                            </select>
                        </label>

                        <label>
                            University year
                            <select
                                name="university_year"
                                value={values.university_year}
                                onChange={handleChange}
                            >
                                {YEARS.map((year) => (
                                    <option key={year} value={year}>
                                        {year}
                                    </option>
                                ))}
                            </select>
                        </label>

                        <label>
                            Degree
                            <select
                                name="degree"
                                value={values.degree}
                                onChange={handleChange}
                            >
                                <option value="B.Tech">B.Tech</option>
                            </select>
                        </label>

                        <label>
                            Specialization
                            <select
                                name="specialization"
                                value={values.specialization}
                                onChange={handleChange}
                            >
                                {SPECIALIZATIONS.map((spec) => (
                                    <option key={spec} value={spec}>
                                        {spec}
                                    </option>
                                ))}
                            </select>
                        </label>

                        {NUMERIC_FIELDS.map((field) => (
                            <label key={field.name}>
                                {field.label}
                                <input
                                    type="number"
                                    name={field.name}
                                    min={field.min}
                                    max={field.max}
                                    step={field.step}
                                    value={values[field.name] ?? ""}
                                    onChange={handleChange}
                                    placeholder="Optional"
                                />
                            </label>
                        ))}
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={status === "loading"}
                    >
                        {status === "loading" ? "Checking..." : "Check My Readiness"}
                    </button>
                </form>

                {status === "error" && (
                    <div className="predictor-message predictor-error" role="alert">
                        {error}
                    </div>
                )}

                {status === "success" && result && (
                    <div className="predictor-result card" aria-live="polite">
                        <p className="predictor-result-label">Predicted readiness</p>
                        <p
                            className="predictor-result-class"
                            style={{ color: CLASS_COLORS[result.predicted_class] ?? "#0f172a" }}
                        >
                            {result.predicted_class}
                        </p>
                        <p className="predictor-result-meta">
                            Confidence {(result.confidence * 100).toFixed(1)}% ·
                            Target role: {result.target_role} ·
                            Prediction time {result.inference_time_ms} ms
                        </p>

                        <div className="predictor-bars">
                            {probabilities.map(([label, probability]) => (
                                <div className="predictor-bar-row" key={label}>
                                    <span className="predictor-bar-label">{label}</span>
                                    <span className="predictor-bar-track">
                                        <span
                                            className="predictor-bar-fill"
                                            style={{
                                                width: `${(probability * 100).toFixed(1)}%`,
                                                background: CLASS_COLORS[label] ?? "#635bff",
                                            }}
                                        />
                                    </span>
                                    <span className="predictor-bar-value">
                                        {(probability * 100).toFixed(1)}%
                                    </span>
                                </div>
                            ))}
                        </div>

                        {result.warnings && result.warnings.length > 0 && (
                            <details className="predictor-warnings">
                                <summary>
                                    {result.warnings.length} field(s) were filled by the model
                                </summary>
                                <ul>
                                    {result.warnings.map((warning, index) => (
                                        <li key={index}>{warning}</li>
                                    ))}
                                </ul>
                            </details>
                        )}
                    </div>
                )}
            </div>
        </section>
    );
}

export default PredictorForm;
