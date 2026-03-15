"""
Insights Engine — AI-powered competitor intelligence.
Derives spec-based competitor discovery and similarity scoring
from the existing model_groups / model_prices data (no external notebook required).
"""

import re
import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model_groups import GROUPS, get_spec_peers, get_group_label, get_brand
from model_prices import get_price_rating, MODEL_PRICE_RATING

# ── Spec catalogue (representative specs per model) ───────────────────────────
# Tier: 1=budget, 2=mid, 3=high-end, 4=flagship
MODEL_SPECS = {
    # ASUS
    "ASUS VivoBook 15 X1502ZA":    {"cpu_tier":2,"ram":8, "gpu":"integrated","battery":42,"display":15.6,"price_tier":1},
    "ASUS VivoBook Go 15 E1504FA": {"cpu_tier":1,"ram":8, "gpu":"integrated","battery":42,"display":15.6,"price_tier":1},
    "ASUS VivoBook 16 X1605":      {"cpu_tier":2,"ram":8, "gpu":"integrated","battery":42,"display":16.0,"price_tier":1},
    "ASUS ZenBook 14 OLED":        {"cpu_tier":3,"ram":16,"gpu":"integrated","battery":75,"display":14.0,"price_tier":2},
    "ASUS TUF F15 FX506":          {"cpu_tier":2,"ram":8, "gpu":"rtx3050","battery":56,"display":15.6,"price_tier":2},
    "ASUS TUF A15 FA506":          {"cpu_tier":2,"ram":8, "gpu":"rtx3050","battery":56,"display":15.6,"price_tier":2},
    "ASUS TUF F15 FX507":          {"cpu_tier":3,"ram":16,"gpu":"rtx4060","battery":56,"display":15.6,"price_tier":3},
    "ASUS ROG Strix G15":          {"cpu_tier":3,"ram":16,"gpu":"rtx4060","battery":90,"display":15.6,"price_tier":3},
    "ASUS ROG Zephyrus G14":       {"cpu_tier":4,"ram":16,"gpu":"rtx4070","battery":76,"display":14.0,"price_tier":4},
    "ASUS ROG Strix Scar 15":      {"cpu_tier":4,"ram":32,"gpu":"rtx4080","battery":90,"display":15.6,"price_tier":4},
    # HP
    "HP 15s":                      {"cpu_tier":1,"ram":8, "gpu":"integrated","battery":41,"display":15.6,"price_tier":1},
    "HP Pavilion 15":              {"cpu_tier":2,"ram":8, "gpu":"integrated","battery":41,"display":15.6,"price_tier":1},
    "HP Pavilion Aero":            {"cpu_tier":2,"ram":8, "gpu":"integrated","battery":43,"display":13.3,"price_tier":2},
    "HP Victus 16":                {"cpu_tier":2,"ram":8, "gpu":"rtx3050","battery":70,"display":16.1,"price_tier":2},
    "HP Omen 17":                  {"cpu_tier":3,"ram":16,"gpu":"rtx4060","battery":83,"display":17.3,"price_tier":3},
    "HP Omen Transcend 14":        {"cpu_tier":3,"ram":16,"gpu":"rtx4060","battery":68,"display":14.0,"price_tier":3},
    # Dell
    "Dell Inspiron 3520":          {"cpu_tier":1,"ram":8, "gpu":"integrated","battery":41,"display":15.6,"price_tier":1},
    "Dell Inspiron 5430":          {"cpu_tier":2,"ram":16,"gpu":"integrated","battery":54,"display":14.0,"price_tier":2},
    "Dell Inspiron 7430":          {"cpu_tier":3,"ram":16,"gpu":"integrated","battery":54,"display":14.0,"price_tier":2},
    "Dell Vostro 3530":            {"cpu_tier":1,"ram":8, "gpu":"integrated","battery":41,"display":15.6,"price_tier":1},
    "Dell G16":                    {"cpu_tier":3,"ram":16,"gpu":"rtx4060","battery":86,"display":16.0,"price_tier":3},
    "Dell Alienware m16 R2":       {"cpu_tier":4,"ram":32,"gpu":"rtx4080","battery":86,"display":16.0,"price_tier":4},
    # Lenovo
    "Lenovo IdeaPad 3":            {"cpu_tier":1,"ram":8, "gpu":"integrated","battery":45,"display":15.6,"price_tier":1},
    "Lenovo IdeaPad Slim 3":       {"cpu_tier":1,"ram":8, "gpu":"integrated","battery":45,"display":15.6,"price_tier":1},
    "Lenovo IdeaPad Slim 5":       {"cpu_tier":2,"ram":16,"gpu":"integrated","battery":56,"display":14.0,"price_tier":2},
    "Lenovo IdeaPad Gaming 3":     {"cpu_tier":2,"ram":8, "gpu":"rtx3050","battery":45,"display":15.6,"price_tier":2},
    "Lenovo LOQ":                  {"cpu_tier":3,"ram":16,"gpu":"rtx4060","battery":60,"display":15.6,"price_tier":3},
    "Lenovo Legion 5":             {"cpu_tier":3,"ram":16,"gpu":"rtx4060","battery":80,"display":15.6,"price_tier":3},
    "Lenovo Legion Slim 7":        {"cpu_tier":4,"ram":16,"gpu":"rtx4070","battery":99,"display":16.0,"price_tier":4},
    "Lenovo Yoga Slim 6":          {"cpu_tier":2,"ram":16,"gpu":"integrated","battery":75,"display":14.0,"price_tier":2},
}

