import { Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import NewWatch from "./pages/NewWatch.jsx";
import WatchDetail from "./pages/WatchDetail.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/app" element={<Dashboard />} />
      <Route path="/app/new" element={<NewWatch />} />
      <Route path="/app/watches/:id" element={<WatchDetail />} />
    </Routes>
  );
}
