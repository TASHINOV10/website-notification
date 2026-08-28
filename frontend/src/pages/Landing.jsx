import { Link } from "react-router-dom";
import Navbar from "../components/Navbar.jsx";

const FEATURES = [
  {
    title: "Track any listing",
    body: "Paste a product URL and PriceWatch keeps an eye on it — no scripts, no browser extension.",
  },
  {
    title: "Pixel-precise price detection",
    body: "Point it at the exact price element with a CSS selector, or let it auto-detect common price patterns.",
  },
  {
    title: "Your schedule",
    body: "Check every 5 minutes or once a week, per watch. It only re-checks what's actually due.",
  },
  {
    title: "Email the moment it changes",
    body: "No dashboard-refreshing. A price drop (or increase) lands straight in your inbox.",
  },
];

const STEPS = [
  { n: "1", title: "Add a URL", body: "Drop in the listing link and, optionally, a CSS selector for the price." },
  { n: "2", title: "We watch it", body: "A scheduler checks the page on the interval you set and logs every price seen." },
  { n: "3", title: "You get notified", body: "The moment the price changes, an email goes out with the old and new price." },
];

export default function Landing() {
  return (
    <div>
      <Navbar />

      <section className="hero">
        <h1>Know the moment a price drops.</h1>
        <p className="hero-sub">
          PriceWatch watches any product listing on the web and emails you the instant its
          price changes. Self-hosted, open, and built to run on the cheapest box you own.
        </p>
        <div className="hero-actions">
          <Link className="btn btn-primary btn-large" to="/app/new">
            Add your first watch
          </Link>
          <Link className="btn btn-large" to="/app">
            View dashboard
          </Link>
        </div>
      </section>

      <section className="features">
        {FEATURES.map((f) => (
          <div className="feature-card" key={f.title}>
            <h3>{f.title}</h3>
            <p>{f.body}</p>
          </div>
        ))}
      </section>

      <section className="how-it-works">
        <h2>How it works</h2>
        <div className="steps">
          {STEPS.map((s) => (
            <div className="step" key={s.n}>
              <div className="step-number">{s.n}</div>
              <h3>{s.title}</h3>
              <p>{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="site-footer">
        <p>PriceWatch — a small, self-hosted price tracker.</p>
      </footer>
    </div>
  );
}
