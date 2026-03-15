import { useEffect, useState } from "react";
import { getModels, getModelAspects, getSpecPeers } from "../api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from "recharts";

const COLORS = ["#6366f1","#22c55e","#f59e0b","#ef4444","#06b6d4","#a855f7"];

function AspectBar({ label, pos, neg }) {
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", marginBottom: 2 }}>
        <span style={{ color: "var(--text)" }}>{label}</span>
        <span style={{ color: "var(--muted)" }}>+{pos}% / -{neg}%</span>
      </div>
      <div style={{ display: "flex", height: 6, borderRadius: 3, overflow: "hidden", background: "var(--surface2)" }}>
        <div style={{ width: `${pos}%`, background: "var(--green)" }} />
        <div style={{ width: `${neg}%`, background: "var(--red)", marginLeft: "auto" }} />
      </div>
    </div>
  );
}

function ModelCard({ model, target }) {
  const [aspects, setAspects] = useState([]);
  const [peers, setPeers] = useState(null);
  const [open, setOpen] = useState(false);
  const [peerOpen, setPeerOpen] = useState(false);

  useEffect(() => {
    if (open) {
      getModelAspects(target, model.laptop_name)
        .then(r => setAspects(r.data.model_aspects))
        .catch(() => {});
    }
  }, [open]);

  const loadPeers = () => {
    if (!peers) {
      getSpecPeers(model.laptop_name)
        .then(r => setPeers(r.data))
        .catch(() => setPeers({ peers: [], group: "Unknown" }));
    }
    setPeerOpen(p => !p);
  };

  const weaknesses = aspects.filter(a => a.neg_ratio >= 20).sort((a, b) => b.neg_ratio - a.neg_ratio);
  const strengths  = aspects.filter(a => a.pos_ratio >= 50).sort((a, b) => b.pos_ratio - a.pos_ratio);

  return (
    <div className="card" style={{ marginBottom: "1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <span style={{ fontWeight: 600 }}>{model.laptop_name}</span>
          {model.price && (
            <span style={{ marginLeft: 12, color: "var(--accent2)", fontSize: "0.85rem" }}>
              ₹{Number(model.price).toLocaleString("en-IN")}
            </span>
          )}
          {model.rating && (
            <span style={{ marginLeft: 10, color: "var(--yellow)", fontSize: "0.85rem" }}>
              {model.rating}
            </span>
          )}
        </div>
        <button onClick={() => setOpen(o => !o)}
          style={{ background: "var(--surface2)", border: "1px solid var(--border)",
                   color: "var(--muted)", borderRadius: 6, padding: "4px 12px", fontSize: "0.8rem" }}>
          {open ? "▲ Hide" : "▼ Review Analysis"}
        </button>
      </div>

      {open && (
        <div style={{ marginTop: "1rem" }}>
          <div className="grid-2">
            <div>
              <div className="section-title" style={{ fontSize: "0.85rem" }}>Weaknesses</div>
              {weaknesses.length === 0
                ? <p className="empty">No significant complaints.</p>
                : weaknesses.slice(0, 5).map((a, i) => (
                  <AspectBar key={i} label={a.aspect} pos={a.pos_ratio} neg={a.neg_ratio} />
                ))
              }
            </div>
            <div>
              <div className="section-title" style={{ fontSize: "0.85rem" }}>Strengths</div>
              {strengths.length === 0
                ? <p className="empty">No strong praise signals.</p>
                : strengths.slice(0, 5).map((a, i) => (
                  <AspectBar key={i} label={a.aspect} pos={a.pos_ratio} neg={a.neg_ratio} />
                ))
              }
            </div>
          </div>

          <button onClick={loadPeers}
            style={{ marginTop: "1rem", background: "var(--surface2)", border: "1px solid var(--border)",
                     color: "var(--accent2)", borderRadius: 6, padding: "5px 14px", fontSize: "0.8rem" }}>
            {peerOpen ? "Hide" : "Show"} Spec-Based Comparison
          </button>

          {peerOpen && peers && (
            <div style={{ marginTop: "1rem" }}>
              <div style={{ fontSize: "0.78rem", color: "var(--muted)", marginBottom: 8 }}>
                Group: {peers.group}
              </div>
              <table>
                <thead>
                  <tr><th>Model</th><th>Brand</th><th>Price</th><th>Rating</th></tr>
                </thead>
                <tbody>
                  <tr style={{ background: "var(--surface2)" }}>
                    <td>{model.laptop_name}</td>
                    <td>{target}</td>
                    <td>{model.price ? `₹${Number(model.price).toLocaleString("en-IN")}` : "—"}</td>
                    <td>{model.rating ?? "—"}</td>
                  </tr>
                  {peers.peers.map((p, i) => (
                    <tr key={i}>
                      <td>{p.model}</td>
                      <td>{p.brand}</td>
                      <td>{p.price ? `₹${Number(p.price).toLocaleString("en-IN")}` : "—"}</td>
                      <td>{p.rating ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function TargetOverview({ target }) {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getModels(target)
      .then(r => {
        setModels(r.data.models || []);
        setLoading(false);
      })
      .catch(err => {
        setError(`Failed to load data: ${err.message}. Make sure the API server is running on http://localhost:8000`);
        setLoading(false);
      });
  }, [target]);

  if (loading) return <div className="page-title" style={{ color: "var(--muted)" }}>Loading {target} models...</div>;
  if (error)   return <div className="page-title" style={{ color: "var(--red)", fontSize: "1rem" }}>{error}</div>;
  if (models.length === 0) return <div className="page-title" style={{ color: "var(--muted)" }}>No models found for {target}. Check that the API is running and data is loaded.</div>;

  const prices  = models.filter(m => m.price).map(m => ({ name: m.laptop_name, value: m.price }));
  const ratings = models.filter(m => m.rating).map(m => ({ name: m.laptop_name, value: m.rating }));

  return (
    <div>
      <div className="page-title">{target} — Target Overview</div>

      <div className="metric-grid">
        <div className="metric-card"><div className="label">Models Listed</div>
          <div className="value">{models.length}</div></div>
        <div className="metric-card"><div className="label">Price Range</div>
          <div className="value" style={{ fontSize: "1rem" }}>
            {models.filter(m=>m.price).length
              ? `₹${Math.min(...models.filter(m=>m.price).map(m=>m.price)).toLocaleString("en-IN")} – ₹${Math.max(...models.filter(m=>m.price).map(m=>m.price)).toLocaleString("en-IN")}`
              : "—"}
          </div>
        </div>
        <div className="metric-card"><div className="label">Avg Rating</div>
          <div className="value">
            {ratings.length ? (ratings.reduce((s,r)=>s+r.value,0)/ratings.length).toFixed(1) : "—"}
          </div>
        </div>
      </div>

      <div className="section-title">Model-Level Review Analysis</div>
      {models.map((m, i) => (
        <ModelCard key={i} model={m} target={target} />
      ))}
    </div>
  );
}
