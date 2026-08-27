import { useCallback, useEffect, useState } from "react";
import { Download, FileText, RefreshCw } from "lucide-react";
import { createReport, fileUrl, getReports } from "../api/reports.js";

function formatDateTime(value) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function ReportList() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  const loadReports = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setReports(await getReports());
    } catch (err) {
      setError(err.message || "Could not load reports.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  async function handleGenerate() {
    setGenerating(true);
    setError("");
    try {
      await createReport({ force: true });
      await loadReports();
    } catch (err) {
      setError(err.message || "Could not generate a report.");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <section>
      <div className="toolbar">
        <button
          className="btn btn-primary"
          onClick={handleGenerate}
          disabled={generating}
        >
          {generating ? <span className="spinner" /> : <FileText size={16} />}
          {generating ? "Generating…" : "Generate report"}
        </button>
        <button
          className="btn btn-ghost"
          onClick={loadReports}
          disabled={loading || generating}
        >
          <RefreshCw size={15} />
          Refresh
        </button>
      </div>

      {error && <div className="notice notice-error">{error}</div>}

      <div className="section-title">
        <h2>Reports</h2>
        {!loading && (
          <span className="count">
            {reports.length} {reports.length === 1 ? "report" : "reports"}
          </span>
        )}
      </div>

      {loading ? (
        <div className="empty">Loading reports…</div>
      ) : reports.length === 0 ? (
        <div className="empty">No reports generated yet.</div>
      ) : (
        <ul className="report-list">
          {reports.map((report) => (
            <li key={report.id} className="report-card">
              <div className="meta">
                <div className="date">{formatDateTime(report.created_at)}</div>
                <div className="sub">
                  Report date {report.report_date} · #{report.id}
                </div>
              </div>
              <a
                className="btn-link"
                href={fileUrl(report)}
                target="_blank"
                rel="noreferrer"
              >
                <Download size={14} style={{ verticalAlign: "-2px" }} /> PDF
              </a>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
