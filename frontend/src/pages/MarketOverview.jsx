import { useEffect, useState } from "react";
import { getPriceModels, getSentiment, getAspects } from "../api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Legend, Cell, PieChart, Pie,
} from "recharts";

const BRAND_COLORS = { ASUS: "#6366f1", HP: "#22c55e", Dell: "#f59e0b", Lenovo: "#06b6d4" };
const ASPECT_COLORS = ["#6366f1","#22c55e","#f59e0b","#ef4444","#06b6d4","#a855f7","#ec4899","#14b8a6","#f97316","#84cc16","#e879f9","#38bdf8"];

export default function MarketOverview() {
  const [allModels, setAllModels] = useState([]);
  const [sentiment, setSentiment] = useState([]);
  const [aspects, setAspects] = useState([]);
  const [brand, setBrand] = useState("ASUS");   // ASUS default

  useEffect(() => {
    getPriceModels().then(r => setAllModels(r.data.models)).catch(() => {});
    getSentiment().then(r => setSentiment(r.data.sentiment)).catch(() => {});
    getAspects().then(r => setAspects(r.data.aspects)).catch(() => {});
  }, []);

  const brands = ["All", ...Object.keys(BRAND_COLORS)];

  // Price chart — filtered by selected brand, sorted low→high
  const priceData = allModels
    .filter(m => m.price && (brand === "All" || m.brand === brand))
    .sort((a, b) => a.price - b.price)
    .map(m => ({
      name: m.laptop_name.replace(/^(ASUS|HP|Dell|Lenovo)\s+/i, ""),
      fullName: m.laptop_name,
      price: m.price,
      rating: m.rating,
      brand: m.brand,
    }));

  // Summary stats per brand
  const brandStats = Object.keys(BRAND_COLORS).map(b => {
    const bModels = allModels.filter(m => m.brand === b && m.price);
    const prices = bModels.map(m => m.price);
    const ratings = bModels.filter(m => m.rating).map(m => m.rating);
    return {
      brand: b,
      count: bModels.length,
      minPrice: prices.length ? Math.min(...prices) : 0,
      maxPrice: prices.length ? Math.max(...prices) : 0,
      avgRating: ratings.length ? (ratings.reduce((s, r) => s + r, 0) / ratings.length).toFixed(1) : "—",
    };
  });

  // Sentiment data
  const sentData = sentiment.map(s => ({
    brand: s.Brand, positive: s.Positive, negative: s.Negative, neutral: s.Neutral,
  }));

  // Aspect demand pie
  const aspectPie = aspects.slice(0, 8).map((a, i) => ({
    name: a.aspect, value: a.demand, fill: ASPECT_COLORS[i],
  }));

  const chartHeight = priceData.length > 8 ? 360 : 280;

  return (
    <div>
      <div className="page-title">Market Overview</div>

      {/* ── Brand Summary Cards ── */}
      <div className="metric-grid" style={{ marginBottom: "1.5rem" }}>
        {brandStats.map(b => (
          <div key={b.brand} className="metric-card"
            style={{ borderTop: `3px solid ${BRAND_COLORS[b.brand]}`, cursor: "pointer" }}
            onClick={() => setBrand(b.brand)}>
            <div className="label">{b.brand}</div>
            <div className="value" style={{ fontSize: "1.1rem", color: BRAND_COLORS[b.brand] }}>{b.count} models</div>
            <div style={{ fontSize: "0.78rem", color: "var(--muted)", marginTop: 4 }}>
              ₹{(b.minPrice / 1000).toFixed(0)}k – ₹{(b.maxPrice / 1000).toFixed(0)}k
            </div>
            <div style={{ fontSize: "0.78rem", color: "var(--yellow)", marginTop: 2 }}>{b.avgRating} avg</div>
          </div>
        ))}
      </div>

      {/* ── Price by Model ── */}
      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <div className="section-title" style={{ margin: 0 }}>Price by Model</div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {brands.map(b => (
              <button key={b} onClick={() => setBrand(b)}
                style={{
                  padding: "4px 12px", borderRadius: 6, fontSize: "0.78rem", cursor: "pointer",
                  background: brand === b ? (BRAND_COLORS[b] || "var(--accent)") : "var(--surface2)",
                  color: brand === b ? "#fff" : "var(--muted)",
                  border: `1px solid ${brand === b ? "transparent" : "var(--border)"}`,
                }}>
                {b}
              </button>
            ))}
          </div>
        </div>

        {priceData.length === 0
          ? <p className="empty">No price data available.</p>
          : (
            <ResponsiveContainer width="100%" height={chartHeight}>
              <BarChart data={priceData} margin={{ bottom: 70, left: 10 }}>
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#94a3b8" }}
                  angle={-35} textAnchor="end" interval={0} />
                <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }}
                  tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null;
                    const d = payload[0].payload;
                    return (
                      <div style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: 8, padding: "10px 14px" }}>
                        <div style={{ color: "#e2e8f0", fontWeight: 600, marginBottom: 4 }}>{d.fullName}</div>
                        <div style={{ color: BRAND_COLORS[d.brand] }}>₹{Number(d.price).toLocaleString("en-IN")}</div>
                        {d.rating && <div style={{ color: "#fbbf24", fontSize: "0.82rem" }}>{d.rating}</div>}
                      </div>
                    );
                  }}
                />
                <Bar dataKey="price" radius={[4, 4, 0, 0]}>
                  {priceData.map((e, i) => (
                    <Cell key={i} fill={BRAND_COLORS[e.brand] || "#6366f1"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )
        }

        {/* Legend */}
        {brand === "All" && (
          <div style={{ display: "flex", gap: 16, marginTop: 10, flexWrap: "wrap" }}>
            {Object.entries(BRAND_COLORS).map(([b, c]) => (
              <span key={b} style={{ fontSize: "0.78rem", color: "var(--muted)", display: "flex", alignItems: "center", gap: 5 }}>
                <span style={{ width: 10, height: 10, borderRadius: 2, background: c, display: "inline-block" }} />
                {b}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* ── Sentiment + Aspect Demand side by side ── */}
      <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
        <div className="card">
          <div className="section-title">Brand Sentiment</div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={sentData} margin={{ bottom: 5 }}>
              <XAxis dataKey="brand" tick={{ fill: "#94a3b8", fontSize: 12 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} unit="%" />
              <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #e2e8f0" }} />
              <Legend />
              <Bar dataKey="positive" name="Positive" fill="#22c55e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="neutral"  name="Neutral"  fill="#94a3b8" radius={[4, 4, 0, 0]} />
              <Bar dataKey="negative" name="Negative" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="section-title">What Buyers Talk About</div>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={aspectPie} dataKey="value" nameKey="name"
                cx="50%" cy="50%" outerRadius={90} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={false}>
                {aspectPie.map((e, i) => <Cell key={i} fill={e.fill} />)}
              </Pie>
              <Tooltip formatter={(v, n) => [v + " mentions", n]}
                contentStyle={{ background: "#ffffff", border: "1px solid #e2e8f0" }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Price vs Rating table ── */}
      <div className="card">
        <div className="section-title">Price vs Rating — {brand === "All" ? "All Brands" : brand}</div>
        <table>
          <thead>
            <tr>
              <th>Model</th>
              <th>Brand</th>
              <th>Price</th>
              <th>Rating</th>
              <th>Value Score</th>
            </tr>
          </thead>
          <tbody>
            {priceData.map((m, i) => {
              const valueScore = m.rating ? ((m.rating / 5) * 100 - (m.price / 230000) * 50).toFixed(0) : "—";
              return (
                <tr key={i}>
                  <td>{m.fullName}</td>
                  <td style={{ color: BRAND_COLORS[m.brand] }}>{m.brand}</td>
                  <td>₹{Number(m.price).toLocaleString("en-IN")}</td>
                  <td style={{ color: "#fbbf24" }}>{m.rating ? `${m.rating}` : "—"}</td>
                  <td style={{ color: valueScore > 60 ? "var(--green)" : valueScore > 40 ? "var(--yellow)" : "var(--red)" }}>
                    {valueScore}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
