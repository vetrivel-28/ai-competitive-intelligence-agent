import { useEffect, useState, useMemo } from "react";
import { getCompetitorAdvantages } from "../api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, Legend } from "recharts";

const BC   = { ASUS:"#6366f1", HP:"#22c55e", Dell:"#f59e0b", Lenovo:"#06b6d4" };
const SEV  = { High:{ color:"#b91c1c", bg:"#fee2e2", label:"High" }, Medium:{ color:"#92400e", bg:"#fef3c7", label:"Medium" }, Low:{ color:"#15803d", bg:"#dcfce7", label:"Low" } };
const TYPE = { price:"Price", rating:"Rating", feature:"Feature", complaint:"Complaint" };
const TYPE_COLOR = { price:"#22c55e", rating:"#fbbf24", feature:"#06b6d4", complaint:"#f97316" };

function SevBadge({ sev }) {
  const s = SEV[sev] || SEV.Low;
  return <span style={{ background:s.bg, color:s.color, borderRadius:4, padding:"2px 8px", fontSize:"0.72rem", fontWeight:700, whiteSpace:"nowrap" }}>{s.label}</span>;
}

function MetricCard({ label, value, sub, color }) {
  return (
    <div className="metric-card">
      <div className="label">{label}</div>
      <div className="value" style={{ color: color||"var(--accent2)", fontSize:"1.4rem" }}>{value}</div>
      {sub && <div style={{ fontSize:"0.72rem", color:"var(--muted)", marginTop:3 }}>{sub}</div>}
    </div>
  );
}

