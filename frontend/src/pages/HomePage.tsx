import BlueprintIllustration from "../components/BlueprintIllustration";
import PredictionForm from "../components/PredictionForm";
import { IconBolt, IconCoin, IconLayers, IconRuler } from "../components/icons";

export default function HomePage() {
  return (
    <>
      <div className="shell">
        <section className="hero-panel">
          <div className="hero-inner">
            <div className="hero-text">
              <span className="eyebrow">Property valuation model</span>
              <h1 className="hero-title">
                Know what a home
                <br />
                is worth <em>before</em> you sign.
              </h1>
              <p className="hero-copy">
                Enter a few details about a property — BHK, carpet area, location, amenities —
                and get an instant estimate from a model trained on real listing data. No agent,
                no guesswork.
              </p>

              <div className="stat-row">
                <div className="stat-chip">
                  <span className="stat-number">6,000+</span>
                  <span className="stat-label">listings analyzed</span>
                </div>
                <div className="stat-chip">
                  <span className="stat-number">10</span>
                  <span className="stat-label">cities covered</span>
                </div>
                <div className="stat-chip">
                  <span className="stat-number">&lt;1s</span>
                  <span className="stat-label">to estimate</span>
                </div>
              </div>
            </div>

            <BlueprintIllustration />
          </div>
        </section>

        <section className="form-panel">
          <div className="form-card">
            <span className="eyebrow eyebrow--card">Get an estimate</span>
            <h2 className="form-title">Property details</h2>
            <PredictionForm />
          </div>
        </section>
      </div>

      <section className="features-strip">
        <div className="features-inner">
          <div className="feature">
            <IconLayers className="feature-icon" />
            <h3>Trained on real listings</h3>
            <p>
              The model learns from thousands of cleaned property records — price, area,
              furnishing, location, and more.
            </p>
          </div>
          <div className="feature">
            <IconBolt className="feature-icon" />
            <h3>Instant, transparent estimate</h3>
            <p>
              Predictions come straight from a served machine-learning pipeline, returned in
              well under a second.
            </p>
          </div>
          <div className="feature">
            <IconRuler className="feature-icon" />
            <h3>Built on what matters</h3>
            <p>
              BHK, carpet area, floor, furnishing and location — the same factors a buyer would
              actually weigh.
            </p>
          </div>
          <div className="feature">
            <IconCoin className="feature-icon" />
            <h3>Multi-currency</h3>
            <p>View your estimate in Indian Rupees, US Dollars, or Egyptian Pounds.</p>
          </div>
        </div>
      </section>
    </>
  );
}
