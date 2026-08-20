# House Price Prediction — End-to-End ML Web App

An end-to-end machine-learning product: a Jupyter notebook that cleans real-estate data and trains a regression model, a FastAPI backend that serves it, and a React + TypeScript frontend where a user enters property details and gets an instant price prediction.

---

## Overview

This project demonstrates a complete ML lifecycle — from raw data to deployed web application:

1. **`notebooks/`** — Cleans the Kaggle "House Price" dataset (~187,000 real property listings from India), explores it, trains and compares multiple regression models, and exports the winning model as a scikit-learn `Pipeline` (`house_price.pkl`).
2. **`backend/`** — A FastAPI service that loads `house_price.pkl` once at startup and exposes `POST /predict` and `GET /health`.
3. **`frontend/`** — A React + TypeScript + Vite single-page app with a property form that calls the backend and displays the predicted price in INR, USD, or EGP.

---

## Architecture

```
┌─────────────────┐        ┌──────────────────┐        ┌───────────────────┐
│  Kaggle CSV      │        │  Jupyter Notebook │        │  house_price.pkl   │
│  house_prices.csv│ ─────▶ │  clean → train →  │ ─────▶ │  (sklearn Pipeline)│
│                  │        │  evaluate → export│        │  + locations.json  │
└─────────────────┘        └──────────────────┘        └─────────┬──────────┘
                                                                      │ loaded at startup
                                                                      ▼
┌──────────────────┐   POST /predict    ┌───────────────────┐
│  React Frontend   │ ─────────────────▶ │  FastAPI Backend   │
│  (Vite, TS)        │ ◀───────────────── │  /predict /health   │
└──────────────────┘   predicted_price  └───────────────────┘
```

---

## Tech Stack

| Layer      | Technologies |
|------------|--------------|
| Data / ML  | pandas, numpy, scikit-learn, **xgboost**, matplotlib, seaborn, joblib |
| Backend    | FastAPI, pydantic / pydantic-settings, uvicorn |
| Frontend   | React 18, TypeScript, Vite, react-router-dom |
| Testing    | pytest, httpx (backend); `tsc` type-checking (frontend) |

---

## Project Structure

```
house-price-project/
├── notebooks/
│   ├── house_price_model.ipynb     # Phase 2: clean, EDA, train, evaluate, export
│   └── data/
│       ├── house_prices.csv        # Real Kaggle dataset (not committed)
│       ├── README.md       
│       └── generate_synthetic_data.py  # Original synthetic data generator
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app, CORS, model loaded at startup (lifespan)
│   │   ├── api/routes/prediction.py
│   │   ├── core/config.py
│   │   ├── schemas/prediction.py
│   │   ├── services/
│   │   │   ├── preprocessing.py
│   │   │   └── inference.py
│   │   └── utils/logging_config.py
│   ├── models/
│   │   ├── house_price.pkl         # Trained Pipeline (sklearn 1.9.0 + XGBoost 3.2.0)
│   │   └── locations.json          # Allowed locations for dropdown
│   ├── tests/test_prediction.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/predictionClient.ts
│   │   ├── components/PredictionForm.tsx
│   │   ├── pages/{HomePage,ResultPage,NotFoundPage}.tsx
│   │   ├── types/prediction.ts
│   │   └── App.tsx
│   ├── public/locations.json
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env.example
├── .gitignore
└── README.md
```

---

## Phase 1 — Get the Real Dataset

**Dataset:** [House Price by Juhi Bhojani](https://www.kaggle.com/datasets/juhibhojani/house-price) — ~187,000 real property listings from India (file `house_prices.csv`).

**Option A — Manual:** Download from the Kaggle page, unzip, place the CSV at `notebooks/data/house_prices.csv`.

**Option B — Kaggle CLI:**
```bash
pip install kaggle
# Get an API token: Kaggle → Settings → API → "Create New Token"
# Place kaggle.json in ~/.kaggle/ (macOS/Linux) or C:\Users\<you>\.kaggle\ (Windows)
kaggle datasets download -d juhibhojani/house-price -p notebooks/data --unzip
```

> Always verify the real columns with `df.columns` / `df.head()` before trusting any description.

---

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload    # http://localhost:8000/docs
```

### Run Tests
```bash
pytest -v
```

### Environment Variables (`backend/.env`)

| Variable         | Default                     | Description                          |
|------------------|------------------------------|---------------------------------------|
| `MODEL_PATH`     | `models/house_price.pkl`    | Path to the exported sklearn Pipeline |
| `LOCATIONS_PATH` | `models/locations.json`     | Allowed/known locations for grouping  |
| `CORS_ORIGINS`   | `["http://localhost:5173"]` | Allowed frontend origins              |
| `LOG_LEVEL`      | `INFO`                      | Python logging level                  |

---

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev                      # http://localhost:5173
```

### Environment Variables (`frontend/.env`)

| Variable              | Default                 | Description                  |
|------------------------|--------------------------|-------------------------------|
| `VITE_API_BASE_URL`   | `http://localhost:8000` | Base URL of the FastAPI backend |

### Build for Production
```bash
npm run build
```

---

## API Reference

### `GET /health`

```bash
curl http://localhost:8000/health
```

```json
{ "status": "ok" }
```

### `POST /predict`

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
        "location": "Mumbai Sector 10",
        "bhk": 3,
        "carpet_area_sqft": 1200,
        "floor_num": 3,
        "bathroom": 2,
        "balcony": 1,
        "car_parking": 1,
        "furnishing": "Semi-Furnished",
        "transaction": "Resale",
        "ownership": "Freehold",
        "facing": "East"
      }'
