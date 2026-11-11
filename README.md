# PrePilot - Interview Readiness Predictor

PrePilot predicts a student's interview readiness - **Poor, Average, Good or
Excellent** - from academic results, coding practice and preparation signals,
so students can see where they stand before the real interview.

The prediction comes from a Random Forest classifier served by a small
Python API in this repository. The React frontend in this repository is the
product interface for that model.

## Model card (from `ml/model_metadata.json`)

| | |
|---|---|
| Algorithm | RandomForestClassifier (100 trees, `random_state` 42, stratified split) |
| Features | 37 (33 numeric, 4 categorical) |
| Training data | 60,000 records - 48,000 train / 12,000 held-out test |
| Test accuracy | **92.89%** |
| Macro F1 | **90.38** |
| Weighted F1 | 92.91 |
| Baseline (DummyClassifier) accuracy | 47.11% |
| Supported degrees | B.Tech only |
| Supported target roles | AI/ML Engineer · Data Engineer / Analyst · Full Stack Web Developer · Software Development Engineer (SDE) · Technical Support / QA Engineer |

Missing input fields are filled with the training medians by the inference
pipeline, and every substitution is reported back in the API response as a
warning.

> Note: the training dataset CSV is not committed to this repository, so the
> model can be served and used, but not retrained from a fresh clone.

## Architecture

```
preppilot-frontend/
├── src/                  React frontend (Vite)
│   ├── pages/            Home, Login, Register (react-router-dom routes)
│   ├── components/       Navbar, Hero, Features, PredictorForm, Footer
│   └── lib/              Browser-local helpers (see "Accounts" below)
├── ml/                   Python ML side
│   ├── server.py         HTTP API on port 5000 (Python standard library only)
│   ├── predict.py        Inference pipeline (validation, imputation, prediction)
│   ├── train_readiness.py  Model training script
│   ├── export_model.py   Exports the .joblib pipeline + metadata
│   ├── model_metadata.json   Feature spec, medians and evaluation metrics
│   └── preppilot_readiness_model.joblib   Trained model pipeline
└── requirements.txt      Python dependencies
```

## Run it locally

You need two processes: the ML API and the frontend.

### 1. ML API (port 5000)

```bash
pip install -r requirements.txt
python ml/server.py
```

### 2. Frontend (Vite dev server)

```bash
npm install
npm run dev
```

Open the URL Vite prints (default http://localhost:5173). The readiness form
calls the ML API at `http://127.0.0.1:5000` by default. To point it
elsewhere, copy `.env.example` to `.env` and set `VITE_API_BASE_URL`.

### Other scripts

```bash
npm run build    # production build
npm run preview  # serve the production build
npm run lint     # ESLint
```

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Service status, model name and supported roles |
| GET | `/api/roles` | Supported target roles |
| POST | `/api/predict` | Readiness prediction for a profile |

`POST /api/predict` accepts a JSON object with any subset of the 37 model
features (see `ml/model_metadata.json` for the full list). Example:

```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"cgpa": 8.4, "dsa_score": 82, "target_role_match": "Software Development Engineer (SDE)"}'
```

Response:

```json
{
  "status": "success",
  "predicted_class": "Good",
  "confidence": 0.81,
  "probabilities": { "Average": 0.09, "Excellent": 0.08, "Good": 0.81, "Poor": 0.02 },
  "target_role": "Software Development Engineer (SDE)",
  "inference_time_ms": 12.4,
  "warnings": ["Missing numeric feature 'age'; defaulted to benchmark median 20.0."],
  "mode": "live_ml"
}
```

## Accounts - honest status

PrePilot has **no account server yet**. The Login and Register pages
validate the form in the browser and keep the sign-in in `localStorage` on
the user's own device only. No account is created on a server, no password
is stored or sent anywhere, and no page claims otherwise. When a real auth
backend exists, `src/lib/localUser.js` is the single place to replace.

## Known limitations

- The model cannot be retrained from this repository (dataset not committed).
- `ml/server.py` reports `records_evaluated: 60000` in its `model_info`
  block; the held-out evaluation actually used the 12,000-record test split
  recorded in `ml/model_metadata.json`.
- The frontend has no automated test suite yet; verification is lint +
  production build + manual/API smoke tests.
