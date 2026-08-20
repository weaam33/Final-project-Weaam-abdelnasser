"""
Generates a SYNTHETIC stand-in for the Kaggle 'House Price' dataset
(https://www.kaggle.com/datasets/juhibhojani/house-price).

This exists ONLY because the real dataset could not be downloaded in this
environment (no network access to kaggle.com). It replicates the same
column names and the same "messiness" (text prices, mixed-unit areas,
missing values, high-cardinality categoricals) described in the project
guide, so the notebook can be built and tested end-to-end.

>>> Replace notebooks/data/house_prices.csv with the REAL Kaggle file
>>> before you submit. Column names must match; if the real file differs,
>>> adjust Section 2.1 of the notebook accordingly.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 6000  # smaller than the real ~187k rows, enough to prototype the pipeline

cities = ["Mumbai", "Delhi", "Bangalore", "Pune", "Hyderabad", "Chennai",
          "Kolkata", "Ahmedabad", "Noida", "Gurgaon"]
localities = [f"{c} Sector {i}" for c in cities for i in range(1, 12)]

furnishing_opts = ["Furnished", "Semi-Furnished", "Unfurnished"]
transaction_opts = ["New Property", "Resale"]
ownership_opts = ["Freehold", "Leasehold", "Co-operative Society", "Power Of Attorney"]
facing_opts = ["East", "West", "North", "South", "North-East", "South-West", np.nan]
overlooking_opts = ["Garden/Park", "Main Road", "Pool", "Not Available", np.nan]
status_opts = ["Ready to Move", "Under Construction"]

def make_area_string(sqft):
    """Return area as messy text: sqft or sqm, sometimes with commas."""
    if rng.random() < 0.7:
        return f"{sqft:,.0f} sqft"
    else:
        sqm = sqft / 10.764
        return f"{sqm:,.0f} sqm"

def make_floor_string():
    total = rng.integers(1, 25)
    if rng.random() < 0.05:
        return "Ground out of " + str(total)
    if rng.random() < 0.03:
        return "Basement out of " + str(total)
    floor = rng.integers(0, total + 1)
    return f"{floor} out of {total}"

def make_price_string(price_rupees):
    if rng.random() < 0.02:
        return "Call for Price"
    if price_rupees >= 1e7:
        return f"{price_rupees/1e7:.2f} Cr"
    else:
        return f"{price_rupees/1e5:.1f} Lac"

rows = []
for i in range(N):
    locality = localities[rng.integers(0, len(localities))]
    city = locality.split(" Sector")[0]
    bhk = rng.integers(1, 6)  # number of bedrooms (1 to 5 BHK)
    carpet_sqft = 350 * bhk + rng.normal(150, 250)
    carpet_sqft = max(200, carpet_sqft)
    super_sqft = carpet_sqft * rng.uniform(1.05, 1.3)
    bathroom = max(1, bhk - rng.integers(0, 2))
    balcony = rng.integers(0, 4)
    car_parking = rng.integers(0, 3)
    furnishing = furnishing_opts[rng.integers(0, len(furnishing_opts))]
    transaction = transaction_opts[rng.integers(0, len(transaction_opts))]
    ownership = ownership_opts[rng.integers(0, len(ownership_opts))]
    facing = facing_opts[rng.integers(0, len(facing_opts))]
    overlooking = overlooking_opts[rng.integers(0, len(overlooking_opts))]
    status = status_opts[rng.integers(0, len(status_opts))]
    society = f"{locality.split()[0]} {'ABCDE'[rng.integers(0,5)]} Society {rng.integers(1,300)}"

    # price roughly driven by area, city tier, bathrooms, furnishing
    city_multiplier = {
        "Mumbai": 22000, "Delhi": 16000, "Bangalore": 14000, "Gurgaon": 15000,
        "Pune": 10000, "Hyderabad": 9000, "Chennai": 9500, "Noida": 9000,
        "Kolkata": 7000, "Ahmedabad": 6500,
    }[city]
    base = carpet_sqft * city_multiplier
    base *= (1 + 0.08 * bhk)
    base *= (1 + 0.05 * bathroom)
    base *= 1.1 if furnishing == "Furnished" else (1.0 if furnishing == "Semi-Furnished" else 0.92)
    noise = rng.normal(1, 0.15)
    price = max(300000, base * noise)

    row = {
        "Index": i,
        "Title": f"{bhk} BHK Flat for sale in {locality}",
        "Description": f"Spacious {bhk} BHK, {status}, located in {locality}.",
        "Amount(in rupees)": make_price_string(price),
        "Price (in rupees)": round(price, -3),  # sometimes present as numeric too
        "location": locality,
        "Carpet Area": make_area_string(carpet_sqft) if rng.random() > 0.08 else np.nan,
        "Status": status,
        "Floor": make_floor_string(),
        "Transaction": transaction,
        "Furnishing": furnishing if rng.random() > 0.05 else np.nan,
        "facing": facing,
        "overlooking": overlooking,
        "Society": society if rng.random() > 0.3 else np.nan,
        "Bathroom": bathroom if rng.random() > 0.03 else np.nan,
        "Balcony": balcony if rng.random() > 0.1 else np.nan,
        "Car Parking": car_parking if rng.random() > 0.4 else np.nan,
        "Ownership": ownership if rng.random() > 0.2 else np.nan,
        "Super Area": make_area_string(super_sqft) if rng.random() > 0.4 else np.nan,
        "Dimensions": np.nan,
        "Plot Area": np.nan,
    }
    rows.append(row)

df = pd.DataFrame(rows)

# sprinkle a few pure-garbage rows to mimic real-world mess
garbage_idx = rng.choice(N, size=int(N * 0.01), replace=False)
df.loc[garbage_idx, "Amount(in rupees)"] = "Call for Price"

out_path = "house_prices.csv"
df.to_csv(out_path, index=False)
print(f"Wrote {len(df)} rows to {out_path}")
