"""
FastAPI backend — serves all analysis data as REST endpoints.
Run with: uvicorn api.main:app --reload --port 8000
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import glob
import os
import sys
import re
from collections import defaultdict
from dotenv import load_dotenv

# Load .env from project root (one level up from api/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
from model_prices import get_price_rating, MODEL_PRICE_RATING
from model_groups import get_spec_peers, get_group_label, get_brand, GROUPS

from contextlib import asynccontextmanager

# ── RAG model setup ───────────────────────────────────────────────────────────
RAG_DIR = os.path.join(os.path.dirname(__file__), "..", "rag_model_ai")
sys.path.insert(0, os.path.abspath(RAG_DIR))

_rag_ready = False
_rag_df = None
_rag_index = None
_rag_embed = None

def _init_rag():
    global _rag_ready, _rag_df, _rag_index, _rag_embed
    if _rag_ready:
        return
    try:
        import rag_model as rm
        # Point the RAG model at the correct data dir (relative to rag_model_ai/)
        data_dir = os.path.join(os.path.abspath(RAG_DIR), "reddit_vader_results", "reddit_vader_results")
        cache_file = os.path.join(os.path.abspath(RAG_DIR), "rag_cache.pkl")
        # Temporarily patch constants so the module uses absolute paths
        orig_data = rm.DATA_DIR
        orig_cache = rm.CACHE_FILE
        rm.DATA_DIR   = data_dir
        rm.CACHE_FILE = cache_file
        from sentence_transformers import SentenceTransformer
        _rag_df    = rm.load_dataset(data_dir)
        _rag_embed = SentenceTransformer("all-MiniLM-L6-v2")
        _rag_index, _ = rm.build_index(_rag_df, _rag_embed)
        rm.DATA_DIR   = orig_data
        rm.CACHE_FILE = orig_cache
        _rag_ready = True
        print("RAG model ready.")
    except Exception as e:
        print(f"RAG init failed: {e}")

@asynccontextmanager
async def lifespan(app):
    load_all()   # warm cache at startup
    _init_rag()  # load RAG model
    yield

app = FastAPI(title="Laptop Intelligence API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Constants ─────────────────────────────────────────────────────────────────
AMAZON_DIR = "amazon_final_files"
REDDIT_DIR = "reddit_vader_results/reddit_vader_results"
BRAND_PREFIXES = ["ASUS", "HP", "Dell", "Lenovo", "Apple", "MSI", "Acer"]

ASPECT_KEYWORDS = {
    "performance": ["performance","fast","speed","smooth","lag","gaming","processor","cpu","amd","intel","fps","powerful"],
    "battery":     ["battery","backup","charging","charge","drain"],
    "display":     ["display","screen","brightness","refresh","resolution","fhd","144hz","panel"],
    "price":       ["price","cost","expensive","cheap","value","money","deal","worth"],
    "design":      ["design","build","look","stylish","weight","portable","body","plastic","premium"],
    "keyboard":    ["keyboard","keys","typing","trackpad","touchpad"],
    "audio":       ["speaker","speakers","audio","sound","mic"],
    "camera":      ["camera","webcam"],
    "thermal":     ["heat","heating","temperature","thermal","fan","cooling","hot"],
    "storage":     ["ssd","hdd","storage"],
    "ram":         ["ram","memory"],
    "graphics":    ["gpu","graphics","rtx","gtx","nvidia"],
}

# ── Data loading (cached at startup) ─────────────────────────────────────────
_cache = {}

def infer_brand(name: str) -> str:
    for b in BRAND_PREFIXES:
        if str(name).lower().startswith(b.lower()):
            return b
    return "Unknown"

def classify(score) -> str:
    try:
        s = float(score)
        return "Positive" if s > 0 else ("Negative" if s < 0 else "Neutral")
    except:
        return "Neutral"

def detect_aspects(text: str) -> list:
    t = str(text).lower()
    return [a for a, kws in ASPECT_KEYWORDS.items()
            if any(re.search(r"\b" + kw + r"\b", t) for kw in kws)]

def short_name(fname: str) -> str:
    stem = os.path.splitext(os.path.basename(fname))[0]
    return stem.replace("_", " ").strip().rstrip(".,- ")

def load_all() -> dict:
    if _cache:
        return _cache

    frames = []
    for fp in glob.glob(f"{AMAZON_DIR}/*.csv"):
        try:
            df = pd.read_csv(fp)
            df.columns = [c.strip().lower() for c in df.columns]
            df["laptop_name"] = short_name(fp)
            df["brand"] = df["laptop_name"].apply(infer_brand)
            df["source"] = "amazon"
            frames.append(df)
        except Exception:
            pass

    for fp in glob.glob(f"{REDDIT_DIR}/*.csv"):
        if "all_reddit_cleaned" in fp:
            continue
        try:
            df = pd.read_csv(fp)
            df.columns = [c.strip().lower() for c in df.columns]
            df["laptop_name"] = short_name(fp)
            df["brand"] = df["laptop_name"].apply(infer_brand)
            df["source"] = "reddit"
            frames.append(df)
        except Exception:
            pass

    if not frames:
        _cache.update({"sentences": pd.DataFrame(), "models": pd.DataFrame(),
                       "sentiment": pd.DataFrame(), "aspects": pd.DataFrame(),
                       "model_aspects": pd.DataFrame(), "opportunities": pd.DataFrame()})
        return _cache

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        all_s = pd.concat(frames, ignore_index=True)
    all_s["laptop_name"] = all_s["laptop_name"].str.strip()
    all_s["brand"] = all_s["brand"].str.strip()
    all_s["compound_score"] = pd.to_numeric(all_s.get("compound_score", 0), errors="coerce").fillna(0)
    all_s["sentiment_label"] = all_s["compound_score"].apply(classify)

    # Models
    grp = all_s.groupby(["laptop_name", "brand"], as_index=False).agg(
        total_sentences=("sentence", "count"),
        avg_sentiment=("compound_score", "mean"),
        review=("sentence", lambda x: " | ".join(x.dropna().astype(str).head(3))),
    )
    grp["price"]  = grp["laptop_name"].apply(lambda n: get_price_rating(n)["price"])
    grp["rating"] = grp["laptop_name"].apply(lambda n: get_price_rating(n)["rating"])

    # Brand sentiment
    def sent_pct(g):
        total = len(g)
        return pd.Series({
            "Positive": round((g["sentiment_label"] == "Positive").sum() / total * 100, 1),
            "Negative": round((g["sentiment_label"] == "Negative").sum() / total * 100, 1),
            "Neutral":  round((g["sentiment_label"] == "Neutral").sum()  / total * 100, 1),
            "Total": total,
        })
    sent_df = all_s.groupby("brand").apply(sent_pct, include_groups=False).reset_index()
    sent_df.rename(columns={"brand": "Brand"}, inplace=True)

    # Global aspect stats
    aspect_stats = defaultdict(lambda: {"demand": 0, "strength": 0, "weakness": 0})
    model_asp_stats = defaultdict(lambda: defaultdict(lambda: {"d": 0, "s": 0, "w": 0}))

    for _, row in all_s.iterrows():
        aspects = detect_aspects(row.get("sentence", ""))
        label = row["sentiment_label"]
        model = row["laptop_name"]
        brand = row["brand"]
        for asp in aspects:
            aspect_stats[asp]["demand"] += 1
            model_asp_stats[(model, brand)][asp]["d"] += 1
            if label == "Positive":
                aspect_stats[asp]["strength"] += 1
                model_asp_stats[(model, brand)][asp]["s"] += 1
            elif label == "Negative":
                aspect_stats[asp]["weakness"] += 1
                model_asp_stats[(model, brand)][asp]["w"] += 1

    total_asp = sum(v["demand"] for v in aspect_stats.values()) or 1
    aspect_rows = []
    for asp, c in sorted(aspect_stats.items(), key=lambda x: -x[1]["demand"]):
        aspect_rows.append({
            "aspect": asp.capitalize(),
            "demand": c["demand"],
            "strength": c["strength"],
            "weakness": c["weakness"],
            "demand_pct": round(c["demand"] / total_asp * 100, 1),
        })
    aspects_df = pd.DataFrame(aspect_rows)

    # Model-aspect scores
    ma_rows = []
    for (model, brand), asp_dict in model_asp_stats.items():
        for asp, c in asp_dict.items():
            d = c["d"] or 1
            ma_rows.append({
                "laptop_name": model, "brand": brand, "aspect": asp,
                "demand": c["d"], "strength": c["s"], "weakness": c["w"],
                "pos_ratio": round(c["s"] / d * 100, 1),
                "neg_ratio": round(c["w"] / d * 100, 1),
            })
    ma_df = pd.DataFrame(ma_rows) if ma_rows else pd.DataFrame()

    opp_df = aspects_df[["aspect", "demand", "demand_pct"]].copy()
    opp_df.rename(columns={"aspect": "opportunity", "demand": "mentions",
                            "demand_pct": "percentage"}, inplace=True)

    _cache.update({
        "sentences": all_s,
        "models": grp,
        "sentiment": sent_df,
        "aspects": aspects_df,
        "model_aspects": ma_df,
        "opportunities": opp_df.head(12),
    })
    return _cache


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/price-models")
def get_price_models(brand: str = Query(None)):
    """Returns the 40 canonical models with prices from model_prices.py (Amazon data)."""
    rows = []
    for model_name, pr in MODEL_PRICE_RATING.items():
        b = infer_brand(model_name)
        if brand and b.lower() != brand.lower():
            continue
        rows.append({
            "laptop_name": model_name,
            "brand": b,
            "price": pr["price"],
            "rating": pr["rating"],
        })
    rows.sort(key=lambda x: x["price"])
    return {"models": rows}


@app.get("/api/brands")
def get_brands():
    d = load_all()
    if d["models"].empty:
        return {"brands": []}
    return {"brands": sorted(d["models"]["brand"].dropna().unique().tolist())}


@app.get("/api/models")
def get_models(brand: str = Query(None)):
    d = load_all()
    df = d["models"].copy()
    if brand:
        df = df[df["brand"].str.lower() == brand.lower()]
    df = df.where(pd.notna(df), None)
    return {"models": df.to_dict(orient="records")}


@app.get("/api/sentiment")
def get_sentiment():
    d = load_all()
    df = d["sentiment"].copy().where(pd.notna(d["sentiment"]), None)
    return {"sentiment": df.to_dict(orient="records")}


@app.get("/api/aspects")
def get_aspects():
    d = load_all()
    df = d["aspects"].copy().where(pd.notna(d["aspects"]), None)
    return {"aspects": df.to_dict(orient="records")}


@app.get("/api/opportunities")
def get_opportunities():
    d = load_all()
    df = d["opportunities"].copy().where(pd.notna(d["opportunities"]), None)
    return {"opportunities": df.to_dict(orient="records")}


@app.get("/api/model-aspects")
def get_model_aspects(brand: str = Query(None), model: str = Query(None)):
    d = load_all()
    df = d["model_aspects"].copy()
    if brand:
        df = df[df["brand"].str.lower() == brand.lower()]
    if model:
        df = df[df["laptop_name"].str.lower() == model.lower()]
    df = df.where(pd.notna(df), None)
    return {"model_aspects": df.to_dict(orient="records")}


def _norm(s: str) -> str:
    """Normalise a model name for matching: lowercase, strip punctuation, collapse spaces."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", str(s).lower())).strip()


