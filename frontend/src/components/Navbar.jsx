import { Link } from "react-router-dom";

export default function Navbar({ inApp = false }) {
  return (
    <header className="topbar">
      <Link to="/" className="brand">
        PriceWatch
      </Link>
      {inApp ? (
        <Link className="btn btn-primary" to="/app/new">
          + Add watch
        </Link>
      ) : (
        <Link className="btn btn-primary" to="/app">
          Open dashboard
        </Link>
      )}
    </header>
  );
}
