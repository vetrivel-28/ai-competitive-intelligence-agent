import { useEffect, useState } from "react";
import { getOpportunities } from "../api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const COLORS = ["#6366f1","#22c55e","#f59e0b","#ef4444","#06b6d4","#a855f7","#ec4899","#14b8a6","#f97316","#84cc16","#8b5cf6","#0ea5e9"];

const TIPS = {
  performance: "Highlight benchmark scores and CPU/GPU performance in marketing.",
  battery:     "Develop ultra-slim models with 15+ hour battery life.",
  display:     "Promote high-refresh OLED displays for creators and gamers.",
  gaming:      "Launch dedicated gaming lines with RGB branding and high FPS.",
  price:       "Release budget-friendly variants targeting first-time buyers.",
  design:      "Showcase premium build quality and slim form factor.",
  thermal:     "Invest in better cooling systems to reduce heat complaints.",
  ram:         "Offer higher RAM configurations as standard.",
  graphics:    "Partner with NVIDIA/AMD for exclusive GPU bundles.",
  storage:     "Include faster NVMe SSDs as default storage.",
  keyboard:    "Improve keyboard travel and backlight quality.",
  audio:       "Upgrade speaker quality for content creators.",
};

export default function Opportunities() {
  const [opps, setOpps] = useState([]);

  useEffect(() => {
    getOpportunities().then(r => setOpps(r.data.opportunities)).catch(() => {});
  }, []);

  return (
    <div>
      <div className="page-title">Market Opportunity Insights</div>

      <div className="metric-grid">
        <div className="metric-card"><div className="label">Opportunities</div>
          <div className="value">{opps.length}</div></div>
        <div className="metric-card"><div className="label">Total Mentions</div>
          <div className="value">{opps.reduce((s, o) => s + o.mentions, 0).toLocaleString()}</div></div>
        <div className="metric-card"><div className="label">Top Opportunity</div>
          <div className="value" style={{ fontSize: "1rem" }}>{opps[0]?.opportunity || "—"}</div></div>
      </div>

      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <div className="section-title">Trending Aspects by Mention Count</div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={opps} layout="vertical" margin={{ left: 20 }}>
            <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis type="category" dataKey="opportunity" tick={{ fill: "#94a3b8", fontSize: 12 }} width={100} />
            <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #e2e8f0" }} />
            <Bar dataKey="mentions" radius={[0,4,4,0]}>
              {opps.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="section-title">Opportunity Breakdown</div>
      <div className="grid-3" style={{ marginBottom: "1.5rem" }}>
        {opps.map((o, i) => (
          <div key={i} className="opp-card">
            <div style={{ fontWeight: 600 }}>{o.opportunity}</div>
            <div style={{ fontSize: "0.78rem", color: "var(--muted)", margin: "4px 0" }}>
              {o.mentions.toLocaleString()} mentions — {o.percentage}%
            </div>
            <div className="opp-bar" style={{ width: `${Math.min(o.percentage * 3, 100)}%`,
              background: COLORS[i % COLORS.length] }} />
          </div>
        ))}
      </div>

      <div className="section-title">Strategic Recommendations</div>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {opps.slice(0, 5).map((o, i) => {
          const key = o.opportunity.toLowerCase();
          const tip = Object.entries(TIPS).find(([k]) => key.includes(k))?.[1]
            || `Invest in R&D and marketing for the ${o.opportunity} segment.`;
          return (
            <div key={i} className="strat-card">
              <div style={{ fontWeight: 600, marginBottom: 4, fontSize: "0.9rem" }}>
                {o.opportunity} <span style={{ color: "var(--muted)", fontWeight: 400 }}>({o.mentions} mentions)</span>
              </div>
              <div style={{ fontSize: "0.85rem", color: "#374151" }}>{tip}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