def find_model_in_df(peer_name: str, peer_brand: str, df: pd.DataFrame,
                     name_col: str = "laptop_name") -> pd.Series | None:
    """
    Find the best-matching row in df for a given peer model name + brand.
    Strategy:
      1. Exact normalised match within the correct brand
      2. All normalised tokens of peer_name present in the row name (brand-filtered)
      3. Fallback: same brand + highest token overlap
    Returns the matching row Series or None.
    """
    brand_df = df[df["brand"].str.lower() == peer_brand.lower()]
    if brand_df.empty:
        return None

    norm_peer = _norm(peer_name)
    peer_tokens = set(norm_peer.split())

    # 1. Exact normalised match
    for _, row in brand_df.iterrows():
        if _norm(row[name_col]) == norm_peer:
            return row

    # 2. All peer tokens present in row name
    best_row = None
    best_overlap = 0
    for _, row in brand_df.iterrows():
        row_tokens = set(_norm(row[name_col]).split())
        overlap = len(peer_tokens & row_tokens)
        if overlap > best_overlap:
            best_overlap = overlap
            best_row = row

    # Require at least 2 tokens to match to avoid false positives
    if best_row is not None and best_overlap >= 2:
        return best_row

    return None


@app.get("/api/competitor-advantages")
def get_competitor_advantages(target: str = Query("ASUS")):
    d = load_all()
    ma = d["model_aspects"]
    advantages = []

    if ma.empty:
        return {"advantages": []}

    target_models = ma[ma["brand"].str.lower() == target.lower()]["laptop_name"].unique()
    seen = set()

    for t_model in target_models:
        peers = get_spec_peers(t_model)
        t_pr = get_price_rating(t_model)

        for peer in peers:
            p_name  = peer["model"]
            p_brand = peer["brand"]

            match = find_model_in_df(p_name, p_brand, ma)
            if match is None:
                continue
            c_model = match["laptop_name"]
            c_brand = match["brand"]
            c_pr    = get_price_rating(c_model)

            # ── Price advantage ──────────────────────────────────────────
            if t_pr["price"] and c_pr["price"]:
                diff = t_pr["price"] - c_pr["price"]
                if diff >= 3000:
                    key = (c_model, t_model, "price_raw")
                    if key not in seen:
                        seen.add(key)
                        sev = "High" if diff >= 10000 else "Medium" if diff >= 5000 else "Low"
                        advantages.append({
                            "competitor": c_brand,
                            "competitor_model": c_model,
                            "target_model": t_model,
                            "advantage": "Price",
                            "adv_type": "price",
                            "detail": f"Rs.{c_pr['price']:,} vs Rs.{t_pr['price']:,} — Rs.{diff:,} cheaper",
                            "metric": f"-Rs.{diff:,}",
                            "severity": sev,
                        })

            # ── Rating advantage ─────────────────────────────────────────
            if t_pr["rating"] and c_pr["rating"]:
                rdiff = round(c_pr["rating"] - t_pr["rating"], 1)
                if rdiff >= 0.2:
                    key = (c_model, t_model, "rating_raw")
                    if key not in seen:
                        seen.add(key)
                        sev = "High" if rdiff >= 0.4 else "Medium" if rdiff >= 0.3 else "Low"
                        advantages.append({
                            "competitor": c_brand,
                            "competitor_model": c_model,
                            "target_model": t_model,
                            "advantage": "Rating",
                            "adv_type": "rating",
                            "detail": f"Rated {c_pr['rating']} vs {t_pr['rating']} for {t_model} (+{rdiff} pts)",
                            "metric": f"+{rdiff} pts",
                            "severity": sev,
                        })

            # ── Feature / complaint advantages ───────────────────────────
            t_asp = ma[(ma["laptop_name"] == t_model) & (ma["brand"].str.lower() == target.lower())]
            c_asp = ma[(ma["laptop_name"] == c_model) & (ma["brand"].str.lower() == c_brand.lower())]

            for _, c_row in c_asp.iterrows():
                asp     = c_row["aspect"]
                t_match = t_asp[t_asp["aspect"] == asp]
                if t_match.empty:
                    continue
                t_row    = t_match.iloc[0]
                diff_pos = c_row["pos_ratio"] - t_row["pos_ratio"]
                diff_neg = t_row["neg_ratio"] - c_row["neg_ratio"]

                if diff_pos >= 15:
                    key = (c_model, t_model, asp, "feat")
                    if key not in seen:
                        seen.add(key)
                        sev = "High" if diff_pos >= 30 else "Medium" if diff_pos >= 20 else "Low"
                        advantages.append({
                            "competitor": c_brand,
                            "competitor_model": c_model,
                            "target_model": t_model,
                            "advantage": asp.capitalize(),
                            "adv_type": "feature",
                            "detail": f"{c_row['pos_ratio']:.0f}% positive {asp} vs {t_row['pos_ratio']:.0f}% for {t_model}",
                            "metric": f"+{diff_pos:.0f}%",
                            "severity": sev,
                        })

                if diff_neg >= 15:
                    key = (c_model, t_model, asp, "comp")
                    if key not in seen:
                        seen.add(key)
                        sev = "High" if diff_neg >= 30 else "Medium" if diff_neg >= 20 else "Low"
                        advantages.append({
                            "competitor": c_brand,
                            "competitor_model": c_model,
                            "target_model": t_model,
                            "advantage": asp.capitalize(),
                            "adv_type": "complaint",
                            "detail": f"Only {c_row['neg_ratio']:.0f}% {asp} complaints vs {t_row['neg_ratio']:.0f}% for {t_model}",
                            "metric": f"-{diff_neg:.0f}% complaints",
                            "severity": sev,
                        })

    # Sort: High first, then Medium, then Low
    sev_order = {"High": 0, "Medium": 1, "Low": 2}
    advantages.sort(key=lambda x: sev_order.get(x["severity"], 3))
    return {"advantages": advantages}


