import { useState } from "react";
import { Link, useLocation, Navigate } from "react-router-dom";
import type { PredictionRequest } from "../types/prediction";
import { CURRENCIES, formatPrice, type CurrencyCode } from "../utils/currency";
import BlueprintIllustration from "../components/BlueprintIllustration";

interface LocationState {
  predictedPrice: number; // always in INR, from the backend
  form: PredictionRequest;
  currency: CurrencyCode;
}

/** Very rough illustrative EMI estimate: 20yr loan, ~9% annual rate, 80% financed. */
function estimateMonthlyEmi(priceInr: number): number {
  const principal = priceInr * 0.8;
  const monthlyRate = 0.09 / 12;
  const months = 20 * 12;
  const factor = Math.pow(1 + monthlyRate, months);
  return (principal * monthlyRate * factor) / (factor - 1);
}

export default function ResultPage() {
  const location = useLocation();
  const state = location.state as LocationState | null;
  const [currency, setCurrency] = useState<CurrencyCode>(state?.currency ?? "INR");

  if (!state) {
    // Direct navigation without a prediction — send the user back to the form.
    return <Navigate to="/" replace />;
  }

  const { predictedPrice, form } = state;
  const pricePerSqft = predictedPrice / form.carpet_area_sqft;
  const monthlyEmi = estimateMonthlyEmi(predictedPrice);

  return (
    <div className="shell shell--result">
      <section className="hero-panel">
        <div className="hero-inner">
          <span className="eyebrow">Estimate ready</span>
          <h1 className="hero-title">
            Here's what
            <br />
            it's likely <em>worth.</em>
          </h1>
          <p className="hero-copy">
            Based on {form.bhk} BHK, {form.carpet_area_sqft} sqm in {form.location || "the selected area"},
            with {form.bathroom} bathroom(s) and {form.furnishing.toLowerCase()} furnishing.
          </p>
          <BlueprintIllustration />
        </div>
      </section>

      <section className="form-panel">
        <div className="form-card result-card">
          <span className="eyebrow eyebrow--card">Predicted price</span>

          <div className="currency-toggle" role="group" aria-label="Display currency">
            {Object.values(CURRENCIES).map((c) => (
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

          <span className="result-price">{formatPrice(predictedPrice, currency)}</span>
          <p className="result-note">
            Rates are approximate, illustrative conversions from INR (Aug 2026) — not live
            exchange rates.
          </p>

          <div className="breakdown">
            <div className="breakdown-row">
              <span>Price per sqm</span>
              <strong>{formatPrice(pricePerSqft, currency)}</strong>
            </div>
            <div className="breakdown-row">
              <span>Est. monthly EMI*</span>
              <strong>{formatPrice(monthlyEmi, currency)}</strong>
            </div>
            <p className="breakdown-footnote">
              *Illustrative only — 20-year loan, ~9% annual rate, 80% financed.
            </p>
          </div>

          <Link to="/" className="back-link">
            ← Try another property
          </Link>
        </div>
      </section>
    </div>
  );
}
