import { useEffect, useState } from "react";
import { getModelAspects } from "../api";

export default function StrengthsWeaknesses({ target }) {
  const [aspects, setAspects] = useState([]);

  useEffect(() => {
    getModelAspects(target).then(r => setAspects(r.data.model_aspects)).catch(() => {});
  }, [target]);

  // Aggregate across all target models
  const agg = aspects.reduce((acc, a) => {
    if (!acc[a.aspect]) acc[a.aspect] = { demand: 0, strength: 0, weakness: 0 };
    acc[a.aspect].demand   += a.demand;
    acc[a.aspect].strength += a.strength;
    acc[a.aspect].weakness += a.weakness;
    return acc;
  }, {});

  const rows = Object.entries(agg).map(([asp, c]) => ({
    aspect: asp, ...c,
    pos_ratio: c.demand ? +(c.strength / c.demand * 100).toFixed(1) : 0,
    neg_ratio: c.demand ? +(c.weakness / c.demand * 100).toFixed(1) : 0,
  }));

  const strengths  = rows.filter(r => r.pos_ratio >= 50).sort((a, b) => b.pos_ratio - a.pos_ratio);
  const weaknesses = rows.filter(r => r.neg_ratio >= 15).sort((a, b) => b.neg_ratio - a.neg_ratio);

  return (
    <div>
      <div className="page-title">{target} — Strengths & Weaknesses</div>

      <div className="metric-grid">
        <div className="metric-card"><div className="label">Strengths Found</div>
          <div className="value" style={{ color: "var(--green)" }}>{strengths.length}</div></div>
        <div className="metric-card"><div className="label">Weaknesses Found</div>
          <div className="value" style={{ color: "var(--red)" }}>{weaknesses.length}</div></div>
        <div className="metric-card"><div className="label">Aspects Analysed</div>
          <div className="value">{rows.length}</div></div>
      </div>

      <div className="grid-2">
        <div>
          <div className="section-title">Strengths</div>
          {strengths.length === 0
            ? <p className="empty">No strong praise signals found.</p>
            : strengths.map((s, i) => (
              <div key={i} className="card" style={{ marginBottom: "0.75rem",
                borderLeft: "3px solid var(--green)" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontWeight: 600, textTransform: "capitalize" }}>{s.aspect}</span>
                  <span style={{ color: "var(--green)", fontWeight: 700 }}>{s.pos_ratio}% positive</span>
                </div>
                <div style={{ fontSize: "0.78rem", color: "var(--muted)", marginTop: 4 }}>
                  {s.strength} positive mentions out of {s.demand} total
                </div>
                <div style={{ height: 5, background: "var(--surface2)", borderRadius: 3, marginTop: 8 }}>
                  <div style={{ height: "100%", width: `${s.pos_ratio}%`,
                    background: "var(--green)", borderRadius: 3 }} />
                </div>
              </div>
            ))
          }
        </div>

        <div>
          <div className="section-title">Weaknesses</div>
          {weaknesses.length === 0
            ? <p className="empty">No significant complaints found.</p>
            : weaknesses.map((w, i) => (
              <div key={i} className="card" style={{ marginBottom: "0.75rem",
                borderLeft: "3px solid var(--red)" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontWeight: 600, textTransform: "capitalize" }}>{w.aspect}</span>
                  <span style={{ color: "var(--red)", fontWeight: 700 }}>{w.neg_ratio}% negative</span>
                </div>
                <div style={{ fontSize: "0.78rem", color: "var(--muted)", marginTop: 4 }}>
                  {w.weakness} negative mentions out of {w.demand} total
                </div>
                <div style={{ height: 5, background: "var(--surface2)", borderRadius: 3, marginTop: 8 }}>
                  <div style={{ height: "100%", width: `${w.neg_ratio}%`,
                    background: "var(--red)", borderRadius: 3 }} />
                </div>
              </div>
            ))
          }
        </div>
      </div>
    </div>
  );
}
