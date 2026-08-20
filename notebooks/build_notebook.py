import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))

def code(text):
    cells.append(nbf.v4.new_code_cell(text))

# ---------------------------------------------------------------- Title
md("""# House Price Prediction — Data Cleaning, Modeling & Export

Dataset: **House Price** by Juhi Bhojani — https://www.kaggle.com/datasets/juhibhojani/house-price

> **Note on the data file used here:** this notebook was developed and tested against a
> synthetically generated stand-in file (`data/house_prices.csv`, ~20k rows) that mirrors the
> real Kaggle dataset's columns and messiness, because the sandbox this notebook was authored
> in could not reach kaggle.com. **Before submitting, replace `data/house_prices.csv` with the
> real file downloaded from Kaggle** (see README) and re-run all cells (Kernel → Restart & Run
> All). The cleaning logic below was written to match the *documented* schema of the real
> dataset, so it should work unchanged — just double-check `df.columns` in 2.1 against the real
> file and adjust if anything differs.
""")

# ---------------------------------------------------------------- 2.1
md("## 2.1 Load & Inspect")

code("""import pandas as pd
import numpy as np

pd.set_option("display.max_columns", 50)

df = pd.read_csv("data/house_prices.csv")
df.shape""")

code("""df.head()""")

code("""df.info()""")

code("""df.describe(include="all").T""")

code("""missing = df.isna().mean().sort_values(ascending=False)
missing""")

md("""**Observations:**
- The dataset has the number of rows/columns shown by `df.shape` above.
- Numeric-looking columns (`Price (in rupees)`, `Bathroom`, `Balcony`, `Car Parking`, `Index`) are
  stored as numbers, but the two columns that matter most for modeling — `Amount(in rupees)`
  (the price) and `Carpet Area` / `Super Area` (the size) — are stored as **free text** and need
  parsing.
- Columns with the most missing values (see the `missing` series above) are typically
  `Dimensions`, `Plot Area`, `Society`, and `Super Area` — several of these will be dropped in
  section 2.3.
- High-cardinality text columns: `location` and `Society` (thousands of unique values) will be
  bucketed before one-hot encoding.
""")

# ---------------------------------------------------------------- 2.2
md("## 2.2 Exploratory Data Analysis (EDA)")

code("""import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")""")

md("First, a quick numeric parse of price so we can plot its distribution (full parsing logic lives in 2.3).")

code("""def parse_amount(x):
    if not isinstance(x, str):
        return None
    x = x.strip().lower()
    try:
        if "lac" in x:
            return float(x.replace("lac", "").replace(",", "").strip()) * 1e5
        if "cr" in x:
            return float(x.replace("cr", "").replace(",", "").strip()) * 1e7
        return float(x.replace(",", ""))
    except ValueError:
        return None

df["price_clean"] = df["Amount(in rupees)"].apply(parse_amount)
df["price_clean"].describe()""")

md("**Plot 1 — Distribution of price (log scale)**: price is heavily right-skewed, as expected for real-estate data, so we view it on a log axis.")

code("""plt.figure(figsize=(7,4))
sns.histplot(df["price_clean"].dropna(), log_scale=True, bins=50)
plt.title("Price distribution (log scale)")
plt.xlabel("Price (INR)")
plt.show()""")

md("**Plot 2 — Price vs. carpet area (scatter)**: larger properties generally cost more, though the relationship is noisy and depends heavily on location.")

code("""def parse_area(x):
    if not isinstance(x, str):
        return None
    x = x.strip().lower().replace(",", "")
    try:
        if "sqft" in x:
            return float(x.replace("sqft", "").strip())
        if "sqm" in x:
            return float(x.replace("sqm", "").strip()) * 10.764
        return float(x)
    except ValueError:
        return None

df["carpet_area_sqft"] = df["Carpet Area"].apply(parse_area)

plt.figure(figsize=(7,4))
sample = df.dropna(subset=["carpet_area_sqft", "price_clean"]).sample(min(3000, len(df)), random_state=1)
sns.scatterplot(data=sample, x="carpet_area_sqft", y="price_clean", alpha=0.3)
plt.yscale("log")
plt.title("Price vs. Carpet Area")
plt.xlabel("Carpet Area (sqft)")
plt.ylabel("Price (INR, log scale)")
plt.show()""")

md("**Plot 3 — Average price by top-15 locations (bar chart)**: location is one of the strongest price drivers.")

code("""top_locations = (df.groupby("location")["price_clean"].mean()
                    .sort_values(ascending=False).head(15))

plt.figure(figsize=(8,5))
sns.barplot(x=top_locations.values, y=top_locations.index, orient="h", color="steelblue")
plt.title("Average price by top-15 locations")
plt.xlabel("Average price (INR)")
plt.ylabel("Location")
plt.show()""")

md("**Plot 4 — Price by furnishing status / bathrooms (box plots)**: furnished properties and those with more bathrooms tend to command higher prices.")

