import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Chatbot from "./components/Chatbot";
import Home from "./pages/Home";
import TargetOverview from "./pages/TargetOverview";
import MarketOverview from "./pages/MarketOverview";
import CompetitorComparison from "./pages/CompetitorComparison";
import CompetitorAdvantages from "./pages/CompetitorAdvantages";
import StrengthsWeaknesses from "./pages/StrengthsWeaknesses";
import Strategy from "./pages/Strategy";
import Opportunities from "./pages/Opportunities";
import Insights from "./pages/Insights";
import { getBrands } from "./api";

export default function App() {
  const [brands, setBrands] = useState(["ASUS", "HP", "Dell", "Lenovo"]);
  const [target, setTarget] = useState("ASUS");

  useEffect(() => {
    getBrands().then(r => {
      if (r.data.brands.length) setBrands(r.data.brands);
    }).catch(() => {});
  }, []);

  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar target={target} setTarget={setTarget} brands={brands} />
        <main style={{ flex: 1, padding: "2rem", overflowY: "auto" }}>
          <Routes>
            <Route path="/"              element={<Home target={target} />} />
            <Route path="/target"        element={<TargetOverview target={target} />} />
            <Route path="/market"        element={<MarketOverview />} />
            <Route path="/comparison"    element={<CompetitorComparison target={target} />} />
            <Route path="/advantages"    element={<CompetitorAdvantages target={target} />} />
            <Route path="/strengths"     element={<StrengthsWeaknesses target={target} />} />
            <Route path="/strategy"      element={<Strategy target={target} />} />
            <Route path="/opportunities" element={<Opportunities />} />
            <Route path="/insights"      element={<Insights target={target} />} />
          </Routes>
        </main>
        <Chatbot />
      </div>
    </BrowserRouter>
  );
}
