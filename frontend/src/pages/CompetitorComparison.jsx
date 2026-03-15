import { useEffect, useState } from "react";
import { getModelComparison } from "../api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis, Legend } from "recharts";

const BC = { ASUS:"#6366f1", HP:"#22c55e", Dell:"#f59e0b", Lenovo:"#06b6d4" };
const ASPS = ["performance","battery","display","thermal","keyboard","design","price","graphics","ram","storage"];
const AL = { performance:"Performance", battery:"Battery", display:"Display", thermal:"Thermal", keyboard:"Keyboard", design:"Design", price:"Price", graphics:"Graphics", ram:"RAM", storage:"Storage" };
const ASUS_MODELS = ["ASUS VivoBook 15 X1502ZA","ASUS VivoBook Go 15 E1504FA","ASUS VivoBook 16 X1605","ASUS ZenBook 14 OLED","ASUS TUF F15 FX506","ASUS TUF A15 FA506","ASUS TUF F15 FX507","ASUS ROG Strix G15","ASUS ROG Zephyrus G14","ASUS ROG Strix Scar 15"];
const sn = n => n.replace(/^(ASUS|HP|Dell|Lenovo)\s+/i,"");
const fmt = v => v != null ? "Rs."+Number(v).toLocaleString("en-IN") : "--";
const ADV_TYPE_LABEL = { price:"Price", rating:"Rating", feature:"Feature", complaint:"Complaint" };