@app.get("/api/model-comparison")
def get_model_comparison(asus_model: str = Query(...)):
    """
    Full comparison data for one ASUS model vs its spec-matched peers.
    Returns prices, ratings, and per-aspect sentiment for every model in the group.
    """
    from model_groups import get_spec_peers, get_group_label, GROUPS, get_spec_group
    d = load_all()
    ma = d["model_aspects"]
    pr_data = MODEL_PRICE_RATING

    # Get the full row from GROUPS (includes the ASUS model itself)
    group_name, row_key = get_spec_group(asus_model)
    if group_name is None:
        return {"error": "Model not found in any spec group", "models": []}

    row_models = GROUPS[group_name][row_key]   # e.g. [ASUS ..., HP ..., Dell ..., Lenovo ...]
    group_label = get_group_label(asus_model)

    ASPECTS_LIST = ["performance","battery","display","thermal","keyboard","design","price","graphics","ram","storage"]

    result_models = []
    for m_name in row_models:
        brand = get_brand(m_name)
        pr = get_price_rating(m_name)

        # Find aspect data — match by brand-aware token overlap
        if not ma.empty:
            m_rows = find_model_in_df(m_name, brand, ma)
            if m_rows is not None:
                matched_name = m_rows["laptop_name"]
                asp_rows = ma[ma["laptop_name"] == matched_name]
            else:
                asp_rows = pd.DataFrame()
        else:
            asp_rows = pd.DataFrame()

        aspects = {}
        for asp in ASPECTS_LIST:
            row = asp_rows[asp_rows["aspect"] == asp]
            if not row.empty:
                r = row.iloc[0]
                aspects[asp] = {
                    "pos_ratio": r["pos_ratio"],
                    "neg_ratio": r["neg_ratio"],
                    "demand":    int(r["demand"]),
                    "strength":  int(r["strength"]),
                    "weakness":  int(r["weakness"]),
                }
            else:
                aspects[asp] = None

        result_models.append({
            "model":   m_name,
            "brand":   brand,
            "price":   pr["price"],
            "rating":  pr["rating"],
            "aspects": aspects,
            "is_target": brand == "ASUS",
        })

    return {
        "asus_model":   asus_model,
        "group":        group_label,
        "models":       result_models,
    }


