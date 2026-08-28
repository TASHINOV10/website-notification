import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "../components/Navbar.jsx";
import { getWatch, checkWatchNow, deleteWatch } from "../api.js";

export default function WatchDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [watch, setWatch] = useState(null);
  const [error, setError] = useState(null);
  const [checking, setChecking] = useState(false);

  async function refresh() {
    try {
      setWatch(await getWatch(id));
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function handleCheck() {
    setChecking(true);
    try {
      await checkWatchNow(id);
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setChecking(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Delete this watch?")) return;
    try {
      await deleteWatch(id);
      navigate("/app");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <Navbar inApp />
      <main>
        {error && <div className="alert">{error}</div>}

        {watch && (
          <>
            <h2>{watch.name || watch.url}</h2>
            <p className="muted">
              <a href={watch.url} target="_blank" rel="noopener noreferrer">
                {watch.url}
              </a>
            </p>

            <div className="details">
              <div>
                <strong>Current price:</strong> {watch.last_price != null ? watch.last_price : "—"}
              </div>
              <div>
                <strong>Notify:</strong> {watch.notify_email}
              </div>
              <div>
                <strong>Interval:</strong> every {watch.check_interval_minutes} min
              </div>
              <div>
                <strong>Last checked:</strong>{" "}
                {watch.last_checked_at ? new Date(watch.last_checked_at).toLocaleString() : "never"}
              </div>
              {watch.last_error && (
                <div className="error-text">
                  <strong>Last error:</strong> {watch.last_error}
                </div>
              )}
            </div>

            <div className="actions">
              <button className="btn btn-primary" onClick={handleCheck} disabled={checking}>
                {checking ? "Checking…" : "Check now"}
              </button>
              <button className="btn btn-danger" onClick={handleDelete}>
                Delete
              </button>
            </div>

            <h3>Price history</h3>
            {watch.price_history.length === 0 ? (
              <p className="empty">No history yet.</p>
            ) : (
              <table className="watch-table">
                <thead>
                  <tr>
                    <th>Price</th>
                    <th>Checked at</th>
                  </tr>
                </thead>
                <tbody>
                  {[...watch.price_history].reverse().map((p) => (
                    <tr key={p.id}>
                      <td>{p.price}</td>
                      <td>{new Date(p.checked_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}
      </main>
    </div>
  );
}