export default function CompetitorComparison({ target }) {
  const [sel, setSel]         = useState("ASUS ROG Strix G15");
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr]         = useState(null);
  const [open, setOpen]       = useState({});

  useEffect(() => {
    setLoading(true); setErr(null); setData(null);
    getModelComparison(sel)
      .then(r => { setData(r.data); setLoading(false); })
      .catch(e => { setErr("API error: " + e.message); setLoading(false); });
  }, [sel]);

  const ms   = data?.models || [];
  const asus = ms.find(m => m.is_target);
  const comp = ms.filter(m => !m.is_target);
  const pc   = ms.map(m => ({ name:sn(m.model), fullName:m.model, price:m.price,  brand:m.brand }));
  const rc   = ms.map(m => ({ name:sn(m.model), fullName:m.model, rating:m.rating, brand:m.brand }));

  const radar = ASPS.map(a => {
    const row = { aspect: AL[a] };
    ms.forEach(m => { row[m.brand+(m.is_target?" *":"")] = m.aspects[a]?.pos_ratio ?? 0; });
    return row;
  });

  const adv = [];
  if (asus) {
    comp.forEach(c => {
      if (c.price && asus.price && asus.price - c.price >= 3000)
        adv.push({ type:"price", brand:c.brand, text:c.model+" -- Rs."+(asus.price-c.price).toLocaleString("en-IN")+" cheaper than "+asus.model });
      if (c.rating && asus.rating && c.rating - asus.rating >= 0.2)
        adv.push({ type:"rating", brand:c.brand, text:c.model+" -- Rated "+(c.rating-asus.rating).toFixed(1)+" pts higher ("+c.rating+" vs "+asus.rating+")" });
      ASPS.forEach(a => {
        const ca=c.aspects[a], ta=asus.aspects[a];
        if (!ca||!ta) return;
        if (ca.pos_ratio-ta.pos_ratio>=15) adv.push({ type:"feature",   brand:c.brand, text:c.model+" -- Better "+a+" ("+ca.pos_ratio+"% vs "+ta.pos_ratio+"% positive)" });
        if (ta.neg_ratio-ca.neg_ratio>=15) adv.push({ type:"complaint", brand:c.brand, text:c.model+" -- Fewer "+a+" complaints ("+ca.neg_ratio+"% vs "+ta.neg_ratio+"%)" });
      });
    });
  }

  return (
    <div>
      <div className="page-title">Competitor Comparison -- {target} vs Spec-Matched Rivals</div>

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

      {loading && <div style={{ color:"var(--muted)", padding:"3rem", textAlign:"center" }}>Loading comparison data...</div>}
      {err     && <div style={{ color:"var(--red)", padding:"1rem", background:"var(--surface)", borderRadius:8 }}>{err}</div>}

      {!loading && !err && data && ms.length > 0 && (
        <div>
          <div className="card" style={{ marginBottom:"1.5rem" }}>
            <div style={{ display:"flex", alignItems:"center", gap:12, flexWrap:"wrap" }}>
              <div style={{ background:BC.ASUS+"22", border:"1px solid "+BC.ASUS, borderRadius:8, padding:"10px 16px" }}>
                <div style={{ fontSize:"0.72rem", color:"var(--muted)" }}>Target Model</div>
                <div style={{ color:BC.ASUS, fontWeight:700 }}>{data.asus_model}</div>
                <div style={{ fontSize:"0.75rem", color:"var(--muted)" }}>{data.group}</div>
                {asus?.price && <div style={{ fontSize:"0.78rem", color:"var(--muted)", marginTop:2 }}>{fmt(asus.price)} -- {asus.rating}</div>}
              </div>
              <div style={{ color:"var(--muted)", fontSize:"1.4rem" }}>vs</div>
              {comp.map(c => (
                <div key={c.model} style={{ background:BC[c.brand]+"22", border:"1px solid "+BC[c.brand], borderRadius:8, padding:"10px 16px" }}>
                  <div style={{ fontSize:"0.72rem", color:"var(--muted)" }}>{c.brand}</div>
                  <div style={{ color:BC[c.brand], fontWeight:600 }}>{c.model}</div>
                  {c.price && <div style={{ fontSize:"0.78rem", color:"var(--muted)", marginTop:2 }}>{fmt(c.price)} -- {c.rating}</div>}
                </div>
              ))}
            </div>
          </div>

          <div className="grid-2" style={{ marginBottom:"1.5rem" }}>
            <div className="card">
              <div className="section-title">Price Comparison</div>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={pc} margin={{ bottom:50 }}>
                  <XAxis dataKey="name" tick={{ fontSize:10, fill:"#94a3b8" }} angle={-30} textAnchor="end" interval={0} />
                  <YAxis tick={{ fill:"#94a3b8" }} tickFormatter={v=>"Rs."+(v/1000).toFixed(0)+"k"} />
                  <Tooltip formatter={(v,n,p)=>["Rs."+Number(v).toLocaleString("en-IN"), p.payload.fullName]} contentStyle={{ background:"#ffffff", border:"1px solid #e2e8f0" }} />
                  <Bar dataKey="price" radius={[4,4,0,0]}>
                    {pc.map((e,i) => <Cell key={i} fill={BC[e.brand]||"#6366f1"} opacity={e.brand==="ASUS"?1:0.7} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="card">
              <div className="section-title">Rating Comparison</div>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={rc} margin={{ bottom:50 }}>
                  <XAxis dataKey="name" tick={{ fontSize:10, fill:"#94a3b8" }} angle={-30} textAnchor="end" interval={0} />
                  <YAxis tick={{ fill:"#94a3b8" }} domain={[3.5,5]} tickCount={4} />
                  <Tooltip formatter={(v,n,p)=>[v, p.payload.fullName]} contentStyle={{ background:"#ffffff", border:"1px solid #e2e8f0" }} />
                  <Bar dataKey="rating" radius={[4,4,0,0]}>
                    {rc.map((e,i) => <Cell key={i} fill={BC[e.brand]||"#6366f1"} opacity={e.brand==="ASUS"?1:0.7} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card" style={{ marginBottom:"1.5rem" }}>
            <div className="section-title">Feature Sentiment Radar</div>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radar}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="aspect" tick={{ fill:"#94a3b8", fontSize:11 }} />
                {ms.map(m => {
                  const k = m.brand+(m.is_target?" *":"");
                  return <Radar key={k} name={k} dataKey={k} stroke={BC[m.brand]} fill={BC[m.brand]} fillOpacity={m.is_target?0.25:0.1} strokeWidth={m.is_target?2:1} />;
                })}
                <Legend />
                <Tooltip contentStyle={{ background:"#ffffff", border:"1px solid #e2e8f0" }} formatter={(v,n)=>[v+"% positive",n]} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div className="card" style={{ marginBottom:"1.5rem" }}>
            <div className="section-title">Feature Strength -- % Positive Reviews</div>
            <div style={{ overflowX:"auto" }}>
              <table>
                <thead><tr><th>Feature</th>{ms.map(m=><th key={m.model} style={{ color:BC[m.brand] }}>{m.is_target?"* ":""}{m.brand}</th>)}</tr></thead>
                <tbody>
                  {ASPS.map(a => {
                    const vals=ms.map(m=>m.aspects[a]?.pos_ratio??null);
                    const max=Math.max(...vals.filter(v=>v!==null));
                    return <tr key={a}><td style={{ color:"var(--muted)", fontSize:"0.82rem" }}>{AL[a]}</td>
                      {ms.map(m=>{ const v=m.aspects[a]?.pos_ratio; return <td key={m.model} style={{ color:v===null?"var(--muted)":v===max?"var(--green)":"var(--text)", fontWeight:v===max?700:400, background:m.is_target?"var(--surface2)":"transparent" }}>{v!=null?v+"%":"--"}</td>; })}
                    </tr>;
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card" style={{ marginBottom:"1.5rem" }}>
            <div className="section-title">Complaint Rate -- % Negative Reviews</div>
            <div style={{ overflowX:"auto" }}>
              <table>
                <thead><tr><th>Feature</th>{ms.map(m=><th key={m.model} style={{ color:BC[m.brand] }}>{m.is_target?"* ":""}{m.brand}</th>)}</tr></thead>
                <tbody>
                  {ASPS.map(a => {
                    const vals=ms.map(m=>m.aspects[a]?.neg_ratio??null);
                    const max=Math.max(...vals.filter(v=>v!==null));
                    return <tr key={a}><td style={{ color:"var(--muted)", fontSize:"0.82rem" }}>{AL[a]}</td>
                      {ms.map(m=>{ const v=m.aspects[a]?.neg_ratio; return <td key={m.model} style={{ color:v===null?"var(--muted)":v===max&&max>0?"var(--red)":"var(--text)", fontWeight:v===max&&max>0?700:400, background:m.is_target?"var(--surface2)":"transparent" }}>{v!=null?v+"%":"--"}</td>; })}
                    </tr>;
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="section-title">Model Review Insights</div>
          <div style={{ marginBottom:"1.5rem" }}>
            {ms.map(m => {
              const str=ASPS.filter(a=>m.aspects[a]?.pos_ratio>=50).sort((a,b)=>(m.aspects[b]?.pos_ratio??0)-(m.aspects[a]?.pos_ratio??0)).slice(0,3);
              const wk=ASPS.filter(a=>m.aspects[a]?.neg_ratio>=20).sort((a,b)=>(m.aspects[b]?.neg_ratio??0)-(m.aspects[a]?.neg_ratio??0)).slice(0,3);
              return (
                <div key={m.model} className="card" style={{ marginBottom:"0.75rem", borderLeft:"3px solid "+BC[m.brand] }}>
                  <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                    <div>
                      <span style={{ fontWeight:600, color:BC[m.brand] }}>{m.is_target?"* ":""}{m.model}</span>
                      {m.price  && <span style={{ marginLeft:12, color:"var(--muted)", fontSize:"0.82rem" }}>{fmt(m.price)}</span>}
                      {m.rating && <span style={{ marginLeft:8,  color:"#fbbf24",      fontSize:"0.82rem" }}>* {m.rating}</span>}
                    </div>
                    <button onClick={()=>setOpen(p=>({...p,[m.model]:!p[m.model]}))} style={{ background:"var(--surface2)", border:"1px solid var(--border)", color:"var(--muted)", borderRadius:6, padding:"3px 10px", fontSize:"0.78rem", cursor:"pointer" }}>
                      {open[m.model]?"Hide":"Details"}
                    </button>
                  </div>
                  {open[m.model] && (
                    <div className="grid-2" style={{ marginTop:"1rem" }}>
                      <div>
                        <div style={{ fontSize:"0.78rem", color:"var(--green)", marginBottom:6 }}>Strengths</div>
                        {str.length===0?<p className="empty" style={{ fontSize:"0.8rem" }}>No strong signals</p>
                          :str.map(a=><div key={a} style={{ fontSize:"0.82rem", marginBottom:4 }}><span style={{ color:"var(--text)" }}>{AL[a]}</span><span style={{ color:"var(--green)", marginLeft:8 }}>{m.aspects[a].pos_ratio}% positive</span></div>)}
                      </div>
                      <div>
                        <div style={{ fontSize:"0.78rem", color:"var(--red)", marginBottom:6 }}>Weaknesses</div>
                        {wk.length===0?<p className="empty" style={{ fontSize:"0.8rem" }}>No major complaints</p>
                          :wk.map(a=><div key={a} style={{ fontSize:"0.82rem", marginBottom:4 }}><span style={{ color:"var(--text)" }}>{AL[a]}</span><span style={{ color:"var(--red)", marginLeft:8 }}>{m.aspects[a].neg_ratio}% complaints</span></div>)}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="card">
            <div className="section-title">Competitor Advantage Summary</div>
            {adv.length===0
              ?<p className="empty">No significant competitor advantages detected.</p>
              :adv.map((a,i)=>(
                <div key={i} className="adv-card" style={{ borderLeftColor:BC[a.brand]||"var(--red)", marginBottom:"0.5rem" }}>
                  <span style={{ marginRight:4 }}>{ADV_TYPE_LABEL[a.type]}</span>
                  <span style={{ fontSize:"0.85rem", color:"var(--text)" }}>{a.text}</span>
                </div>
              ))
            }
          </div>
        </div>
      )}

      {!loading && !err && (!data || ms.length===0) && (
        <div style={{ color:"var(--muted)", padding:"3rem", textAlign:"center" }}>
          No data. Make sure the API is running on port 8000.
        </div>
      )}
    </div>
  );
}