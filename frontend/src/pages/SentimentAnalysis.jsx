import { useEffect, useState } from "react";
import { getSentiment } from "../api";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
         BarChart, Bar, XAxis, YAxis } from "recharts";

const BRAND_COLORS = { ASUS: "#6366f1", HP: "#22c55e", Dell: "#f59e0b", Lenovo: "#06b6d4" };

export default function SentimentAnalysis() {
  const [sentiment, setSentiment] = useState([]);

  useEffect(() => {
    getSentiment().then(r => setSentiment(r.data.sentiment)).catch(() => {});
  }, []);

  return (
    <div>
      <div className="page-title">Sentiment Analysis</div>

      <div className="grid-2" style={{ marginBottom: "1.5rem" }}>
        {sentiment.map((s, i) => (
          <div key={i} className="card">
            <div className="section-title">{s.Brand}</div>
            <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
              <ResponsiveContainer width={160} height={160}>
                <PieChart>
                  <Pie data={[
                    { name: "Positive", value: s.Positive },
                    { name: "Neutral",  value: s.Neutral  },
                    { name: "Negative", value: s.Negative },
                  ]} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value">
                    <Cell fill="#22c55e" />
                    <Cell fill="#94a3b8" />
                    <Cell fill="#ef4444" />
                  </Pie>
                  <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #e2e8f0" }} />
                </PieChart>
              </ResponsiveContainer>
              <div>
                <div style={{ marginBottom: 6 }}>
                  <span className="badge badge-green">+{s.Positive}% Positive</span>
                </div>
                <div style={{ marginBottom: 6 }}>
                  <span className="badge" style={{ background: "#1e293b", color: "#94a3b8" }}>
                    {s.Neutral}% Neutral
                  </span>
                </div>
                <div style={{ marginBottom: 6 }}>
                  <span className="badge badge-high">-{s.Negative}% Negative</span>
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: 8 }}>
                  {Number(s.Total).toLocaleString()} reviews analysed
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="section-title">Brand Sentiment Comparison</div>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={sentiment.map(s => ({
            brand: s.Brand, positive: s.Positive, neutral: s.Neutral, negative: s.Negative
          }))}>
            <XAxis dataKey="brand" tick={{ fill: "#94a3b8" }} />
            <YAxis tick={{ fill: "#94a3b8" }} unit="%" />
            <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #e2e8f0" }} />
            <Legend />
            <Bar dataKey="positive" name="Positive" fill="#22c55e" radius={[4,4,0,0]} />
            <Bar dataKey="neutral"  name="Neutral"  fill="#94a3b8" radius={[4,4,0,0]} />
            <Bar dataKey="negative" name="Negative" fill="#ef4444" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