SPEC_KEYS = ["cpu_tier","ram","gpu","battery","display","price_tier"]
GPU_TIER  = {"integrated":0,"rtx3050":1,"rtx4060":2,"rtx4070":3,"rtx4080":4}


def _get_specs(model_name: str) -> dict | None:
    """Fuzzy-match model name to spec catalogue."""
    norm = model_name.lower().strip()
    for k, v in MODEL_SPECS.items():
        if k.lower() == norm:
            return v
    # partial match — longest key that is a substring
    best, best_len = None, 0
    for k, v in MODEL_SPECS.items():
        kl = k.lower()
        if kl in norm or norm in kl:
            if len(kl) > best_len:
                best, best_len = v, len(kl)
    return best


def _spec_similarity(s1: dict, s2: dict) -> float:
    """Return 0-100 similarity score between two spec dicts."""
    if not s1 or not s2:
        return 0.0
    score = 0
    weights = {"cpu_tier":25,"ram":20,"gpu":25,"battery":10,"display":10,"price_tier":10}
    for key, w in weights.items():
        v1, v2 = s1.get(key), s2.get(key)
        if v1 is None or v2 is None:
            continue
        if key == "gpu":
            t1, t2 = GPU_TIER.get(v1,0), GPU_TIER.get(v2,0)
            diff = abs(t1 - t2)
            score += w * max(0, 1 - diff / 4)
        elif key in ("ram","battery","display"):
            mx = max(v1, v2) or 1
            score += w * (1 - abs(v1 - v2) / mx)
        else:
            score += w if v1 == v2 else w * max(0, 1 - abs(v1 - v2) / 3)
    return round(score, 1)


def competitor_analysis(asus_model_name: str) -> dict:
    """
    Return AI-powered competitor intelligence for a given ASUS model.
    """
    asus_specs = _get_specs(asus_model_name)
    asus_pr    = get_price_rating(asus_model_name)

    # Discover competitor models via spec peers
    raw_peers = get_spec_peers(asus_model_name)
    group_label = get_group_label(asus_model_name)

    ranked = []
    for peer in raw_peers:
        p_name  = peer["model"]
        p_brand = peer["brand"]
        p_specs = _get_specs(p_name)
        p_pr    = get_price_rating(p_name)
        sim     = _spec_similarity(asus_specs, p_specs)

        spec_diff = {}
        if asus_specs and p_specs:
            for k in SPEC_KEYS:
                av, pv = asus_specs.get(k), p_specs.get(k)
                if av is not None and pv is not None and av != pv:
                    spec_diff[k] = {"asus": av, "competitor": pv}

        price_diff = None
        if asus_pr["price"] and p_pr["price"]:
            price_diff = p_pr["price"] - asus_pr["price"]  # negative = competitor cheaper

        ranked.append({
            "model":       p_name,
            "brand":       p_brand,
            "match_score": sim,
            "price":       p_pr["price"],
            "rating":      p_pr["rating"],
            "price_diff":  price_diff,
            "spec_diff":   spec_diff,
            "specs":       p_specs,
        })

    ranked.sort(key=lambda x: -x["match_score"])

    return {
        "asus_model":   asus_model_name,
        "asus_specs":   asus_specs,
        "asus_price":   asus_pr["price"],
        "asus_rating":  asus_pr["rating"],
        "group":        group_label,
        "competitors":  ranked,
    }