@app.get("/api/spec-peers")
def get_spec_peers_api(model: str = Query(...)):
    peers = get_spec_peers(model)
    group = get_group_label(model)
    d = load_all()
    result = []
    for peer in peers:
        p_name = peer["model"]
        p_brand = peer["brand"]
        pr = get_price_rating(p_name)
        # Use brand-aware matching
        match = find_model_in_df(p_name, p_brand, d["models"])
        if match is not None:
            result.append({
                "model": match["laptop_name"], "brand": match["brand"],
                "price": match.get("price"), "rating": match.get("rating"),
            })
        else:
            result.append({"model": p_name, "brand": p_brand,
                           "price": pr["price"], "rating": pr["rating"]})
    return {"peers": result, "group": group}


@app.get("/api/insights")
def get_insights(asus_model: str = Query(...)):
    """AI-powered competitor intelligence for a given ASUS model."""
    try:
        from backend.insights_engine import competitor_analysis, generate_insights
        d = load_all()
        ma = d["model_aspects"]

        # Get model-level aspect data for sentiment-based weakness detection
        model_asp_list = []
        if not ma.empty:
            rows = ma[ma["laptop_name"].str.lower() == asus_model.lower()]
            if rows.empty:
                # fuzzy: token overlap
                norm = set(re.sub(r"[^a-z0-9 ]", " ", asus_model.lower()).split())
                for name in ma["laptop_name"].unique():
                    tokens = set(re.sub(r"[^a-z0-9 ]", " ", name.lower()).split())
                    if len(norm & tokens) >= 2:
                        rows = ma[ma["laptop_name"] == name]
                        break
            model_asp_list = rows.to_dict(orient="records") if not rows.empty else []

        analysis  = competitor_analysis(asus_model)
        insights  = generate_insights(asus_model, model_asp_list)
        return {"analysis": analysis, "insights": insights}
    except Exception as e:
        return {"error": str(e), "analysis": None, "insights": []}


