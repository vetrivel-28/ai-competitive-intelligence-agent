import { useEffect, useState } from "react";
import { getInsights } from "../api";

const BC = { ASUS:"#6366f1", HP:"#22c55e", Dell:"#f59e0b", Lenovo:"#06b6d4" };

const TYPE_META = {
  threat:    { label:"Competitor Threat",   borderColor:"#dc2626", icon:"⚠" },
  price:     { label:"Price Insight",       borderColor:"#f59e0b", icon:"₹" },
  gap:       { label:"Feature Gap",         borderColor:"#06b6d4", icon:"↑" },
  advantage: { label:"ASUS Advantage",      borderColor:"#16a34a", icon:"✓" },
  weakness:  { label:"Weakness Detected",   borderColor:"#f97316", icon:"!" },
};

const SEV_COLOR = { High:"#dc2626", Medium:"#d97706", Low:"#16a34a" };

const ASUS_MODELS = [
  "ASUS VivoBook 15 X1502ZA","ASUS VivoBook Go 15 E1504FA","ASUS VivoBook 16 X1605",
  "ASUS ZenBook 14 OLED","ASUS TUF F15 FX506","ASUS TUF A15 FA506",
  "ASUS TUF F15 FX507","ASUS ROG Strix G15","ASUS ROG Zephyrus G14","ASUS ROG Strix Scar 15",
];

const fmt = v => v != null ? "₹" + Number(v).toLocaleString("en-IN") : "--";

function InsightCard({ ins }) {
  const meta = TYPE_META[ins.type] || TYPE_META.gap;
  return (
    <div className="card" style={{
      marginBottom:"0.75rem",
      borderLeft:"3px solid " + meta.borderColor,
    }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", gap:8 }}>
        <div style={{ flex:1 }}>
          <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:4 }}>
            <span style={{ fontSize:"0.72rem", fontWeight:700, color:meta.borderColor,
                           textTransform:"uppercase", letterSpacing:"0.05em" }}>
              {meta.icon} {meta.label}
            </span>
            {ins.brand && ins.brand !== "ASUS" && (
              <span style={{ fontSize:"0.72rem", color:BC[ins.brand]||"var(--muted)",
                             background:"var(--surface2)", borderRadius:4, padding:"1px 6px" }}>
                {ins.brand}
              </span>
            )}
          </div>
          <div style={{ fontWeight:600, fontSize:"0.9rem", color:"var(--text)", marginBottom:4 }}>
            {ins.title}
          </div>
          <div style={{ fontSize:"0.83rem", color:"var(--muted)", lineHeight:1.5 }}>
            {ins.body}
          </div>
        </div>
        {ins.severity && (
          <span style={{
            fontSize:"0.7rem", fontWeight:700, whiteSpace:"nowrap",
            color:SEV_COLOR[ins.severity]||"var(--muted)",
            background:"var(--surface2)", borderRadius:4, padding:"2px 8px",
          }}>{ins.severity}</span>
        )}
      </div>
    </div>
  );
}

function SpecRow({ label, asusVal, compVal, better }) {
  return (
    <tr>
      <td style={{ color:"var(--muted)", fontSize:"0.82rem" }}>{label}</td>
      <td style={{ fontWeight:600, color:"var(--accent2)" }}>{asusVal}</td>
      <td style={{ fontWeight:600, color: better === "comp" ? "var(--green)" : better === "asus" ? "var(--red)" : "var(--text)" }}>
        {compVal}
        {better === "comp" && <span style={{ marginLeft:4, fontSize:"0.7rem", color:"var(--green)" }}>▲</span>}
        {better === "asus" && <span style={{ marginLeft:4, fontSize:"0.7rem", color:"var(--red)" }}>▼</span>}
      </td>
    </tr>
  );
}

