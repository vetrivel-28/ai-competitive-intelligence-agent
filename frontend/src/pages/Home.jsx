import { useEffect, useState } from "react";
import { getSummary } from "../api";

const ADV_TYPE_COLOR = {
  price:     { bg: "#fff0f0", border: "#fca5a5", label: "Price" },
  rating:    { bg: "#fff0f0", border: "#fca5a5", label: "Rating" },
  feature:   { bg: "#fff0f0", border: "#fca5a5", label: "Feature" },
  complaint: { bg: "#fff0f0", border: "#fca5a5", label: "Complaint" },
};

function InsightCard({ bg, borderColor, title, subtitle }) {
  return (
    <div style={{
      background: bg,
      border: `1px solid ${borderColor}`,
      borderLeft: `4px solid ${borderColor}`,
      borderRadius: 10,
      padding: "14px 16px",
      marginBottom: 10,
    }}>
      <div style={{ fontWeight: 600, fontSize: "0.88rem", color: "#1e293b", marginBottom: 4 }}>
        {title}
      </div>
      {subtitle && (
        <div style={{ fontSize: "0.78rem", color: "#64748b", lineHeight: 1.5 }}>
          {subtitle}
        </div>
      )}
    </div>
  );
}

export default function Home({ target }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    getSummary(target).then(r => setData(r.data)).catch(() => {});
  }, [target]);

  if (!data) return <div className="loading">Loading...</div>;

  return (
    <div>
      <div className="page-title">AI Market Summary — {target}</div>

      <div className="metric-grid">
        <div className="metric-card">
          <div className="label">Brands Analysed</div>
          <div className="value">{data.brand_count}</div>
        </div>
        <div className="metric-card">
          <div className="label">Brands</div>
          <div className="value" style={{ fontSize: "0.9rem", paddingTop: 4 }}>
            {data.brands.join(", ")}
          </div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
        {/* Competitor Advantages */}
        <div className="card">
          <div className="section-title">Competitor Advantages</div>
          {data.advantages.length === 0
            ? <p className="empty">No significant advantages detected.</p>
            : data.advantages.map((a, i) => {
                const c = ADV_TYPE_COLOR[a.adv_type] || ADV_TYPE_COLOR.feature;
                return (
                  <InsightCard
                    key={i}
                    bg="#fff0f0"
                    borderColor="#fca5a5"
                    title={`${a.competitor_model} — ${a.advantage} over ${a.target_model}`}
                    subtitle={a.detail}
                  />
                );
              })
          }
        </div>

        {/* Target Weaknesses */}
        <div className="card">
          <div className="section-title">Target Weaknesses</div>
          {data.weaknesses.length === 0
            ? <p className="empty">No significant weaknesses detected.</p>
            : data.weaknesses.map((w, i) => (
                <InsightCard
                  key={i}
                  bg="#fff8ed"
                  borderColor="#fbbf24"
                  title={`${w.model} — ${w.aspect.charAt(0).toUpperCase() + w.aspect.slice(1)}`}
                  subtitle={w.summary}
                />
              ))
          }
        </div>
      </div>

      {/* Emerging Market Opportunities */}
      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <div className="section-title">Emerging Market Opportunities</div>
        <div className="grid-3">
          {data.opportunities.map((o, i) => (
            <div key={i} style={{
              background: "#eff6ff",
              border: "1px solid #93c5fd",
              borderLeft: "4px solid #3b82f6",
              borderRadius: 10,
              padding: "14px 16px",
            }}>
              <div style={{ fontWeight: 600, fontSize: "0.9rem", color: "#1e293b", marginBottom: 4 }}>
                {o.opportunity}
              </div>
              <div style={{ fontSize: "0.78rem", color: "#64748b", marginBottom: 8 }}>
                {o.mentions} mentions — {o.percentage}% of discussions
              </div>
              <div style={{ height: 5, background: "#bfdbfe", borderRadius: 3 }}>
                <div style={{
                  height: "100%",
                  width: `${Math.min(o.percentage * 3, 100)}%`,
                  background: "#3b82f6",
                  borderRadius: 3,
                }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