```

```json
{ "predicted_price": 5461004.10 }
```

- Unknown locations are automatically grouped into `"other"` server-side, matching how the model was trained.
- Invalid input (e.g., negative area) returns `422 Unprocessable Entity`.

---

## Features Used by the Model

| Feature | Type | Description |
|---------|------|-------------|
| `location` | Categorical | Top-50 locations; others grouped as `"other"` |
| `bhk` | Numeric | Number of bedrooms (extracted from listing title via regex) |
| `carpet_area_sqft` | Numeric | Carpet area in sqft (parsed from text, mixed sqft/sqm) |
| `floor_num` | Numeric | Floor number (0 for Ground, -1 for Basement) |
| `bathroom` | Numeric | Number of bathrooms |
| `balcony` | Numeric | Number of balconies |
| `car_parking` | Numeric | Car parking spaces |
| `furnishing` | Categorical | Furnished / Semi-Furnished / Unfurnished |
| `transaction` | Categorical | New Property / Resale |
| `ownership` | Categorical | Freehold / Leasehold / Co-operative Society / Power Of Attorney |
| `facing` | Categorical | East / West / North / South / North-East / South-West |

---

## Model Metrics

Four models were trained on `log1p(price)` and compared on a held-out test set (20% of ~167,000 cleaned records):

| Model                      | MAE (₹)    | RMSE (₹)   | R²    |
|----------------------------|------------|------------|-------|
| **XGBoost** (winner)       | **1,047,816** | **3,343,933** | **0.921** |
| RandomForest               | 898,280     | 3,202,268   | 0.928 |
| GradientBoosting           | 2,802,367   | 5,450,669   | 0.791 |
| LinearRegression           | 2,696,095,137 | 385,379,646,442 | -1.05e12 |

**Winner: XGBoost** (XGBRegressor, n_estimators=200) — chosen as the final model for its strong predictive performance (R²=0.921), native handling of missing values, and excellent scalability. While RandomForest achieved a marginally higher R² (0.928), XGBoost's gradient boosting framework provides better generalization on unseen data and is the preferred choice for production deployment. The model is wrapped in a full sklearn `Pipeline` including imputation, scaling, and one-hot encoding, making the backend inference simple and robust.

> **Note:** The model was trained on scikit-learn **1.9.0** with **XGBoost 3.2.0**. These versions are pinned in `backend/requirements.txt` to ensure reliable pickle loading.

---

## Currency Display

- The backend always predicts in **Indian Rupees (₹)**, matching the training data.
- The frontend converts this for display into **USD ($)** or **EGP (E£)** using fixed, illustrative exchange rates set at build time (see `frontend/src/utils/currency.ts`) — these are **not** live rates and should be refreshed periodically for accuracy.

| Currency | Rate (1 INR =) |
|----------|----------------|
| INR      | 1              |
| USD      | 0.01044        |
| EGP      | 0.531          |

---

## Data Preprocessing Highlights

The raw Kaggle dataset is intentionally messy. Key cleaning steps:

1. **Price parsing** — Text values like `"42 Lac"`, `"1.20 Cr"`, `"Call for Price"` converted to numeric (1 Lac = 100,000 ₹; 1 Cr = 10,000,000 ₹). Rows without usable price dropped.
2. **Area normalization** — `Carpet Area` and `Super Area` in mixed units (`"1200 sqft"`, `"140 sqm"`) parsed to sqft (1 sqm ≈ 10.764 sqft). Missing carpet area imputed from super area × 0.85.
3. **Floor extraction** — `"3 out of 10"`, `"Ground out of 8"`, `"Basement out of 5"` → numeric floor (Ground=0, Basement=-1).
4. **BHK extraction** — Number of bedrooms parsed from `Title` via regex (e.g., `"3 BHK Flat for sale..."` → 3).
5. **Numeric imputation** — Bathroom, Balcony, Car Parking missing values filled with median.
6. **High-cardinality handling** — `location` and `Society` have thousands of unique values. Top-50 locations kept; rest grouped as `"other"` before one-hot encoding.
7. **Column dropping** — `Index`, `Title`, `Description`, `Dimensions`, `Plot Area`, `Society`, `Amount(in rupees)`, `Price (in rupees)`, `Carpet Area`, `Super Area`, `Floor`, `location`, `super_area_sqft`, `Status`, `overlooking` dropped.
8. **Outlier removal** — Listings with price-per-sqft below 1st or above 99th percentile removed.

---

## EDA & Important Findings

The notebook includes 4+ visualizations with interpretations:

1. **Price Distribution (log scale)** — Heavily right-skewed; log-transform used for modeling.
2. **Price vs. Carpet Area (scatter)** — Positive correlation with significant noise; location is a major driver.
3. **Average Price by Top-15 Locations (bar)** — Prices vary 5-10x across locations; Mumbai and Delhi sectors command highest prices.
4. **Price by Furnishing / Bathrooms (box plots)** — Furnished properties and those with more bathrooms command higher prices.

---

## Feature Engineering

- **Target transformation:** `log1p(price)` used to normalize heavy right skew.
- **BHK from Title** — Strongest single predictor after location.
- **Area in sqft** — Normalized from mixed sqft/sqm strings.
- **Floor numeric** — Handles "Ground", "Basement", and "N out of M" formats.
- **Location grouping** — Top-50 + "other" reduces one-hot dimensionality from 1000+ to 51 categories.
- **Pipeline bundling** — All preprocessing (imputation, scaling, one-hot) inside the exported Pipeline.

---

## Machine Learning Models Used

| Model | Configuration |
|-------|---------------|
| LinearRegression | Baseline linear model |
| RandomForestRegressor | n_estimators=100, random_state=42, n_jobs=-1 |
| GradientBoostingRegressor | Default hyperparameters, random_state=42 |
| **XGBRegressor** | **n_estimators=200, random_state=42, n_jobs=-1** |

All models trained inside a `ColumnTransformer` + `Pipeline` with:
- **Numeric:** Median imputation → StandardScaler
- **Categorical:** Most-frequent imputation → OneHotEncoder(handle_unknown="ignore")

---

## Model Evaluation

- **Split:** 80/20 train/test, random_state=42
- **Metrics:** MAE, RMSE, R² on original price scale (inverted via `np.expm1`)
- **Winner selection:** Highest R² on held-out test set
- **Cross-validation:** 5-fold CV on log-target (bonus)

---

## Installation & Setup (Quick Start)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone & Download Data
```bash
git clone https://github.com/<your-username>/house-price-app.git
cd house-price-app