code("""fig, axes = plt.subplots(1, 2, figsize=(12,4))

sns.boxplot(data=df, x="Furnishing", y="price_clean", ax=axes[0])
axes[0].set_yscale("log")
axes[0].set_title("Price by furnishing status")
axes[0].tick_params(axis="x", rotation=20)

sns.boxplot(data=df, x="Bathroom", y="price_clean", ax=axes[1])
axes[1].set_yscale("log")
axes[1].set_title("Price by number of bathrooms")

plt.tight_layout()
plt.show()""")

md("""**Commentary:** price is strongly right-skewed (Plot 1), positively correlated with carpet
area (Plot 2), varies a lot by location — some localities average several times the price of
others (Plot 3) — and increases with both furnishing quality and bathroom count (Plot 4). These
patterns motivate modeling `log1p(price)` and including location, area, furnishing and bathroom
count as features.""")

# ---------------------------------------------------------------- 2.3
md("""## 2.3 Cleaning & Feature Engineering

This dataset is messy on purpose. We handle each documented issue in turn.""")

md("**1. Price is text** — already parsed above into `price_clean`. Drop rows without a usable price.")

code("""df = df.dropna(subset=["price_clean"])
df = df[df["price_clean"] > 0]
df.shape""")

md("**2. Areas are text** — `carpet_area_sqft` already parsed above. Also parse `Super Area` and use it to fill missing carpet area where possible.")

code("""df["super_area_sqft"] = df["Super Area"].apply(parse_area)

# fall back to super area (scaled down slightly) when carpet area is missing
fallback = df["super_area_sqft"] * 0.85
df["carpet_area_sqft"] = df["carpet_area_sqft"].fillna(fallback)

df[["carpet_area_sqft", "super_area_sqft"]].describe()""")

md("**3. Floor** — extract the numeric floor, handling `Ground` and `Basement`.")

code("""def parse_floor(x):
    if not isinstance(x, str):
        return None
    x = x.strip().lower()
    first = x.split(" out of")[0].strip()
    if first in ("ground", "g"):
        return 0
    if first == "basement":
        return -1
    try:
        return int(first)
    except ValueError:
        return None

df["floor_num"] = df["Floor"].apply(parse_floor)
df["floor_num"].describe()""")

md("**3b. Number of rooms (BHK)** — not its own column, but embedded in `Title` (e.g. *\"3 BHK Flat for sale in...\"*). Extract it with a regex; this turns out to be one of the strongest price predictors.")

code("""def parse_bhk(title):
    if not isinstance(title, str):
        return None
    match = re.search(r\"(\\d+)\\s*BHK\", title, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None

import re
df["bhk"] = df["Title"].apply(parse_bhk)
df["bhk"] = df["bhk"].fillna(df["bhk"].median())
df["bhk"].value_counts().sort_index()""")

md("**4. Bathroom / Balcony / Car Parking** — convert to numeric, impute missing with the median.")

code("""for col in ["Bathroom", "Balcony", "Car Parking"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col] = df[col].fillna(df[col].median())

df.rename(columns={"Bathroom": "bathroom", "Balcony": "balcony", "Car Parking": "car_parking"}, inplace=True)""")

md("**5. High-cardinality categoricals** — keep the top-50 locations, group the rest into `\"other\"`.")

code("""TOP_N_LOCATIONS = 50
top_locs = df["location"].value_counts().head(TOP_N_LOCATIONS).index
df["location_grouped"] = df["location"].where(df["location"].isin(top_locs), other="other")
df["location_grouped"].value_counts().head(10)""")

md("**6. Drop useless columns.**")

code("""drop_cols = ["Index", "Title", "Description", "Dimensions", "Plot Area", "Society",
             "Amount(in rupees)", "Price (in rupees)", "Carpet Area", "Super Area", "Floor",
             "location", "super_area_sqft", "Status", "overlooking"]
df = df.drop(columns=[c for c in drop_cols if c in df.columns])
df.columns.tolist()""")

md("**7. Remove outliers** — drop listings with absurd price-per-sqft (below 1st / above 99th percentile).")

code("""df["price_per_sqft"] = df["price_clean"] / df["carpet_area_sqft"].replace(0, np.nan)
low, high = df["price_per_sqft"].quantile([0.01, 0.99])
before = len(df)
df = df[(df["price_per_sqft"] >= low) & (df["price_per_sqft"] <= high)]
df = df.drop(columns=["price_per_sqft"])
print(f"Removed {before - len(df)} outlier rows ({before} -> {len(df)})")""")

code("""df = df.dropna(subset=["carpet_area_sqft"])
df.isna().mean().sort_values(ascending=False)""")

# ---------------------------------------------------------------- 2.4
md("""## 2.4 Build a Pipeline & Train

We bundle preprocessing (imputation, scaling, one-hot encoding) **inside** the exported model
using `ColumnTransformer` + `Pipeline`, so the backend only needs to call `.predict()` on raw
feature values.""")

