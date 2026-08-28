const express = require("express");
const router = express.Router();

const API_BASE = process.env.BACKEND_URL || "http://localhost:8000";

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Backend error ${res.status}: ${detail}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

router.get("/", async (req, res) => {
  try {
    const watches = await api("/watches");
    res.render("index", { watches, error: null });
  } catch (err) {
    res.render("index", { watches: [], error: err.message });
  }
});

router.get("/new", (req, res) => {
  res.render("new", { error: null, formValues: {} });
});

router.post("/watches", async (req, res) => {
  const { name, url, css_selector, notify_email, check_interval_minutes } = req.body;
  try {
    await api("/watches", {
      method: "POST",
      body: JSON.stringify({
        name: name || null,
        url,
        css_selector: css_selector || null,
        notify_email,
        check_interval_minutes: Number(check_interval_minutes) || 60,
      }),
    });
    res.redirect("/");
  } catch (err) {
    res.render("new", { error: err.message, formValues: req.body });
  }
});

router.get("/watches/:id", async (req, res) => {
  try {
    const watch = await api(`/watches/${req.params.id}`);
    res.render("watch", { watch, error: null });
  } catch (err) {
    res.render("watch", { watch: null, error: err.message });
  }
});

router.post("/watches/:id/check", async (req, res) => {
  try {
    await api(`/watches/${req.params.id}/check`, { method: "POST" });
  } catch (err) {
    // fall through, still redirect back so the error surfaces from a fresh GET if it persists
  }
  res.redirect(`/watches/${req.params.id}`);
});

router.post("/watches/:id/delete", async (req, res) => {
  try {
    await api(`/watches/${req.params.id}`, { method: "DELETE" });
  } catch (err) {
    // ignore, redirect back to list either way
  }
  res.redirect("/");
});

module.exports = router;