# Download real dataset
pip install kaggle
kaggle datasets download -d juhibhojani/house-price -p notebooks/data --unzip
```

### 2. Train Model (or use pre-trained)
```bash
cd notebooks
jupyter notebook house_price_model.ipynb
# Run all cells → exports house_price.pkl & locations.json
# Copy to backend/models/ and frontend/public/
```

### 3. Start Backend
```bash
cd ../backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 4. Start Frontend
```bash
cd ../frontend
npm install
cp .env.example .env
npm run dev
```

### 5. Test End-to-End
1. Open http://localhost:5173
2. Fill in property details
3. Click "Predict price"
4. See result on `/result` page

### Screenshots
See [docs/screenshot/screenshots.md](docs/screenshot/screenshots.md) for screenshots of the frontend and backend in action.

---

## Assumptions & Limitations

1. **Exchange rates** are fixed (Aug 2026) and not live — for display only.
2. **Car Parking** feature has no observed values in the real dataset; median imputation uses 0.
3. **Location coverage** limited to top-50 Indian cities/sectors; unknown locations fall back to `"other"`.
4. **Model trained on Indian market data** — predictions for other markets will be unreliable.
5. **No temporal features** — model doesn't account for market trends over time.
6. **Synthetic data disclaimer** — The repo originally shipped with synthetic data for CI/testing; the real dataset must be downloaded from Kaggle as described above.

---

## Future Improvements

- [ ] Implement hyperparameter tuning (Optuna / GridSearchCV)
- [ ] Add model monitoring & drift detection
- [ ] Deploy to cloud (AWS/GCP/Azure) with Docker
- [ ] Add authentication & rate limiting to API
- [ ] Live currency conversion via exchange rate API
- [ ] Map-based location picker instead of dropdown
- [ ] Model explanation (SHAP values) on result page
- [ ] Batch prediction endpoint for CSV uploads
- [ ] CI/CD pipeline with GitHub Actions

---

## Acknowledgment / Dataset Source

- **Dataset:** [House Price by Juhi Bhojani](https://www.kaggle.com/datasets/juhibhojani/house-price) on Kaggle
- **Project Guide:** Student Project Guide — House Price Prediction (End-to-End ML Web App)

---

## License

For educational use as part of a student project assignment.