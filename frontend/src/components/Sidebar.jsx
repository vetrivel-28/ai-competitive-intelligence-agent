import { NavLink } from "react-router-dom";

const NAV = [
  { to: "/",              label: "Home" },
  { to: "/target",        label: "Target Overview" },
  { to: "/market",        label: "Market Overview" },
  { to: "/comparison",    label: "Competitor Comparison" },
  { to: "/advantages",    label: "Competitor Advantages" },
  { to: "/strengths",     label: "Strengths & Weaknesses" },
  { to: "/strategy",      label: "Strategy" },
  { to: "/opportunities", label: "Market Opportunities" },
  { to: "/insights",      label: "Insights" },
];

export default function Sidebar({ target, setTarget, brands }) {
  return (
    <aside style={{
      width: 230, minHeight: "100vh", background: "var(--surface)",
      borderRight: "1px solid var(--border)", display: "flex",
      flexDirection: "column", padding: "1.25rem 0",
    }}>
      <div style={{ padding: "0 1.25rem 1.25rem", borderBottom: "1px solid var(--border)" }}>
        <div style={{ fontSize: "1rem", fontWeight: 700, color: "var(--accent2)", marginBottom: 10 }}>
          Laptop Intel
        </div>
        <label style={{ fontSize: "0.72rem", color: "var(--muted)", display: "block", marginBottom: 4 }}>
          Target Company
        </label>
        <select value={target} onChange={e => setTarget(e.target.value)}
          style={{ width: "100%" }}>
          {brands.map(b => <option key={b}>{b}</option>)}
        </select>
      </div>

      <nav style={{ flex: 1, padding: "0.75rem 0" }}>
        {NAV.map(({ to, label }) => (
          <NavLink key={to} to={to} end={to === "/"}
            style={({ isActive }) => ({
              display: "flex", alignItems: "center", gap: 10,
              padding: "0.55rem 1.25rem", fontSize: "0.88rem",
              color: isActive ? "var(--accent2)" : "var(--muted)",
              background: isActive ? "var(--surface2)" : "transparent",
              borderLeft: isActive ? "3px solid var(--accent)" : "3px solid transparent",
              transition: "all 0.15s",
            })}>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