export default function CompetitorAdvantages({ target }) {
  const [all, setAll]           = useState([]);
  const [loading, setLoading]   = useState(true);
  const [err, setErr]           = useState(null);
  const [fBrand, setFBrand]     = useState("All");
  const [fSev, setFSev]         = useState("All");
  const [fType, setFType]       = useState("All");
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    setLoading(true);
    getCompetitorAdvantages(target)
      .then(r => { setAll(r.data.advantages || []); setLoading(false); })
      .catch(e => { setErr(e.message); setLoading(false); });
  }, [target]);

  const brands = useMemo(() => ["All", ...Array.from(new Set(all.map(a => a.competitor).filter(b => b !== "ASUS")))], [all]);
  const types  = ["All", "price", "rating", "feature", "complaint"];
  const sevs   = ["All", "High", "Medium", "Low"];

  const filtered = useMemo(() => all.filter(a =>
    a.competitor !== "ASUS" &&
    (fBrand === "All" || a.competitor === fBrand) &&
    (fSev   === "All" || a.severity   === fSev) &&
    (fType  === "All" || a.adv_type   === fType)
  ), [all, fBrand, fSev, fType]);

  // Feature frequency chart — how many times each feature beats ASUS
  const featChart = useMemo(() => {
    const counts = {};
    filtered.forEach(a => {
      const k = a.advantage;
      if (!counts[k]) counts[k] = { feature:k, High:0, Medium:0, Low:0, total:0 };
      counts[k][a.severity]++;
      counts[k].total++;
    });
    return Object.values(counts).sort((a,b) => b.total - a.total).slice(0, 10);
  }, [filtered]);

  // Group by competitor brand -> model
  const grouped = useMemo(() => {
    const g = {};
    filtered.forEach(a => {
      if (!g[a.competitor]) g[a.competitor] = {};
      const key = a.competitor_model + " vs " + a.target_model;
      if (!g[a.competitor][key]) g[a.competitor][key] = { competitor_model:a.competitor_model, target_model:a.target_model, items:[] };
      g[a.competitor][key].items.push(a);
    });
    // Sort each brand's matchups by High count desc
    Object.keys(g).forEach(brand => {
      const sorted = Object.values(g[brand]).sort((a,b) => {
        const ha = a.items.filter(x=>x.severity==="High").length;
        const hb = b.items.filter(x=>x.severity==="High").length;
        return hb - ha;
      });
      g[brand] = sorted;
    });
    return g;
  }, [filtered]);

  // Executive summary stats
  const highCount    = filtered.filter(a => a.severity === "High").length;
  const featuresHit  = new Set(filtered.map(a => a.advantage)).size;
  const brandsAhead  = new Set(filtered.map(a => a.competitor)).size;

  if (loading) return <div style={{ color:"var(--muted)", padding:"3rem", textAlign:"center" }}>Analysing competitor data...</div>;
  if (err)     return <div style={{ color:"var(--red)", padding:"1rem" }}>Error: {err}</div>;

  return (
    <div>
      <div className="page-title">Competitor Advantages vs {target}</div>

      {/* Executive Summary */}
      <div className="metric-grid" style={{ marginBottom:"1.5rem" }}>
        <MetricCard label="Total Advantages"       value={filtered.length}  sub={`of ${all.filter(a=>a.competitor!=="ASUS").length} total`} />
        <MetricCard label="High Impact"            value={highCount}        color="var(--red)"    sub="severity: High" />
        <MetricCard label="Competitor Brands Ahead" value={brandsAhead}     color="var(--yellow)" sub="brands outperforming" />
        <MetricCard label="Features Outperformed"  value={featuresHit}      color="#06b6d4"       sub="distinct features" />
      </div>

      {/* Active filter summary */}
      <div style={{ fontSize:"0.78rem", color:"var(--muted)", marginBottom:"1rem", display:"flex", gap:8, flexWrap:"wrap", alignItems:"center" }}>
        <span>Active filters:</span>
        <span style={{ background:"var(--surface2)", borderRadius:4, padding:"2px 8px" }}>Brand: {fBrand}</span>
        <span style={{ background:"var(--surface2)", borderRadius:4, padding:"2px 8px" }}>Severity: {fSev}</span>
        <span style={{ background:"var(--surface2)", borderRadius:4, padding:"2px 8px" }}>Type: {fType}</span>
        {(fBrand!=="All"||fSev!=="All"||fType!=="All") && (
          <button onClick={()=>{setFBrand("All");setFSev("All");setFType("All");}} style={{ background:"var(--red)", color:"#fff", border:"none", borderRadius:4, padding:"2px 8px", fontSize:"0.72rem", cursor:"pointer" }}>Clear</button>
        )}
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom:"1.5rem" }}>
        <div style={{ display:"flex", gap:24, flexWrap:"wrap" }}>
          <div>
            <div style={{ fontSize:"0.72rem", color:"var(--muted)", marginBottom:6, textTransform:"uppercase", letterSpacing:"0.05em" }}>Competitor Brand</div>
            <div style={{ display:"flex", gap:6, flexWrap:"wrap" }}>
              {brands.map(b => (
                <button key={b} onClick={()=>setFBrand(b)} style={{
                  padding:"5px 14px", borderRadius:6, fontSize:"0.8rem", cursor:"pointer",
                  background: fBrand===b ? (BC[b]||"var(--accent)") : "var(--surface2)",
                  color: fBrand===b ? "#fff" : "var(--muted)",
                  border:"1px solid "+(fBrand===b?"transparent":"var(--border)"),
                }}>{b}</button>
              ))}
            </div>
          </div>
          <div>
            <div style={{ fontSize:"0.72rem", color:"var(--muted)", marginBottom:6, textTransform:"uppercase", letterSpacing:"0.05em" }}>Severity</div>
            <div style={{ display:"flex", gap:6 }}>
              {sevs.map(s => {
                const sc = SEV[s];
                return <button key={s} onClick={()=>setFSev(s)} style={{
                  padding:"5px 14px", borderRadius:6, fontSize:"0.8rem", cursor:"pointer",
                  background: fSev===s ? (sc?.color||"var(--accent)") : "var(--surface2)",
                  color: fSev===s ? "#fff" : "var(--muted)",
                  border:"1px solid "+(fSev===s?"transparent":"var(--border)"),
                }}>{s}</button>;
              })}
            </div>
          </div>
          <div>
            <div style={{ fontSize:"0.72rem", color:"var(--muted)", marginBottom:6, textTransform:"uppercase", letterSpacing:"0.05em" }}>Advantage Type</div>
            <div style={{ display:"flex", gap:6, flexWrap:"wrap" }}>
              {types.map(t => (
                <button key={t} onClick={()=>setFType(t)} style={{
                  padding:"5px 14px", borderRadius:6, fontSize:"0.8rem", cursor:"pointer",
                  background: fType===t ? (TYPE_COLOR[t]||"var(--accent)") : "var(--surface2)",
                  color: fType===t ? "#fff" : "var(--muted)",
                  border:"1px solid "+(fType===t?"transparent":"var(--border)"),
                }}>{TYPE[t]||"All"}</button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="card"><p style={{ color:"var(--green)" }}>No advantages match the current filters.</p></div>
      ) : (
        <>
          {/* Feature frequency chart */}
          <div className="card" style={{ marginBottom:"1.5rem" }}>
            <div className="section-title">Features Where Competitors Beat {target}</div>
            <p style={{ fontSize:"0.78rem", color:"var(--muted)", marginBottom:"0.75rem" }}>Number of competitor models outperforming ASUS per feature, stacked by severity.</p>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={featChart} margin={{ bottom:10 }}>
                <XAxis dataKey="feature" tick={{ fill:"#94a3b8", fontSize:11 }} />
                <YAxis tick={{ fill:"#94a3b8" }} allowDecimals={false} />
                <Tooltip contentStyle={{ background:"#ffffff", border:"1px solid #e2e8f0" }} />
                <Legend />
                <Bar dataKey="High"   stackId="a" fill="#ef4444" radius={[0,0,0,0]} />
                <Bar dataKey="Medium" stackId="a" fill="#f59e0b" radius={[0,0,0,0]} />
                <Bar dataKey="Low"    stackId="a" fill="#22c55e" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Grouped cards */}
          {Object.entries(grouped).map(([brand, matchups]) => (
            <div key={brand} style={{ marginBottom:"1.5rem" }}>
              {/* Brand header */}
              <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:"0.75rem" }}>
                <span style={{ width:12, height:12, borderRadius:3, background:BC[brand]||"#6366f1", display:"inline-block" }} />
                <span style={{ fontWeight:700, color:BC[brand]||"var(--text)", fontSize:"1.05rem" }}>{brand}</span>
                <span style={{ fontSize:"0.78rem", color:"var(--muted)" }}>{matchups.reduce((s,m)=>s+m.items.length,0)} advantages across {matchups.length} matchup{matchups.length>1?"s":""}</span>
                <span style={{ marginLeft:"auto", background:"#fee2e2", color:"#b91c1c", borderRadius:4, padding:"2px 8px", fontSize:"0.72rem", fontWeight:700 }}>
                  {matchups.reduce((s,m)=>s+m.items.filter(x=>x.severity==="High").length,0)} High
                </span>
              </div>

              {/* Top 3 critical per brand callout */}
              {(() => {
                const top3 = matchups.flatMap(m=>m.items).filter(a=>a.severity==="High").slice(0,3);
                if (!top3.length) return null;
                return (
                  <div style={{ background:"#ffffff", border:"1px solid var(--border)", borderLeft:"3px solid #dc2626", borderRadius:8, padding:"10px 14px", marginBottom:"0.75rem" }}>
                    <div style={{ fontSize:"0.72rem", color:"#dc2626", fontWeight:700, marginBottom:6, textTransform:"uppercase" }}>Top Critical Advantages</div>
                    {top3.map((a,i) => (
                      <div key={i} style={{ fontSize:"0.82rem", color:"var(--text)", marginBottom:4 }}>
                        <span style={{ color:"#dc2626" }}>▶ </span>
                        <span style={{ fontWeight:600 }}>{a.competitor_model}</span>
                        <span style={{ color:"var(--muted)" }}> vs {a.target_model} — </span>
                        <span>{TYPE[a.adv_type]||a.adv_type} · {a.detail}</span>
                      </div>
                    ))}
                  </div>
                );
              })()}

              {/* Matchup cards */}
              {matchups.map((mu, mi) => {
                const key = brand+"-"+mi;
                const isOpen = expanded[key];
                const highN = mu.items.filter(x=>x.severity==="High").length;
                return (
                  <div key={mi} className="card" style={{ marginBottom:"0.6rem", borderLeft:"3px solid "+(BC[brand]||"#6366f1") }}>
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                      <div>
                        <span style={{ fontWeight:700, color:BC[brand]||"var(--text)" }}>{mu.competitor_model}</span>
                        <span style={{ color:"var(--muted)", fontSize:"0.82rem" }}> vs </span>
                        <span style={{ fontWeight:600, color:"var(--accent2)" }}>{mu.target_model}</span>
                        <span style={{ marginLeft:10, fontSize:"0.78rem", color:"var(--muted)" }}>{mu.items.length} advantage{mu.items.length>1?"s":""}</span>
                        {highN > 0 && <span style={{ marginLeft:6, background:"#fee2e2", color:"#b91c1c", borderRadius:4, padding:"1px 6px", fontSize:"0.7rem", fontWeight:700 }}>{highN} High</span>}
                      </div>
                      <button onClick={()=>setExpanded(p=>({...p,[key]:!p[key]}))} style={{ background:"var(--surface2)", border:"1px solid var(--border)", color:"var(--muted)", borderRadius:6, padding:"3px 10px", fontSize:"0.78rem", cursor:"pointer" }}>
                        {isOpen?"▲ Hide":"▼ Show"}
                      </button>
                    </div>

                    {isOpen && (
                      <div style={{ marginTop:"0.75rem" }}>
                        {mu.items.map((a, ai) => (
                          <div key={ai} style={{
                            display:"flex", justifyContent:"space-between", alignItems:"flex-start",
                            padding:"8px 10px", borderRadius:6, marginBottom:4,
                            background:"#ffffff",
                            border:"1px solid var(--border)",
                            borderLeft:"3px solid "+(SEV[a.severity]?.color||"var(--muted)"),
                          }}>
                            <div style={{ flex:1 }}>
                              <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:3 }}>
                                <span style={{ fontSize:"0.82rem", color:TYPE_COLOR[a.adv_type]||"var(--text)", fontWeight:600 }}>
                                  {TYPE[a.adv_type]||a.adv_type}
                                </span>
                                <span style={{ fontSize:"0.78rem", color:"var(--muted)" }}>· {a.advantage}</span>
                              </div>
                              <div style={{ fontSize:"0.8rem", color:"var(--text)" }}>{a.detail}</div>
                            </div>
                            <div style={{ display:"flex", flexDirection:"column", alignItems:"flex-end", gap:4, marginLeft:12 }}>
                              <SevBadge sev={a.severity} />
                              {a.metric && <span style={{ fontSize:"0.78rem", color:SEV[a.severity]?.color||"var(--muted)", fontWeight:700 }}>{a.metric}</span>}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </>
      )}
    </div>
  );
}