import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const app = express();
const PORT = process.env.PORT || 3000;
const PUBLIC_API_URL = process.env.PUBLIC_API_URL || "http://localhost:8000";

app.get("/config.js", (req, res) => {
  res.type("application/javascript");
  res.send(`window.__CONFIG__ = ${JSON.stringify({ API_URL: PUBLIC_API_URL })};`);
});

app.use(express.static(path.join(__dirname, "dist")));

// SPA fallback: any non-file route serves index.html so client-side routing works.
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "dist", "index.html"));
});

app.listen(PORT, () => {
  console.log(`PriceWatch frontend listening on port ${PORT}, API_URL=${PUBLIC_API_URL}`);
});