@app.get("/api/summary")
def get_summary(target: str = Query("ASUS")):
    """Home page AI Market Summary data."""
    d = load_all()
    brands = sorted(d["models"]["brand"].dropna().unique().tolist()) if not d["models"].empty else []
    opps = d["opportunities"].head(5).to_dict(orient="records") if not d["opportunities"].empty else []
    adv_resp = get_competitor_advantages(target)
    advantages = adv_resp["advantages"][:6]

    # Target weaknesses from model_aspects
    weaknesses = []
    ma = d["model_aspects"]
    if not ma.empty:
        t_ma = ma[ma["brand"].str.lower() == target.lower()]
        for _, row in t_ma[t_ma["neg_ratio"] >= 20].sort_values("neg_ratio", ascending=False).head(5).iterrows():
            weaknesses.append({
                "model": row["laptop_name"],
                "aspect": row["aspect"],
                "neg_ratio": row["neg_ratio"],
                "summary": f"{row['neg_ratio']:.0f}% negative {row['aspect']} reviews ({row['weakness']} mentions)",
            })

    return {
        "brands": brands,
        "brand_count": len(brands),
        "opportunities": opps,
        "advantages": advantages,
        "weaknesses": weaknesses,
    }


# ── Chat / RAG + Gemini endpoint ─────────────────────────────────────────────

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

