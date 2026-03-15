import { useEffect, useState } from "react";
import { getModelAspects, getCompetitorAdvantages } from "../api";

const PRODUCT_TIPS = {
  battery: "Improve battery capacity and optimize power management.",
  thermal: "Improve cooling system and thermal management.",
  performance: "Upgrade CPU/GPU options for better performance.",
  display: "Improve display quality and refresh rate.",
  keyboard: "Improve keyboard feel and key travel.",
  ram: "Offer higher RAM configurations as standard.",
  storage: "Include faster NVMe SSDs as default.",
  graphics: "Partner with NVIDIA/AMD for better GPU options.",
  audio: "Upgrade speaker quality and microphone.",
  camera: "Upgrade webcam resolution.",
  design: "Improve build quality and chassis materials.",
  price: "Review pricing strategy across all segments.",
};

const MARKETING_TIPS = {
  performance: "Highlight benchmark scores in performance marketing.",
  display: "Promote display quality and high refresh rate screens.",
  battery: "Market long battery life for on-the-go users.",
  design: "Showcase premium build quality in unboxing campaigns.",
  gaming: "Focus marketing on gaming performance and FPS benchmarks.",
  price: "Run student discount campaigns and education bundles.",
};

export default function Strategy({ target }) {
  const [aspects, setAspects] = useState([]);
  const [advantages, setAdvantages] = useState([]);

  useEffect(() => {
    getModelAspects(target).then(r => setAspects(r.data.model_aspects)).catch(() => {});
    getCompetitorAdvantages(target).then(r => setAdvantages(r.data.advantages)).catch(() => {});
  }, [target]);

  // Derive weaknesses
  const agg = aspects.reduce((acc, a) => {
    if (!acc[a.aspect]) acc[a.aspect] = { demand: 0, weakness: 0 };
    acc[a.aspect].demand  += a.demand;
    acc[a.aspect].weakness += a.weakness;
    return acc;
  }, {});

  const weakAspects = Object.entries(agg)
    .map(([asp, c]) => ({ asp, neg: c.demand ? +(c.weakness/c.demand*100).toFixed(1) : 0 }))
    .filter(x => x.neg >= 15)
    .sort((a, b) => b.neg - a.neg);

  const productStrats = [...new Set(weakAspects.map(w => PRODUCT_TIPS[w.asp]).filter(Boolean))];
  const marketingStrats = [...new Set(weakAspects.map(w => MARKETING_TIPS[w.asp]).filter(Boolean))];

  const pricingStrats = advantages.some(a => a.advantage.toLowerCase().includes("price"))
    ? ["Reduce mid-range pricing", "Offer competitive bundles", "Introduce entry-level SKUs"]
    : ["Review pricing strategy across all segments", "Offer flexible EMI and financing options"];

  return (
    <div>
      <div className="page-title">{target} — Strategy Recommendations</div>

      <div className="grid-3">
        <div className="card">
          <div className="section-title">Product Strategy</div>
          {productStrats.length === 0
            ? <p className="empty">No product improvements needed.</p>
            : productStrats.map((s, i) => (
              <div key={i} className="strat-card">
                <div style={{ fontSize: "0.88rem", color: "#1e293b" }}>{s}</div>
              </div>
            ))
          }
        </div>

        <div className="card">
          <div className="section-title">Pricing Strategy</div>
          {pricingStrats.map((s, i) => (
            <div key={i} className="strat-card">
              <div style={{ fontSize: "0.88rem", color: "#1e293b" }}>{s}</div>
            </div>
          ))}
        </div>

        <div className="card">
          <div className="section-title">Marketing Strategy</div>
          {marketingStrats.length === 0
            ? <p className="empty">No specific marketing actions needed.</p>
            : marketingStrats.map((s, i) => (
              <div key={i} className="strat-card">
                <div style={{ fontSize: "0.88rem", color: "#1e293b" }}>{s}</div>
              </div>
            ))
          }
        </div>
      </div>

      {weakAspects.length > 0 && (
        <div className="card" style={{ marginTop: "1.5rem" }}>
          <div className="section-title">Model-Specific Actions</div>
          {aspects
            .filter(a => (a.demand ? a.weakness/a.demand*100 : 0) >= 20)
            .sort((a, b) => b.neg_ratio - a.neg_ratio)
            .slice(0, 8)
            .map((a, i) => (
              <div key={i} style={{ padding: "0.6rem 0", borderBottom: "1px solid var(--border)",
                fontSize: "0.88rem" }}>
                <span style={{ color: "var(--accent2)", fontWeight: 600 }}>{a.laptop_name}</span>
                <span style={{ color: "var(--muted)" }}> — Improve </span>
                <span style={{ textTransform: "capitalize" }}>{a.aspect}</span>
                <span style={{ color: "var(--red)", marginLeft: 8, fontSize: "0.78rem" }}>
                  ({a.neg_ratio}% negative)
                </span>
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
}
