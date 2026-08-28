export default function StatusDot({ watch }) {
  const cls = watch.last_error ? "dot-error" : watch.is_active ? "dot-ok" : "dot-paused";
  const title = watch.last_error ? `Error: ${watch.last_error}` : watch.is_active ? "Active" : "Paused";
  return <span className={`dot ${cls}`} title={title} />;
}