def generate_insights(asus_model_name: str, model_aspects: list | None = None) -> list:
    """
    Generate strategic insight cards combining spec analysis + review sentiment.
    Returns a list of insight dicts: { type, title, body, severity }
    """
    analysis = competitor_analysis(asus_model_name)
    insights = []

    asus_specs = analysis["asus_specs"] or {}
    asus_price = analysis["asus_price"]

    for comp in analysis["competitors"][:6]:
        name  = comp["model"]
        brand = comp["brand"]
        score = comp["match_score"]
        diff  = comp.get("spec_diff", {})
        pdiff = comp.get("price_diff")

        # Closest competitor threat
        if score >= 80:
            insights.append({
                "type":     "threat",
                "title":    f"Competitor Threat — {name}",
                "body":     f"{name} is a close competitor to {asus_model_name} with a {score:.0f}% spec match.",
                "severity": "High" if score >= 90 else "Medium",
                "brand":    brand,
            })

        # Price insight
        if pdiff is not None and pdiff <= -3000:
            insights.append({
                "type":     "price",
                "title":    f"Price Insight — {name}",
                "body":     f"{name} is ₹{abs(pdiff):,} cheaper than {asus_model_name} (₹{comp['price']:,} vs ₹{asus_price:,}) while offering similar specs.",
                "severity": "High" if abs(pdiff) >= 10000 else "Medium",
                "brand":    brand,
            })

        # Feature gap — RAM
        if "ram" in diff:
            av, pv = diff["ram"]["asus"], diff["ram"]["competitor"]
            if pv > av:
                insights.append({
                    "type":     "gap",
                    "title":    f"Feature Gap — RAM ({name})",
                    "body":     f"{name} offers {pv}GB RAM while {asus_model_name} offers {av}GB.",
                    "severity": "Medium",
                    "brand":    brand,
                })

        # Feature gap — Battery
        if "battery" in diff:
            av, pv = diff["battery"]["asus"], diff["battery"]["competitor"]
            if pv > av + 10:
                insights.append({
                    "type":     "gap",
                    "title":    f"Feature Gap — Battery ({name})",
                    "body":     f"{name} has a larger battery ({pv}Wh vs {av}Wh for {asus_model_name}).",
                    "severity": "Low",
                    "brand":    brand,
                })

        # Hardware advantage for ASUS
        if "gpu" in diff:
            av, pv = diff["gpu"]["asus"], diff["gpu"]["competitor"]
            if GPU_TIER.get(av, 0) > GPU_TIER.get(pv, 0):
                insights.append({
                    "type":     "advantage",
                    "title":    f"ASUS Hardware Advantage — GPU vs {name}",
                    "body":     f"{asus_model_name} has a stronger GPU ({av}) compared to {name} ({pv}).",
                    "severity": "Low",
                    "brand":    brand,
                })

    # Sentiment-based weakness insights
    if model_aspects:
        for asp_row in model_aspects:
            if asp_row.get("neg_ratio", 0) >= 25:
                asp = asp_row["aspect"]
                # Check if any competitor has lower neg_ratio for same aspect
                insights.append({
                    "type":     "weakness",
                    "title":    f"Weakness — {asp.capitalize()} ({asus_model_name})",
                    "body":     f"{asus_model_name} has {asp_row['neg_ratio']:.0f}% negative {asp} reviews. Consider investigating competitor offerings in this area.",
                    "severity": "High" if asp_row["neg_ratio"] >= 35 else "Medium",
                    "brand":    "ASUS",
                })

    # Deduplicate by title
    seen, unique = set(), []
    for ins in insights:
        if ins["title"] not in seen:
            seen.add(ins["title"])
            unique.append(ins)

    return unique
