import { useEffect, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { fetchLocations, predictPrice, ApiError } from "../api/predictionClient";
import type { PredictionRequest } from "../types/prediction";
import { CURRENCIES, type CurrencyCode } from "../utils/currency";

const FURNISHING_OPTIONS = ["Furnished", "Semi-Furnished", "Unfurnished"] as const;
const TRANSACTION_OPTIONS = ["New Property", "Resale"] as const;
const OWNERSHIP_OPTIONS = ["Freehold", "Leasehold", "Co-operative Society", "Power Of Attorney"];
const FACING_OPTIONS = ["East", "West", "North", "South", "North-East", "South-West"];
const BHK_OPTIONS = [1, 2, 3, 4, 5];

const initialForm: PredictionRequest = {
  location: "",
  bhk: 2,
  carpet_area_sqft: 90,
  floor_num: 1,
  bathroom: 2,
  balcony: 1,
  car_parking: 1,
  furnishing: "Semi-Furnished",
  transaction: "Resale",
  ownership: "Freehold",
  facing: "East",
};

export default function PredictionForm() {
  const navigate = useNavigate();
  const [locations, setLocations] = useState<string[]>([]);
  const [form, setForm] = useState<PredictionRequest>(initialForm);
  const [currency, setCurrency] = useState<CurrencyCode>("INR");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    fetchLocations().then(setLocations);
  }, []);

  function updateField<K extends keyof PredictionRequest>(key: K, value: PredictionRequest[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function validate(): boolean {
    const next: Record<string, string> = {};
    if (!form.location.trim()) next.location = "Please select a location.";
    if (!form.carpet_area_sqft || form.carpet_area_sqft <= 0)
      next.carpet_area_sqft = "Carpet area must be greater than 0.";
    if (form.floor_num < -1) next.floor_num = "Floor looks invalid.";
    if (form.bathroom < 0) next.bathroom = "Bathrooms can't be negative.";
    if (form.balcony < 0) next.balcony = "Balconies can't be negative.";
    if (form.car_parking < 0) next.car_parking = "Car parking can't be negative.";
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setApiError(null);
    if (!validate()) return;

    setLoading(true);
    try {
      // The form stores area in sqm; the model was trained on sqft.
      const payload = { ...form, carpet_area_sqft: form.carpet_area_sqft * 10.764 };
      const result = await predictPrice(payload);
      navigate("/result", {
        state: { predictedPrice: result.predicted_price, form, currency },
      });
    } catch (err) {
      setApiError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="prediction-form">
      <div className="field">
        <label htmlFor="currency">Display currency</label>
        <div className="currency-toggle" role="group" aria-label="Display currency">
          {(Object.values(CURRENCIES)).map((c) => (
            <button
              type="button"
              key={c.code}
              className={c.code === currency ? "currency-pill currency-pill--active" : "currency-pill"}
              onClick={() => setCurrency(c.code)}
            >
              {c.symbol} {c.code}
            </button>
          ))}
        </div>
      </div>

      <div className="field">
        <label htmlFor="location">Location</label>
        <select
          id="location"
          value={form.location}
          onChange={(e) => updateField("location", e.target.value)}
        >
          <option value="">Select a location…</option>
          {locations.map((loc) => (
            <option key={loc} value={loc}>
              {loc}
            </option>
          ))}
        </select>
        {errors.location && <p className="error">{errors.location}</p>}
      </div>

      <div className="grid-2">
        <div className="field">
          <label htmlFor="bhk">BHK (bedrooms)</label>
          <select
            id="bhk"
            value={form.bhk}
            onChange={(e) => updateField("bhk", Number(e.target.value))}
          >
            {BHK_OPTIONS.map((n) => (
              <option key={n} value={n}>
                {n} BHK
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="carpet_area_sqft">Carpet area (sqm)</label>
          <input
            id="carpet_area_sqft"
            type="number"
            min={1}
            value={form.carpet_area_sqft}
            onChange={(e) => updateField("carpet_area_sqft", Number(e.target.value))}
          />
          {errors.carpet_area_sqft && <p className="error">{errors.carpet_area_sqft}</p>}
        </div>
      </div>

      <div className="grid-2">
        <div className="field">
          <label htmlFor="floor_num">Floor</label>
          <input
            id="floor_num"
            type="number"
            value={form.floor_num}
            onChange={(e) => updateField("floor_num", Number(e.target.value))}
          />
          {errors.floor_num && <p className="error">{errors.floor_num}</p>}
        </div>

        <div className="field">
          <label htmlFor="bathroom">Bathrooms</label>
          <input
            id="bathroom"
            type="number"
            min={0}
            value={form.bathroom}
            onChange={(e) => updateField("bathroom", Number(e.target.value))}
          />
          {errors.bathroom && <p className="error">{errors.bathroom}</p>}
        </div>

        <div className="field">
          <label htmlFor="balcony">Balconies</label>
          <input
            id="balcony"
            type="number"
            min={0}
            value={form.balcony}
            onChange={(e) => updateField("balcony", Number(e.target.value))}
          />
          {errors.balcony && <p className="error">{errors.balcony}</p>}
        </div>

        <div className="field">
          <label htmlFor="car_parking">Car parking</label>
          <input
            id="car_parking"
            type="number"
            min={0}
            value={form.car_parking}
            onChange={(e) => updateField("car_parking", Number(e.target.value))}
          />
          {errors.car_parking && <p className="error">{errors.car_parking}</p>}
        </div>
      </div>

      <div className="grid-2">
        <div className="field">
          <label htmlFor="furnishing">Furnishing</label>
          <select
            id="furnishing"
            value={form.furnishing}
            onChange={(e) =>
              updateField("furnishing", e.target.value as PredictionRequest["furnishing"])
            }
          >
            {FURNISHING_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="transaction">Transaction</label>
          <select
            id="transaction"
            value={form.transaction}
            onChange={(e) =>
              updateField("transaction", e.target.value as PredictionRequest["transaction"])
            }
          >
            {TRANSACTION_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="ownership">Ownership</label>
          <select
            id="ownership"
            value={form.ownership}
            onChange={(e) => updateField("ownership", e.target.value)}
          >
            {OWNERSHIP_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="facing">Facing</label>
          <select
            id="facing"
            value={form.facing}
            onChange={(e) => updateField("facing", e.target.value)}
          >
            {FACING_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </div>
      </div>

      {apiError && <p className="error api-error">{apiError}</p>}

      <button type="submit" className="submit-btn" disabled={loading}>
        {loading ? "Predicting…" : "Predict price"}
      </button>
    </form>
  );
}
