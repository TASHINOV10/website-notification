function getApiBase() {
  if (typeof window !== "undefined" && window.__CONFIG__?.API_URL) {
    return window.__CONFIG__.API_URL;
  }
  return import.meta.env.VITE_API_URL || "http://localhost:8000";
}

async function request(path, options = {}) {
  const res = await fetch(`${getApiBase()}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ? JSON.stringify(body.detail) : detail;
    } catch {
      // response wasn't JSON, keep statusText
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const listWatches = () => request("/watches");
export const getWatch = (id) => request(`/watches/${id}`);
export const createWatch = (payload) =>
  request("/watches", { method: "POST", body: JSON.stringify(payload) });
export const checkWatchNow = (id) => request(`/watches/${id}/check`, { method: "POST" });
export const deleteWatch = (id) => request(`/watches/${id}`, { method: "DELETE" });
