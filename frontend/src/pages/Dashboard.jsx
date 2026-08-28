import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar.jsx";
import StatusDot from "../components/StatusDot.jsx";
import { listWatches, checkWatchNow, deleteWatch } from "../api.js";

export default function Dashboard() {
  const [watches, setWatches] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [checkingId, setCheckingId] = useState(null);

  async function refresh() {
    try {
      setWatches(await listWatches());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleCheck(id) {
    setCheckingId(id);
    try {
      await checkWatchNow(id);
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setCheckingId(null);
    }
  }

  async function handleDelete(id) {
    if (!confirm("Delete this watch?")) return;
    try {
      await deleteWatch(id);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <Navbar inApp />
      <main>
        {error && <div className="alert">{error}</div>}

        {!loading && watches.length === 0 && !error && (
          <p className="empty">
            No watches yet. <Link to="/app/new">Add your first one</Link>.
          </p>
        )}

        {watches.length > 0 && (
          <table className="watch-table">
            <thead>
              <tr>
                <th></th>
                <th>Name / URL</th>
                <th>Price</th>
                <th>Interval</th>
                <th>Last checked</th>
                <th></th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {watches.map((w) => (
                <tr key={w.id}>
                  <td>
                    <StatusDot watch={w} />
                  </td>
                  <td>
                    <Link to={`/app/watches/${w.id}`}>{w.name || w.url}</Link>
                    <div className="muted small">{w.url}</div>
                  </td>
                  <td>{w.last_price != null ? w.last_price : "—"}</td>
                  <td>{w.check_interval_minutes} min</td>
                  <td className="small">
                    {w.last_checked_at ? new Date(w.last_checked_at).toLocaleString() : "never"}
                  </td>
                  <td>
                    <button
                      className="btn btn-small"
                      onClick={() => handleCheck(w.id)}
                      disabled={checkingId === w.id}
                    >
                      {checkingId === w.id ? "Checking…" : "Check now"}
                    </button>
                  </td>
                  <td>
                    <button className="btn btn-small btn-danger" onClick={() => handleDelete(w.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </main>
    </div>
  );
}