class ChatRequest(BaseModel):
    query: str

@app.post("/api/chat")
def chat(req: ChatRequest):
    """RAG retrieval -> Gemini LLM -> answer."""
    if not _rag_ready:
        return {"answer": "RAG model is still loading. Please try again in a moment.", "meta": None}
    try:
        import rag_model as rm

        # Step 1 — FAISS retrieval: top 5 relevant review sentences
        results = rm.retrieve(req.query, _rag_df, _rag_index, _rag_embed, top_k=5)

        # Step 2 — Assemble context
        context_lines = []
        for r in results:
            score = r.get("compound_score", 0.0)
            tone  = "positive" if float(score) > 0.05 else ("negative" if float(score) < -0.05 else "neutral")
            context_lines.append(
                f"- [{r['product']} | {tone}] {r['sentence']}"
            )
        context = "\n".join(context_lines)

        # Step 3 — Build Gemini prompt
        prompt = (
            "You are a laptop market analyst assistant. "
            "Answer the user's question using ONLY the review excerpts provided below. "
            "Be concise (2-4 sentences), specific, and mention product names where relevant.\n\n"
            f"Review excerpts:\n{context}\n\n"
            f"User question: {req.query}\n\n"
            "Answer:"
        )

        # Step 4 — Call Gemini
        answer = None
        gemini_used = False
        if GEMINI_API_KEY:
            try:
                from google import genai as google_genai
                client = google_genai.Client(api_key=GEMINI_API_KEY)
                for model_name in ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash"]:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                        )
                        answer = response.text.strip()
                        gemini_used = True
                        break
                    except Exception as model_err:
                        err_str = str(model_err)
                        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "404" in err_str:
                            continue
                        raise
            except Exception:
                pass  # fall through to RAG-only answer

        # Fallback: summarise top results if Gemini unavailable
        if not answer:
            top = results[0]
            score = top.get("compound_score", 0.0)
            tone  = "positive" if float(score) > 0.05 else ("negative" if float(score) < -0.05 else "neutral")
            snippets = " | ".join(f"{r['product']}: \"{r['sentence'][:80]}...\"" for r in results[:3])
            answer = f"Top review matches for your query:\n{snippets}"

        # Meta from top result
        top = results[0]
        score = top.get("compound_score", 0.0)
        tone  = "positive" if float(score) > 0.05 else ("negative" if float(score) < -0.05 else "neutral")

        return {
            "answer": answer,
            "meta": {
                "product":    top["product"],
                "brand":      top["brand"],
                "tone":       tone,
                "score":      round(float(score), 3),
                "similarity": top["similarity_score"],
                "sources":    len(results),
                "gemini":     gemini_used,
            }
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "meta": None}