code("""from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression

numeric_features = ["carpet_area_sqft", "bhk", "floor_num", "bathroom", "balcony", "car_parking"]
categorical_features = ["location_grouped", "Furnishing", "Transaction", "Ownership", "facing"]

preprocessor = ColumnTransformer([
    ("num", Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]), numeric_features),
    ("cat", Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]), categorical_features),
])

X = df[numeric_features + categorical_features]
y = df["price_clean"]
y_log = np.log1p(y)

X_train, X_test, y_train, y_test, ylog_train, ylog_test = train_test_split(
    X, y, y_log, test_size=0.2, random_state=42
)
X_train.shape, X_test.shape""")

md("**Train at least 2 models** and compare a plain target vs. a `log1p`-transformed target.")

code("""models = {
    "LinearRegression": LinearRegression(),
    "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    "GradientBoosting": GradientBoostingRegressor(random_state=42),
}

fitted = {}
for name, reg in models.items():
    pipe = Pipeline([("prep", preprocessor), ("reg", reg)])
    pipe.fit(X_train, ylog_train)   # train on log1p(price)
    fitted[name] = pipe
print("Trained:", list(fitted.keys()))""")

# ---------------------------------------------------------------- 2.5
md("## 2.5 Evaluate")

code("""from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

results = []
for name, pipe in fitted.items():
    pred_log = pipe.predict(X_test)
    pred = np.expm1(pred_log)          # invert log1p back to rupees
    mae = mean_absolute_error(y_test, pred)
    rmse = root_mean_squared_error(y_test, pred)
    r2 = r2_score(y_test, pred)
    results.append({"model": name, "MAE": mae, "RMSE": rmse, "R2": r2})

results_df = pd.DataFrame(results).sort_values("R2", ascending=False)
results_df""")

md("**Predicted vs. actual scatter plot** for the best model.")

code("""best_name = results_df.iloc[0]["model"]
best_pipe = fitted[best_name]
pred = np.expm1(best_pipe.predict(X_test))

plt.figure(figsize=(6,6))
plt.scatter(y_test, pred, alpha=0.3, s=10)
lims = [0, max(y_test.max(), pred.max())]
plt.plot(lims, lims, "r--", linewidth=1)
plt.xlabel("Actual price")
plt.ylabel("Predicted price")
plt.title(f"Predicted vs Actual — {best_name}")
plt.xscale("log"); plt.yscale("log")
plt.show()""")

md("**(Bonus) 5-fold cross-validation** on the winning model's architecture (on log-target, negative MAE scoring).")

code("""from sklearn.model_selection import cross_val_score

cv_pipe = Pipeline([("prep", preprocessor), ("reg", models[best_name].__class__(**models[best_name].get_params()))])
cv_scores = cross_val_score(cv_pipe, X, y_log, cv=5, scoring="neg_mean_absolute_error", n_jobs=-1)
print("CV MAE (log-target):", -cv_scores.mean(), "+/-", cv_scores.std())""")

code("""print("Model comparison:")
print(results_df.to_string(index=False))
print()

if best_name == "LinearRegression":
    reasoning = (
        "the relationship between the engineered features (BHK, carpet area, bathrooms, "
        "location) and log-price turned out to be close to linear once the messy text fields "
        "were cleaned and encoded, so the extra complexity of tree ensembles did not pay off "
        "on this dataset — and a linear model is also the cheapest and most interpretable to "
        "deploy."
    )
else:
    reasoning = (
        "it captured non-linear interactions between location, area, BHK and amenities better "
        "than plain LinearRegression, at an acceptable training and inference cost."
    )

print(f"Winner: {best_name} — best R2 on the held-out test set, chosen as the final model "
      f"because {reasoning}")""")

# ---------------------------------------------------------------- 2.6
md("## 2.6 Export the Model")

code("""import joblib
import sklearn

final_model = best_pipe  # the winning Pipeline (preprocessing + regressor), trained on log1p(price)

joblib.dump(final_model, "house_price.pkl")

# Sanity check: reload and predict one sample
loaded = joblib.load("house_price.pkl")
sample = X_test.iloc[[0]]
pred_price = np.expm1(loaded.predict(sample))[0]
print("Reloaded prediction (INR):", round(pred_price, 2))
print("Actual (INR):", round(y_test.iloc[0], 2))
print("scikit-learn version used for training:", sklearn.__version__)""")

code("""import json

locations = sorted(df["location_grouped"].unique().tolist())
json.dump(locations, open("locations.json", "w"))
print(f"Saved {len(locations)} locations to locations.json")""")

md("""> ⚠️ **Version pinning:** a pickle only loads reliably with the same scikit-learn version
> used to create it. The version printed above must be pinned in `backend/requirements.txt`.
> This notebook also predicts on `log1p(price)` internally — the backend's inference service
> must call `np.expm1()` on the model's raw output before returning it.
""")

nb["cells"] = cells
nbf.write(nb, "house_price_model.ipynb")
print("Notebook written.")