export default function Insights({ target }) {
  const [sel, setSel]         = useState("ASUS ROG Strix G15");
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr]         = useState(null);
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    setLoading(true); setErr(null); setData(null);
    getInsights(sel)
      .then(r => { setData(r.data); setLoading(false); })
      .catch(e => { setErr("API error: " + e.message); setLoading(false); });
  }, [sel]);

  const analysis   = data?.analysis;
  const insights   = data?.insights || [];
  const competitors = analysis?.competitors || [];

  const threats   = insights.filter(i => i.type === "threat");
  const prices    = insights.filter(i => i.type === "price");
  const gaps      = insights.filter(i => i.type === "gap");
  const advantages= insights.filter(i => i.type === "advantage");
  const weaknesses= insights.filter(i => i.type === "weakness");

  return (
    <div>
      <div className="page-title">Insights — AI Competitor Intelligence</div>

      {/* Model selector */}
      <div className="card" style={{ marginBottom:"1.5rem" }}>
        <div className="section-title">Select ASUS Model</div>
        <div style={{ display:"flex", flexWrap:"wrap", gap:8 }}>
          {ASUS_MODELS.map(m => (
            <button key={m} onClick={() => setSel(m)} style={{
              padding:"6px 14px", borderRadius:6, fontSize:"0.8rem", cursor:"pointer",
              background: sel===m ? BC.ASUS : "var(--surface2)",
              color: sel===m ? "#fff" : "var(--muted)",
              border:"1px solid "+(sel===m ? "transparent" : "var(--border)"),
            }}>{m.replace("ASUS ","")}</button>
          ))}
        </div>
      </div>

      {loading && <div style={{ color:"var(--muted)", padding:"3rem", textAlign:"center" }}>Generating insights...</div>}
      {err     && <div style={{ color:"var(--red)", padding:"1rem", background:"var(--surface)", borderRadius:8 }}>{err}</div>}

      {!loading && !err && data && (
        <>
          {/* Summary metrics */}
          {analysis && (
            <div className="metric-grid" style={{ marginBottom:"1.5rem" }}>
              <div className="metric-card">
                <div className="label">ASUS Model</div>
                <div style={{ fontSize:"0.9rem", fontWeight:700, color:"var(--accent2)", marginTop:4 }}>{analysis.asus_model}</div>
              </div>
              <div className="metric-card">
                <div className="label">Price</div>
                <div className="value" style={{ fontSize:"1.1rem" }}>{fmt(analysis.asus_price)}</div>
              </div>
              <div className="metric-card">
                <div className="label">Competitors Found</div>
                <div className="value">{competitors.length}</div>
              </div>
              <div className="metric-card">
                <div className="label">Insights Generated</div>
                <div className="value">{insights.length}</div>
              </div>
            </div>
          )}

          {/* Insight cards grouped by type */}
          {threats.length > 0 && (
            <div style={{ marginBottom:"1.5rem" }}>
              <div className="section-title">Competitor Threats</div>
              {threats.map((ins, i) => <InsightCard key={i} ins={ins} />)}
            </div>
          )}

          {prices.length > 0 && (
            <div style={{ marginBottom:"1.5rem" }}>
              <div className="section-title">Pricing Insights</div>
              {prices.map((ins, i) => <InsightCard key={i} ins={ins} />)}
            </div>
          )}

          {gaps.length > 0 && (
            <div style={{ marginBottom:"1.5rem" }}>
              <div className="section-title">Feature Gaps</div>
              {gaps.map((ins, i) => <InsightCard key={i} ins={ins} />)}
            </div>
          )}

          {weaknesses.length > 0 && (
            <div style={{ marginBottom:"1.5rem" }}>
              <div className="section-title">Detected Weaknesses</div>
              {weaknesses.map((ins, i) => <InsightCard key={i} ins={ins} />)}
            </div>
          )}

          {advantages.length > 0 && (
            <div style={{ marginBottom:"1.5rem" }}>
              <div className="section-title">ASUS Advantages</div>
              {advantages.map((ins, i) => <InsightCard key={i} ins={ins} />)}
            </div>
          )}

          {insights.length === 0 && (
            <div className="card"><p className="empty">No insights generated for this model. Ensure the API is running and data is loaded.</p></div>
          )}

          {/* Ranked competitor table */}
          {competitors.length > 0 && (
            <div className="card" style={{ marginBottom:"1.5rem" }}>
              <div className="section-title">Ranked Competitor Analysis</div>
              <p style={{ fontSize:"0.78rem", color:"var(--muted)", marginBottom:"0.75rem" }}>
                Competitors ranked by spec similarity score to {sel}.
              </p>
              <div style={{ overflowX:"auto" }}>
                <table>
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Model</th>
                      <th>Brand</th>
                      <th>Match Score</th>
                      <th>Price</th>
                      <th>Price Diff</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {competitors.map((c, i) => (
                      <>
                        <tr key={c.model}>
                          <td style={{ color:"var(--muted)", fontSize:"0.82rem" }}>#{i+1}</td>
                          <td style={{ fontWeight:600, color:BC[c.brand]||"var(--text)" }}>{c.model}</td>
                          <td>
                            <span style={{ color:BC[c.brand]||"var(--muted)", fontSize:"0.82rem" }}>{c.brand}</span>
                          </td>
                          <td>
                            <div style={{ display:"flex", alignItems:"center", gap:6 }}>
                              <div style={{ width:60, height:6, borderRadius:3, background:"var(--surface2)", overflow:"hidden" }}>
                                <div style={{ width:`${c.match_score}%`, height:"100%",
                                  background: c.match_score>=80?"var(--green)":c.match_score>=60?"var(--yellow)":"var(--red)" }} />
                              </div>
                              <span style={{ fontSize:"0.82rem", fontWeight:600,
                                color: c.match_score>=80?"var(--green)":c.match_score>=60?"var(--yellow)":"var(--red)" }}>
                                {c.match_score}%
                              </span>
                            </div>
                          </td>
                          <td style={{ fontSize:"0.82rem" }}>{fmt(c.price)}</td>
                          <td style={{ fontSize:"0.82rem",
                            color: c.price_diff==null?"var(--muted)":c.price_diff<0?"var(--green)":"var(--red)" }}>
                            {c.price_diff != null
                              ? (c.price_diff < 0 ? "-₹" + Math.abs(c.price_diff).toLocaleString("en-IN") : "+₹" + c.price_diff.toLocaleString("en-IN"))
                              : "--"}
                          </td>
                          <td>
                            {Object.keys(c.spec_diff||{}).length > 0 && (
                              <button onClick={() => setExpanded(p => ({...p,[c.model]:!p[c.model]}))}
                                style={{ background:"var(--surface2)", border:"1px solid var(--border)",
                                         color:"var(--muted)", borderRadius:6, padding:"2px 8px",
                                         fontSize:"0.75rem", cursor:"pointer" }}>
                                {expanded[c.model] ? "Hide" : "Spec Diff"}
                              </button>
                            )}
                          </td>
                        </tr>
                        {expanded[c.model] && Object.keys(c.spec_diff||{}).length > 0 && (
                          <tr key={c.model+"-diff"}>
                            <td colSpan={7} style={{ padding:"0.5rem 1rem", background:"var(--surface2)" }}>
                              <table style={{ width:"auto", fontSize:"0.8rem" }}>
                                <thead>
                                  <tr>
                                    <th style={{ background:"transparent", fontSize:"0.75rem" }}>Spec</th>
                                    <th style={{ background:"transparent", fontSize:"0.75rem" }}>ASUS</th>
                                    <th style={{ background:"transparent", fontSize:"0.75rem" }}>{c.brand}</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {Object.entries(c.spec_diff).map(([k, v]) => {
                                    const better = k === "gpu"
                                      ? (v.competitor > v.asus ? "comp" : "asus")
                                      : (typeof v.competitor === "number"
                                          ? (v.competitor > v.asus ? "comp" : "asus")
                                          : "none");
                                    return (
                                      <SpecRow key={k}
                                        label={k.replace("_"," ").toUpperCase()}
                                        asusVal={String(v.asus)}
                                        compVal={String(v.competitor)}
                                        better={better}
                                      />
                                    );
                                  })}
                                </tbody>
                              </table>
                            </td>
                          </tr>
                        )}
                      </>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
