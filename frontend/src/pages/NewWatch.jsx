import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar.jsx";
import { createWatch } from "../api.js";

const initialForm = {
  name: "",
  url: "",
  css_selector: "",
  notify_email: "",
  check_interval_minutes: 60,
};

export default function NewWatch() {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await createWatch({
        name: form.name || null,
        url: form.url,
        css_selector: form.css_selector || null,
        notify_email: form.notify_email,
        check_interval_minutes: Number(form.check_interval_minutes) || 60,
      });
      navigate("/app");
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  }

  return (
    <div>
      <Navbar inApp />
      <main>
        <h2>Add a new watch</h2>

        {error && <div className="alert">{error}</div>}

        <form className="form" onSubmit={handleSubmit}>
          <label>
            Name (optional)
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="e.g. Standing desk"
            />
          </label>

          <label>
            Listing URL
            <input
              type="url"
              name="url"
              required
              value={form.url}
              onChange={handleChange}
              placeholder="https://example.com/product/123"
            />
          </label>

          <label>
            CSS selector for price (optional)
            <input
              type="text"
              name="css_selector"
              value={form.css_selector}
              onChange={handleChange}
              placeholder=".price, #priceblock_ourprice, [itemprop=price]"
            />
            <span className="hint">
              Leave blank to auto-detect common price patterns on the page.
            </span>
          </label>

          <label>
            Notify email
            <input
              type="email"
              name="notify_email"
              required
              value={form.notify_email}
              onChange={handleChange}
              placeholder="you@example.com"
            />
          </label>

          <label>
            Check interval (minutes)
            <input
              type="number"
              name="check_interval_minutes"
              min="5"
              max="10080"
              value={form.check_interval_minutes}
              onChange={handleChange}
            />
          </label>

          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? "Creating…" : "Create watch"}
          </button>
        </form>
      </main>
    </div>
  );
}
