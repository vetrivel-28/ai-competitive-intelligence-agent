"""
Laptop Market Analysis Dashboard
Interactive Streamlit dashboard displaying all analysis results
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from strategy_engine import generate_all_strategies
# Target company configuration (inlined)
ALL_BRANDS = ["ASUS", "HP", "Lenovo", "Dell", "Apple", "MSI", "Acer"]
COMPETITOR_POOL = ["HP", "Lenovo", "Dell", "Apple"]

def get_competitors(target):
    return [b for b in COMPETITOR_POOL if b.lower() != target.lower()]

def fmt_model(brand, model_name):
    """Return model_name as-is if it already starts with brand, else prepend brand."""
    if not brand or not model_name:
        return model_name or ""
    if str(model_name).lower().startswith(str(brand).lower()):
        return model_name
    return f"{brand} {model_name}"

# Page configuration
st.set_page_config(
    page_title="Laptop Market Analysis Dashboard",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all analysis data from amazon_final_files/ and reddit_vader_results/."""
    import glob, os, re as _re
    from collections import defaultdict
    data = {}

    AMAZON_DIR = 'amazon_final_files'
    REDDIT_DIR = 'reddit_vader_results/reddit_vader_results'

    BRAND_PREFIXES = ['ASUS', 'HP', 'Dell', 'Lenovo', 'Apple', 'MSI', 'Acer']

    # ── Aspect keyword dictionary ─────────────────────────────────────────
    ASPECT_KEYWORDS = {
        "performance": ["performance","fast","speed","smooth","lag","gaming",
                        "processor","cpu","amd","intel","fps","powerful"],
        "battery":     ["battery","backup","charging","charge","drain"],
        "display":     ["display","screen","brightness","refresh","resolution",
                        "fhd","144hz","panel"],
        "price":       ["price","cost","expensive","cheap","value","money","deal","worth"],
        "design":      ["design","build","look","stylish","weight","portable",
                        "body","plastic","premium"],
        "keyboard":    ["keyboard","keys","typing","trackpad","touchpad"],
        "audio":       ["speaker","speakers","audio","sound","mic"],
        "camera":      ["camera","webcam"],
        "thermal":     ["heat","heating","temperature","thermal","fan","cooling","hot"],
        "storage":     ["ssd","hdd","storage"],
        "ram":         ["ram","memory"],
        "graphics":    ["gpu","graphics","rtx","gtx","nvidia"],
    }

    def infer_brand(name: str) -> str:
        for b in BRAND_PREFIXES:
            if str(name).lower().startswith(b.lower()):
                return b
        return 'Unknown'

    def clean_model_name(fname: str) -> str:
        stem = os.path.splitext(os.path.basename(fname))[0]
        return stem.replace('_', ' ').strip()

    def short_name(raw_name: str, fname_stem: str) -> str:
        """
        Return a clean short model name from the filename stem.
        Strips trailing punctuation/spaces left by scraper filename conventions.
        """
        clean = fname_stem.replace('_', ' ').strip().rstrip('.,- ')
        if clean:
            return clean
        return raw_name.split(',')[0].strip()

    def classify_sentiment(score):
        """Classify compound_score into sentiment_label."""
        try:
            s = float(score)
        except (TypeError, ValueError):
            return 'Neutral'
        if s > 0:
            return 'Positive'
        elif s < 0:
            return 'Negative'
        return 'Neutral'

    def detect_aspects(text: str) -> list:
        """Return list of aspect names found in text."""
        t = str(text).lower()
        found = []
        for aspect, kws in ASPECT_KEYWORDS.items():
            if any(_re.search(r'\b' + kw + r'\b', t) for kw in kws):
                found.append(aspect)
        return found

    # ── Load all CSVs ─────────────────────────────────────────────────────
    amazon_frames, reddit_frames = [], []
    for fpath in glob.glob(f'{AMAZON_DIR}/*.csv'):
        try:
            df = pd.read_csv(fpath)
            df.columns = [c.strip().lower() for c in df.columns]
            # Always override laptop_name with the clean filename stem
            df['laptop_name'] = short_name('', os.path.splitext(os.path.basename(fpath))[0])
            df['brand']  = df['laptop_name'].apply(infer_brand)
            df['source'] = 'amazon'
            amazon_frames.append(df)
        except Exception:
            pass

    for fpath in glob.glob(f'{REDDIT_DIR}/*.csv'):
        if 'all_reddit_cleaned' in fpath:
            continue
        try:
            df = pd.read_csv(fpath)
            df.columns = [c.strip().lower() for c in df.columns]
            # Override with clean filename stem
            df['laptop_name'] = short_name('', os.path.splitext(os.path.basename(fpath))[0])
            df['brand']  = df['laptop_name'].apply(infer_brand)
            df['source'] = 'reddit'
            reddit_frames.append(df)
        except Exception:
            pass

    all_sentences = pd.concat(amazon_frames + reddit_frames, ignore_index=True) \
        if (amazon_frames or reddit_frames) else pd.DataFrame()

    if not all_sentences.empty:
        all_sentences['laptop_name']    = all_sentences['laptop_name'].str.strip()
        all_sentences['brand']          = all_sentences['brand'].str.strip()
        all_sentences['compound_score'] = pd.to_numeric(
            all_sentences.get('compound_score', 0), errors='coerce').fillna(0)

        # ── Apply VADER-based sentiment label ─────────────────────────────
        all_sentences['sentiment_label'] = all_sentences['compound_score'].apply(classify_sentiment)

    # ── Model-level summary ───────────────────────────────────────────────
    if not all_sentences.empty:
        grp = all_sentences.groupby(['laptop_name', 'brand'], as_index=False).agg(
            total_sentences=('sentence', 'count'),
            avg_sentiment=('compound_score', 'mean'),
            review=('sentence', lambda x: ' | '.join(x.dropna().astype(str).head(3))),
        )
        # ── Inject price & rating from model_prices.py ────────────────────
        try:
            from model_prices import get_price_rating
            grp['price']  = grp['laptop_name'].apply(lambda n: get_price_rating(n)['price'])
            grp['rating'] = grp['laptop_name'].apply(lambda n: get_price_rating(n)['rating'])
        except Exception:
            grp['price']  = pd.NA
            grp['rating'] = pd.NA
        grp['model_label'] = grp['brand'] + ' — ' + grp['laptop_name']
        data['models'] = grp
    else:
        data['models'] = pd.DataFrame()

    # ── Brand sentiment summary (from sentiment_label) ────────────────────
    if not all_sentences.empty:
        def sent_pct(group):
            total = len(group)
            pos = (group['sentiment_label'] == 'Positive').sum() / total * 100 if total else 0
            neg = (group['sentiment_label'] == 'Negative').sum() / total * 100 if total else 0
            neu = (group['sentiment_label'] == 'Neutral').sum()  / total * 100 if total else 0
            return pd.Series({'Positive': round(pos,1), 'Negative': round(neg,1),
                              'Neutral': round(neu,1), 'Total': total})
        sent_df = all_sentences.groupby('brand').apply(
            sent_pct, include_groups=False).reset_index()
        sent_df.rename(columns={'brand': 'Brand'}, inplace=True)
        data['sentiment'] = sent_df
    else:
        data['sentiment'] = pd.DataFrame()

    # ── Aspect-Based Sentiment Analysis ───────────────────────────────────
    if not all_sentences.empty:
        aspect_stats = defaultdict(lambda: {'demand': 0, 'strength': 0, 'weakness': 0})

        for _, row in all_sentences.iterrows():
            aspects = detect_aspects(row.get('sentence', ''))
            label   = row['sentiment_label']
            for asp in aspects:
                aspect_stats[asp]['demand'] += 1
                if label == 'Positive':
                    aspect_stats[asp]['strength'] += 1
                elif label == 'Negative':
                    aspect_stats[asp]['weakness'] += 1

        total_aspect_mentions = sum(v['demand'] for v in aspect_stats.values()) or 1
        aspect_rows = []
        for asp, counts in sorted(aspect_stats.items(), key=lambda x: -x[1]['demand']):
            pct = round(counts['demand'] / total_aspect_mentions * 100, 1)
            aspect_rows.append({
                'Aspect':    asp.capitalize(),
                'Demand':    counts['demand'],
                'Strength':  counts['strength'],
                'Weakness':  counts['weakness'],
                'Demand_Pct': pct,
            })

        data['aspects'] = pd.DataFrame(aspect_rows)

        # ── Positive / Negative keyword tables (from aspect data) ─────────
        pos_rows = [(r['Aspect'], r['Strength']) for r in aspect_rows if r['Strength'] > 0]
        neg_rows = [(r['Aspect'], r['Weakness']) for r in aspect_rows if r['Weakness'] > 0]
        data['positive_kw'] = pd.DataFrame(
            sorted(pos_rows, key=lambda x: -x[1])[:20], columns=['Keyword','Count'])
        data['negative_kw'] = pd.DataFrame(
            sorted(neg_rows, key=lambda x: -x[1])[:20], columns=['Keyword','Count'])

        # ── Opportunities: top aspects by demand % ────────────────────────
        opp_df = data['aspects'][['Aspect','Demand','Demand_Pct']].copy()
        opp_df.rename(columns={'Aspect': 'Opportunity', 'Demand': 'Mentions',
                                'Demand_Pct': 'Percentage'}, inplace=True)
        data['opportunities'] = opp_df.sort_values('Mentions', ascending=False).head(12)

        # ── Model-level aspect scores ─────────────────────────────────────
        # For each (laptop_name, brand, aspect) compute pos_ratio and neg_ratio
        model_asp_rows = []
        model_asp_stats = defaultdict(lambda: defaultdict(
            lambda: {'demand': 0, 'strength': 0, 'weakness': 0}))

        for _, row in all_sentences.iterrows():
            model = row['laptop_name']
            brand = row['brand']
            label = row['sentiment_label']
            for asp in detect_aspects(row.get('sentence', '')):
                model_asp_stats[(model, brand)][asp]['demand']   += 1
                if label == 'Positive':
                    model_asp_stats[(model, brand)][asp]['strength'] += 1
                elif label == 'Negative':
                    model_asp_stats[(model, brand)][asp]['weakness'] += 1

        for (model, brand), asp_dict in model_asp_stats.items():
            for asp, counts in asp_dict.items():
                d = counts['demand'] or 1
                model_asp_rows.append({
                    'laptop_name': model,
                    'brand':       brand,
                    'aspect':      asp,
                    'demand':      counts['demand'],
                    'strength':    counts['strength'],
                    'weakness':    counts['weakness'],
                    'pos_ratio':   round(counts['strength'] / d * 100, 1),
                    'neg_ratio':   round(counts['weakness'] / d * 100, 1),
                })

        data['model_aspects'] = pd.DataFrame(model_asp_rows) \
            if model_asp_rows else pd.DataFrame()
    else:
        data['aspects']        = pd.DataFrame()
        data['positive_kw']    = pd.DataFrame()
        data['negative_kw']    = pd.DataFrame()
        data['opportunities']  = pd.DataFrame()
        data['model_aspects']  = pd.DataFrame()

    # ── Competitor / strategies (derived live) ────────────────────────────
    data['competitor'] = pd.DataFrame()
    data['strategies'] = pd.DataFrame()

    return data

# Load data
data = load_data()

# Sidebar
st.sidebar.title("📊 Navigation")
section = st.sidebar.radio(
    "Go to",
    ["🏠 Home", "🏢 Target Overview", "📈 Market Overview", "🆚 Competitor Comparison",
     "⚔️ Competitor Advantages", "💪 Strengths & Weaknesses",
     "🧠 Strategy Recommendations", "🌍 Market Opportunity Insights",
     "😊 Sentiment Analysis", "⚠️ Customer Complaints", "💬 Social Media Insights",
     "🎯 Competitive Strategy", "🤖 Ask AI (RAG)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Target Company")
target_company = st.sidebar.selectbox(
    "Select Target Company",
    options=["ASUS", "HP", "Lenovo", "Dell", "Apple"],
    index=0  # default: ASUS
)
competitors = get_competitors(target_company)
st.sidebar.info(f"Competitors: {', '.join(competitors)}")


# ── Step 3: Filter data by target company ────────────────────────────────────

def split_by_target(df, brand_col, target):
    """Split a dataframe into target_data and competitor_data by brand column."""
    if df.empty or brand_col not in df.columns:
        return pd.DataFrame(), pd.DataFrame()
    target_data     = df[df[brand_col].str.lower() == target.lower()].copy()
    competitor_data = df[df[brand_col].str.lower() != target.lower()].copy()
    return target_data, competitor_data

# Split competitor analysis (Brand column)
target_comp_data,     competitor_comp_data     = split_by_target(data['competitor'], 'Brand', target_company)

# Split sentiment analysis (Brand column)
target_sent_data,     competitor_sent_data     = split_by_target(data['sentiment'],  'Brand', target_company)

# Split strategies (Brand column)
target_strat_data,    competitor_strat_data    = split_by_target(data['strategies'], 'Brand', target_company)

# Combined view: target + selected competitors only
relevant_brands = [target_company] + competitors

def filter_relevant(df, brand_col):
    """Keep only target + competitor rows."""
    if df.empty or brand_col not in df.columns:
        return df
    return df[df[brand_col].isin(relevant_brands)].copy()

filtered_comp = filter_relevant(data['competitor'], 'Brand')
filtered_sent = filter_relevant(data['sentiment'],  'Brand')


# ── Model-level helpers ───────────────────────────────────────────────────────

WEAKNESS_KEYWORDS = {
    'battery drain':    ['battery', 'drain', 'backup', 'charge'],
    'overheating':      ['heat', 'hot', 'thermal', 'overheat', 'temperature'],
    'fan noise':        ['fan', 'noise', 'loud', 'sound'],
    'display issues':   ['display', 'screen', 'flicker', 'dim', 'brightness'],
    'keyboard problems':['keyboard', 'key', 'typing', 'trackpad'],
    'performance':      ['slow', 'lag', 'hang', 'freeze', 'performance', 'speed'],
    'build quality':    ['build', 'plastic', 'flimsy', 'hinge', 'quality'],
    'ram/storage':      ['ram', 'storage', 'memory', 'ssd'],
}

STRENGTH_KEYWORDS = {
    'gaming performance': ['gaming', 'fps', 'game', 'performance'],
    'display quality':    ['display', 'screen', 'ips', 'oled', 'refresh', 'bright'],
    'battery life':       ['battery', 'backup', 'hours', 'long'],
    'build quality':      ['build', 'premium', 'solid', 'metal', 'sturdy'],
    'value for money':    ['value', 'budget', 'affordable', 'price', 'worth'],
    'portability':        ['light', 'slim', 'portable', 'thin', 'compact'],
    'performance':        ['fast', 'speed', 'powerful', 'smooth', 'quick'],
    'keyboard':           ['keyboard', 'typing', 'comfortable'],
}

COMMENTS_PER_MODEL = 50   # fairness cap — equal representation per model


def get_model_reviews(models_df, brand, model_name, n=COMMENTS_PER_MODEL):
    """Return up to n review strings for a specific brand+model."""
    mask = (models_df['brand'].str.lower() == brand.lower()) & \
           (models_df['laptop_name'].str.lower() == model_name.lower())
    rows = models_df[mask].head(n)
    return rows['review'].dropna().tolist()


def detect_model_weaknesses(review_texts):
    """Return weakness reasons found in review texts."""
    found = {}
    combined = ' '.join(str(r) for r in review_texts).lower()
    for label, kws in WEAKNESS_KEYWORDS.items():
        hits = sum(combined.count(k) for k in kws)
        if hits > 0:
            found[label] = hits
    return dict(sorted(found.items(), key=lambda x: x[1], reverse=True))


def detect_model_strengths(review_texts):
    """Return strength reasons found in review texts."""
    found = {}
    combined = ' '.join(str(r) for r in review_texts).lower()
    for label, kws in STRENGTH_KEYWORDS.items():
        hits = sum(combined.count(k) for k in kws)
        if hits > 0:
            found[label] = hits
    return dict(sorted(found.items(), key=lambda x: x[1], reverse=True))


def get_target_models(models_df, target):
    """Return all models for the target brand."""
    if models_df.empty:
        return pd.DataFrame()
    return models_df[models_df['brand'].str.lower() == target.lower()].copy()


def get_competitor_models(models_df, target, comp_list):
    """Return all models for competitor brands."""
    if models_df.empty:
        return pd.DataFrame()
    mask = models_df['brand'].str.lower().isin([c.lower() for c in comp_list])
    return models_df[mask].copy()


def build_model_comparison(models_df, target, comp_list):
    """
    Build a flat comparison dataframe at brand+model level.
    Columns: model_label, brand, laptop_name, price, rating, type
    """
    relevant = [target] + comp_list
    df = models_df[models_df['brand'].isin(relevant)].copy()
    df['type'] = df['brand'].apply(lambda b: 'Target' if b == target else 'Competitor')
    return df.sort_values(['brand', 'price'], ascending=[True, False]).reset_index(drop=True)


def model_strategic_actions(target, models_df, neg_kw_df):
    """Generate model-specific strategic recommendations."""
    actions = []
    target_models = get_target_models(models_df, target)
    if target_models.empty:
        return actions
    for _, row in target_models.iterrows():
        model = row['laptop_name']
        # Use model name as-is if it already contains the brand
        display = model if model.lower().startswith(target.lower()) else f"{target} {model}"
        reviews = get_model_reviews(models_df, target, model)
        weaknesses = detect_model_weaknesses(reviews)
        for weakness in list(weaknesses.keys())[:2]:
            actions.append(f"Improve {weakness} for {display}")
    # Also add from negative keywords
    if not neg_kw_df.empty:
        for _, krow in neg_kw_df.head(3).iterrows():
            kw = krow['Keyword']
            if not target_models.empty:
                model = target_models.iloc[0]['laptop_name']
                display = model if model.lower().startswith(target.lower()) else f"{target} {model}"
                actions.append(f"Address '{kw}' complaints for {display}")
    return actions[:8]


# ── Step 6: Detect competitor advantages ─────────────────────────────────────

def detect_competitor_advantages(target, comp_df, sent_df):
    """
    Model-level + aspect-based competitor advantage detection.
    Uses data['model_aspects'] (injected via global `data`) for aspect ratios.
    Falls back to brand-level sentiment if model_aspects not available.
    Returns list of dicts with keys:
      Competitor, Competitor_Model, Target_Model, Advantage, Detail, Severity
    """
    advantages = []

    # ── Try model-level aspect comparison first ───────────────────────────
    try:
        ma = data.get('model_aspects', pd.DataFrame())
    except Exception:
        ma = pd.DataFrame()

    if not ma.empty:
        from model_groups import get_spec_peers

        target_models = ma[ma['brand'].str.lower() == target.lower()][
            'laptop_name'].unique()

        seen = set()
        for t_model in target_models:
            t_disp = fmt_model(target, t_model)
            peers  = get_spec_peers(t_model)   # [{model, brand}, ...]

            # Also include any model in ma that matches a peer name
            for peer in peers:
                p_name  = peer['model']
                p_brand = peer['brand']

                # Fuzzy match peer against loaded model names
                p_rows = ma[
                    ma['laptop_name'].str.lower().str.contains(
                        p_name.split()[-1].lower(), na=False) |
                    ma['laptop_name'].str.lower().str.contains(
                        p_name.lower()[:8], na=False)
                ]
                if p_rows.empty:
                    continue

                c_model = p_rows.iloc[0]['laptop_name']
                c_brand = p_rows.iloc[0]['brand']
                c_disp  = fmt_model(c_brand, c_model)

                # ── Aspect comparison ─────────────────────────────────────
                t_asp = ma[(ma['laptop_name'] == t_model) &
                           (ma['brand'].str.lower() == target.lower())]
                c_asp = ma[(ma['laptop_name'] == c_model) &
                           (ma['brand'].str.lower() == c_brand.lower())]

                for _, c_row in c_asp.iterrows():
                    asp = c_row['aspect']
                    t_match = t_asp[t_asp['aspect'] == asp]
                    if t_match.empty:
                        continue
                    t_row = t_match.iloc[0]

                    key = (c_disp, t_disp, asp)
                    if key in seen:
                        continue

                    c_pos = c_row['pos_ratio']
                    t_pos = t_row['pos_ratio']
                    c_neg = c_row['neg_ratio']
                    t_neg = t_row['neg_ratio']

                    # Feature advantage: competitor positive ratio ≥15% higher
                    diff_pos = c_pos - t_pos
                    if diff_pos >= 15:
                        seen.add(key)
                        advantages.append({
                            'Competitor':       c_brand,
                            'Competitor_Model': c_disp,
                            'Target_Model':     t_disp,
                            'Advantage':        f'{asp.capitalize()} (Feature)',
                            'Detail':           f"{c_pos:.0f}% positive {asp} reviews vs {t_pos:.0f}% for {t_disp}",
                            'Severity':         'High' if diff_pos >= 25 else 'Medium',
                        })

                    # Complaint advantage: competitor negative ratio ≥15% lower
                    diff_neg = t_neg - c_neg
                    if diff_neg >= 15:
                        seen.add(key)
                        advantages.append({
                            'Competitor':       c_brand,
                            'Competitor_Model': c_disp,
                            'Target_Model':     t_disp,
                            'Advantage':        f'{asp.capitalize()} (Fewer Complaints)',
                            'Detail':           f"Only {c_neg:.0f}% {asp} complaints vs {t_neg:.0f}% for {t_disp}",
                            'Severity':         'High' if diff_neg >= 25 else 'Medium',
                        })

        return advantages

    # ── Fallback: brand-level sentiment comparison ────────────────────────
    if sent_df.empty or 'Brand' not in sent_df.columns:
        return advantages

    sdf = sent_df.copy()
    sdf['Brand'] = sdf['Brand'].str.strip()
    target_row = sdf[sdf['Brand'].str.lower() == target.lower()]
    if target_row.empty:
        return advantages

    t = target_row.iloc[0]

    def get_pct(row, col):
        try: return float(str(row[col]).rstrip('%'))
        except: return 0.0

    t_pos   = get_pct(t, 'Positive')
    t_neg   = get_pct(t, 'Negative')
    t_total = float(t.get('Total', 1) or 1)

    for _, c in sdf[sdf['Brand'].str.lower() != target.lower()].iterrows():
        brand   = c['Brand']
        c_pos   = get_pct(c, 'Positive')
        c_neg   = get_pct(c, 'Negative')
        c_total = float(c.get('Total', 1) or 1)

        diff_pos = c_pos - t_pos
        if diff_pos > 3:
            advantages.append({
                'Competitor': brand, 'Competitor_Model': brand,
                'Target_Model': target,
                'Advantage': 'Better Sentiment',
                'Detail': f"{diff_pos:.1f}% more positive reviews than {target}",
                'Severity': 'High' if diff_pos > 10 else 'Medium',
            })

        diff_neg = t_neg - c_neg
        if diff_neg > 3:
            advantages.append({
                'Competitor': brand, 'Competitor_Model': brand,
                'Target_Model': target,
                'Advantage': 'Fewer Complaints',
                'Detail': f"{diff_neg:.1f}% fewer negative reviews than {target}",
                'Severity': 'High' if diff_neg > 10 else 'Medium',
            })

    return advantages


# Pre-compute advantages for current target
competitor_advantages = detect_competitor_advantages(
    target_company, filtered_comp, data['sentiment']
)


# ── Step 7 & 8: Weaknesses and Strengths ─────────────────────────────────────

def detect_target_weaknesses(target, comp_df, sent_df, neg_kw_df):
    """
    Detect weaknesses of the target company using:
    - Negative keywords from reviews
    - Negative sentiment percentage
    - Rating comparison vs competitors
    """
    weaknesses = []

    # 1. Negative keywords (top complaints)
    if not neg_kw_df.empty:
        top_neg = neg_kw_df.head(10)
        for _, row in top_neg.iterrows():
            weaknesses.append({
                'Source': 'Customer Complaints',
                'Weakness': row['Keyword'],
                'Detail': f"Mentioned {row['Count']} times in negative reviews",
                'Severity': 'High' if row['Count'] >= 5 else 'Medium'
            })

    # 2. Negative sentiment
    if not sent_df.empty:
        t_row = sent_df[sent_df['Brand'].str.lower() == target.lower()]
        if not t_row.empty:
            try:
                neg_pct = float(str(t_row.iloc[0]['Positive']).rstrip('%'))
                # If positive sentiment is below average, flag it
                all_pos = []
                for _, r in sent_df.iterrows():
                    try:
                        all_pos.append(float(str(r['Positive']).rstrip('%')))
                    except:
                        pass
                avg_pos = sum(all_pos) / len(all_pos) if all_pos else 50
                if neg_pct < avg_pos - 10:
                    weaknesses.append({
                        'Source': 'Sentiment Analysis',
                        'Weakness': 'Below-Average Positive Sentiment',
                        'Detail': f"{target} positive sentiment ({neg_pct:.1f}%) is below market avg ({avg_pos:.1f}%)",
                        'Severity': 'High'
                    })
            except:
                pass

    # 3. Rating below competitors
    if not comp_df.empty:
        t_row = comp_df[comp_df['Brand'].str.lower() == target.lower()]
        if not t_row.empty:
            t_rating = t_row.iloc[0].get('Avg_Rating', 0)
            comp_ratings = comp_df[comp_df['Brand'].str.lower() != target.lower()]['Avg_Rating']
            avg_comp_rating = comp_ratings.mean() if not comp_ratings.empty else 0
            if avg_comp_rating - t_rating > 0.1:
                weaknesses.append({
                    'Source': 'Rating Comparison',
                    'Weakness': 'Lower Rating vs Competitors',
                    'Detail': f"{target} avg rating {t_rating:.2f} vs competitor avg {avg_comp_rating:.2f}",
                    'Severity': 'High' if avg_comp_rating - t_rating > 0.3 else 'Medium'
                })

    # 4. Higher price than most competitors
    if not comp_df.empty:
        t_row = comp_df[comp_df['Brand'].str.lower() == target.lower()]
        if not t_row.empty:
            t_price = t_row.iloc[0].get('Avg_Price', 0)
            comp_prices = comp_df[comp_df['Brand'].str.lower() != target.lower()]['Avg_Price']
            cheaper_count = (comp_prices < t_price).sum()
            if cheaper_count >= 2:
                weaknesses.append({
                    'Source': 'Price Analysis',
                    'Weakness': 'Higher Price Segment',
                    'Detail': f"{cheaper_count} competitors offer lower average prices than {target}",
                    'Severity': 'Medium'
                })

    return weaknesses


def detect_target_strengths(target, comp_df, sent_df, pos_kw_df):
    """
    Detect strengths of the target company using:
    - Positive keywords from reviews
    - High positive sentiment
    - Rating vs competitors
    """
    strengths = []

    # 1. Positive keywords
    if not pos_kw_df.empty:
        top_pos = pos_kw_df.head(10)
        for _, row in top_pos.iterrows():
            strengths.append({
                'Source': 'Customer Praise',
                'Strength': row['Keyword'],
                'Detail': f"Praised {row['Count']} times in positive reviews",
                'Impact': 'High' if row['Count'] >= 5 else 'Medium'
            })

    # 2. High positive sentiment vs competitors
    if not sent_df.empty:
        t_row = sent_df[sent_df['Brand'].str.lower() == target.lower()]
        if not t_row.empty:
            try:
                pos_pct = float(str(t_row.iloc[0]['Positive']).rstrip('%'))
                all_pos = []
                for _, r in sent_df.iterrows():
                    try:
                        all_pos.append(float(str(r['Positive']).rstrip('%')))
                    except:
                        pass
                avg_pos = sum(all_pos) / len(all_pos) if all_pos else 50
                if pos_pct > avg_pos + 5:
                    strengths.append({
                        'Source': 'Sentiment Analysis',
                        'Strength': 'Above-Average Positive Sentiment',
                        'Detail': f"{target} positive sentiment ({pos_pct:.1f}%) exceeds market avg ({avg_pos:.1f}%)",
                        'Impact': 'High'
                    })
            except:
                pass

    # 3. Higher rating than competitors
    if not comp_df.empty:
        t_row = comp_df[comp_df['Brand'].str.lower() == target.lower()]
        if not t_row.empty:
            t_rating = t_row.iloc[0].get('Avg_Rating', 0)
            comp_ratings = comp_df[comp_df['Brand'].str.lower() != target.lower()]['Avg_Rating']
            avg_comp_rating = comp_ratings.mean() if not comp_ratings.empty else 0
            if t_rating - avg_comp_rating > 0.05:
                strengths.append({
                    'Source': 'Rating Comparison',
                    'Strength': 'Higher Rating vs Competitors',
                    'Detail': f"{target} avg rating {t_rating:.2f} vs competitor avg {avg_comp_rating:.2f}",
                    'Impact': 'High' if t_rating - avg_comp_rating > 0.2 else 'Medium'
                })

    # 4. Best value score
    if not comp_df.empty:
        t_row = comp_df[comp_df['Brand'].str.lower() == target.lower()]
        if not t_row.empty and 'Value_Score' in comp_df.columns:
            t_val = t_row.iloc[0].get('Value_Score', 0)
            max_val = comp_df['Value_Score'].max()
            if t_val == max_val:
                strengths.append({
                    'Source': 'Value Analysis',
                    'Strength': 'Best Value Score in Market',
                    'Detail': f"{target} leads with value score of {t_val:.2f}",
                    'Impact': 'High'
                })

    return strengths


# Pre-compute weaknesses and strengths
target_weaknesses = detect_target_weaknesses(
    target_company, filtered_comp, data['sentiment'], data['negative_kw']
)
target_strengths = detect_target_strengths(
    target_company, filtered_comp, data['sentiment'], data['positive_kw']
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📁 Data Status")
if not data['competitor'].empty:
    st.sidebar.success(f"✅ Competitor Data: {len(data['competitor'])} brands")
if not data['sentiment'].empty:
    st.sidebar.success(f"✅ Sentiment Data: {len(data['sentiment'])} brands")
if not data['opportunities'].empty:
    st.sidebar.success(f"✅ Opportunities: {len(data['opportunities'])} detected")


# ============================================================================
# HOME SECTION
# ============================================================================
if section == "🏠 Home":
    st.markdown('<h1 class="main-header">💻 Laptop Market Intelligence Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f"Target: **{target_company}** &nbsp;|&nbsp; Competitors: {', '.join(competitors)}")

    # ── Key Metrics — brands only ─────────────────────────────────────────
    st.markdown("### 📊 Brands in Analysis")
    all_brands_in_data = []
    if not data['competitor'].empty and 'Brand' in data['competitor'].columns:
        all_brands_in_data = data['competitor']['Brand'].tolist()
    elif not data['models'].empty:
        all_brands_in_data = data['models']['brand'].unique().tolist()

    c1, c2 = st.columns([1, 3])
    c1.metric("Total Brands Analyzed", len(all_brands_in_data) if all_brands_in_data else "N/A")
    with c2:
        if all_brands_in_data:
            st.markdown("**Brands:** " + " &nbsp;·&nbsp; ".join(
                [f"`{b}`" for b in sorted(all_brands_in_data)]
            ))

    st.markdown("---")

    # ── AI Market Summary ─────────────────────────────────────────────────
    st.markdown("### 🤖 AI Market Summary")

    _weaknesses = detect_target_weaknesses(target_company, filtered_comp, data['sentiment'], data['negative_kw'])
    _strengths  = detect_target_strengths(target_company,  filtered_comp, data['sentiment'], data['positive_kw'])
    _advantages = detect_competitor_advantages(target_company, filtered_comp, data['sentiment'])
    _strategies = generate_all_strategies(
        target_company, _weaknesses, _strengths, _advantages,
        data['negative_kw'], data['opportunities']
    )

    # ── Build model-level competitor advantages ───────────────────────────
    def model_level_advantages(target, models_df, comp_df):
        """
        Model-level advantages using aspect sentiment ratios from data['model_aspects'].
        Falls back to price/rating comparison if aspect data unavailable.
        """
        results = []
        if models_df.empty:
            return results

        ma = data.get('model_aspects', pd.DataFrame())

        if not ma.empty:
            try:
                from model_groups import get_spec_peers
            except ImportError:
                get_spec_peers = lambda m: []

            target_models_list = models_df[
                models_df['brand'].str.lower() == target.lower()]['laptop_name'].unique()

            seen = set()
            for t_model in target_models_list:
                t_disp = fmt_model(target, t_model)
                peers  = get_spec_peers(t_model)
                for peer in peers:
                    p_name  = peer['model']
                    p_brand = peer['brand']
                    p_rows  = ma[
                        ma['laptop_name'].str.lower().str.contains(
                            p_name.split()[-1].lower(), na=False) |
                        ma['laptop_name'].str.lower().str.contains(
                            p_name.lower()[:8], na=False)
                    ]
                    if p_rows.empty:
                        continue
                    c_model = p_rows.iloc[0]['laptop_name']
                    c_brand = p_rows.iloc[0]['brand']
                    c_disp  = fmt_model(c_brand, c_model)

                    t_asp = ma[(ma['laptop_name'] == t_model) &
                               (ma['brand'].str.lower() == target.lower())]
                    c_asp = ma[(ma['laptop_name'] == c_model) &
                               (ma['brand'].str.lower() == c_brand.lower())]

                    for _, c_row in c_asp.iterrows():
                        asp = c_row['aspect']
                        t_match = t_asp[t_asp['aspect'] == asp]
                        if t_match.empty:
                            continue
                        t_row = t_match.iloc[0]
                        key = (c_disp, t_disp, asp)
                        if key in seen:
                            continue
                        diff_pos = c_row['pos_ratio'] - t_row['pos_ratio']
                        diff_neg = t_row['neg_ratio'] - c_row['neg_ratio']
                        if diff_pos >= 15:
                            seen.add(key)
                            results.append(
                                f"{c_disp} — Better {asp} than {t_disp} "
                                f"({c_row['pos_ratio']:.0f}% vs {t_row['pos_ratio']:.0f}% positive)"
                            )
                        elif diff_neg >= 15:
                            seen.add(key)
                            results.append(
                                f"{c_disp} — Fewer {asp} complaints than {t_disp} "
                                f"({c_row['neg_ratio']:.0f}% vs {t_row['neg_ratio']:.0f}% negative)"
                            )
            return results[:6]

        # Fallback: price/rating from models_df
        target_models = models_df[models_df['brand'].str.lower() == target.lower()]
        comp_models   = models_df[models_df['brand'].str.lower() != target.lower()]
        for _, tm in target_models.iterrows():
            t_price  = tm.get('price',  0)
            t_rating = tm.get('rating', 0)
            t_name   = fmt_model(target, tm['laptop_name'])
            for _, cm in comp_models.iterrows():
                c_price  = cm.get('price',  0)
                c_rating = cm.get('rating', 0)
                c_brand  = cm['brand']
                c_name   = fmt_model(c_brand, cm['laptop_name'])
                if pd.notna(c_price) and pd.notna(t_price) and t_price > 0:
                    diff = t_price - c_price
                    if diff > 1000:
                        results.append(f"{c_name} — Rs {diff:,.0f} cheaper than {t_name}")
                if pd.notna(c_rating) and pd.notna(t_rating) and t_rating > 0:
                    diff = c_rating - t_rating
                    if diff > 0.1:
                        results.append(f"{c_name} — rated {diff:.1f} pts higher than {t_name}")
        return results[:6]

    # ── Build model-level weaknesses ──────────────────────────────────────
    def model_level_weaknesses(target, models_df, neg_kw_df):
        """
        Returns list of dicts with model, feature, summary.
        Example: ASUS VivoBook 15 — RAM performance issues
        """
        results = []
        if models_df.empty:
            return results
        target_models = models_df[models_df['brand'].str.lower() == target.lower()]
        for _, mrow in target_models.iterrows():
            model_name = mrow['laptop_name']
            reviews    = get_model_reviews(models_df, target, model_name)
            weaknesses = detect_model_weaknesses(reviews)
            for feature, count in list(weaknesses.items())[:2]:
                summary = f"Multiple users reported {feature} issues based on {count} keyword mentions in reviews."
                results.append({
                    'model':   fmt_model(target, model_name),
                    'feature': feature,
                    'summary': summary
                })
        return results[:5]

    # ── Build clean strategic actions (no duplicate brand) ────────────────
    def clean_actions(target, models_df, neg_kw_df):
        raw = model_strategic_actions(target, models_df, neg_kw_df)
        cleaned = []
        for action in raw:
            # Strip any duplicate brand prefix regardless of pattern
            words = action.split()
            if len(words) >= 2 and words[0].lower() == words[1].lower() == target.lower():
                action = ' '.join(words[1:])
            elif len(words) >= 2 and words[0].lower() == target.lower() and words[1].lower() == target.lower():
                action = ' '.join(words[1:])
            cleaned.append(action)
        return cleaned

    model_adv      = model_level_advantages(target_company, data['models'], filtered_comp)
    model_weak     = model_level_weaknesses(target_company, data['models'], data['negative_kw'])
    clean_acts     = clean_actions(target_company, data['models'], data['negative_kw'])

    col_left, col_right = st.columns(2)

    with col_left:
        # Competitor Advantages — model level
        st.markdown("#### ⚔️ Competitor Advantages")
        if model_adv:
            for adv in model_adv:
                st.markdown(f"🔴 {adv}")
        elif _advantages:
            for adv in _advantages[:4]:
                icon = "🔴" if adv['Severity'] == 'High' else "🟡"
                st.markdown(f"{icon} **{adv['Competitor']}** — {adv['Advantage']}: {adv['Detail']}")
        else:
            st.success(f"No significant competitor advantages detected against {target_company}.")

        st.markdown("#### ❌ Target Weaknesses")
        if model_weak:
            for w in model_weak:
                st.markdown(
                    f"🔴 **{w['model']}** — {w['feature'].title()} issues  \n"
                    f"<small style='color:#888'>Summary: {w['summary']}</small>",
                    unsafe_allow_html=True
                )
        elif _weaknesses:
            for w in _weaknesses[:4]:
                icon = "🔴" if w['Severity'] == 'High' else "🟡"
                st.markdown(f"{icon} {w['Weakness']} — _{w['Detail']}_")
        else:
            st.success("No significant weaknesses detected.")

    with col_right:
        # Emerging Market Opportunities — with demand % and mentions
        st.markdown("#### 🌍 Emerging Market Opportunities")
        if not data['opportunities'].empty:
            for _, row in data['opportunities'].head(5).iterrows():
                pct      = row.get('Percentage', 0)
                mentions = row.get('Mentions', 0)
                st.markdown(f"🔵 **{row['Opportunity']}** — {pct}% demand ({mentions} mentions)")
        else:
            st.info("No opportunity data available.")

        # Recommended Strategic Actions — clean, model-specific
        st.markdown("#### 🧠 Recommended Strategic Actions")
        if clean_acts:
            for action in clean_acts[:5]:
                st.markdown(f"✅ {action}")
        else:
            generic = _strategies['product'][:2] + _strategies['pricing'][:1] + _strategies['marketing'][:1]
            for action in generic:
                st.markdown(f"✅ {action}")


# ============================================================================
# TARGET COMPANY OVERVIEW SECTION  (model-level)
# ============================================================================
elif section == "🏢 Target Overview":
    st.markdown(f'<h1 class="main-header">🏢 {target_company} — Model Overview</h1>', unsafe_allow_html=True)

    target_models = get_target_models(data['models'], target_company)

    if target_models.empty:
        st.warning(f"No model-level data found for {target_company}. Check amazon_sample.csv / flipkart.csv.")
    else:
        # ── Summary metrics ───────────────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        c1.metric("Models Listed", len(target_models))
        c2.metric("Price Range (Rs)", f"{target_models['price'].min():,.0f} – {target_models['price'].max():,.0f}")
        c3.metric("Rating Range", f"{target_models['rating'].min():.1f} – {target_models['rating'].max():.1f}")

        st.markdown("---")

        # ── Model table ───────────────────────────────────────────────────
        st.markdown("### 📋 All Models")
        st.dataframe(
            target_models[['laptop_name', 'brand', 'price', 'rating', 'review']]
            .rename(columns={'laptop_name': 'Model', 'brand': 'Brand',
                             'price': 'Price (Rs)', 'rating': 'Rating',
                             'review': 'Review Sample'})
            .reset_index(drop=True),
            use_container_width=True
        )

        st.markdown("---")

        # ── Per-model weakness & strength from reviews ────────────────────
        st.markdown("### 🔍 Model-Level Review Analysis")
        st.caption(f"Each model analysed using up to {COMMENTS_PER_MODEL} reviews for fair comparison.")

        for _, mrow in target_models.iterrows():
            model_name = mrow['laptop_name']
            reviews = get_model_reviews(data['models'], target_company, model_name)
            weaknesses = detect_model_weaknesses(reviews)
            strengths  = detect_model_strengths(reviews)

            with st.expander(f"📱 {target_company} {model_name}  |  Rs {mrow['price']:,.0f}  |  Rating: {mrow['rating']}"):
                wc, sc = st.columns(2)
                with wc:
                    st.markdown("**❌ Weakness Reasons**")
                    if weaknesses:
                        for label, count in list(weaknesses.items())[:5]:
                            st.error(f"{label} ({count} mentions)")
                    else:
                        st.success("No significant complaints found")
                with sc:
                    st.markdown("**✅ Strengths**")
                    if strengths:
                        for label, count in list(strengths.items())[:5]:
                            st.success(f"{label} ({count} mentions)")
                    else:
                        st.info("No strong praise signals found")

        # ── Specification-Based Competitor Comparison ─────────────────────
        st.markdown("---")
        st.markdown("### 🔬 Specification-Based Competitor Comparison")
        st.caption("Each target model is matched to competitor models in the same specification tier.")

        try:
            from model_groups import get_spec_peers, get_group_label, get_brand
        except ImportError:
            get_spec_peers = lambda m: []
            get_group_label = lambda m: "Ungrouped"
            get_brand = lambda m: "Unknown"

        for _, mrow in target_models.iterrows():
            t_model  = mrow['laptop_name']
            t_price  = mrow.get('price',  0)
            t_rating = mrow.get('rating', 0)
            peers    = get_spec_peers(t_model)
            group_lbl = get_group_label(t_model)

            with st.expander(f"🔍 Compare {fmt_model(target_company, t_model)} with Similar Specification Models  |  {group_lbl}"):
                if not peers:
                    st.info("No specification peers found for this model in the grouping file.")
                else:
                    # Build comparison rows from models_df where available
                    rows = [{
                        'Model':    fmt_model(target_company, t_model),
                        'Brand':    target_company,
                        'Price (Rs)': t_price,
                        'Rating':   t_rating,
                    }]
                    for peer in peers:
                        peer_name  = peer['model']
                        peer_brand = peer['brand']
                        # Try to find this peer in the loaded models data
                        match = data['models'][
                            data['models']['laptop_name'].str.lower().str.contains(
                                peer_name.split()[-1].lower(), na=False   # match on last word e.g. "G14"
                            ) |
                            data['models']['laptop_name'].str.lower().str.contains(
                                peer_name.lower()[:10], na=False
                            )
                        ]
                        if not match.empty:
                            r = match.iloc[0]
                            rows.append({
                                'Model':      r['laptop_name'],
                                'Brand':      r.get('brand', peer_brand),
                                'Price (Rs)': r.get('price',  0),
                                'Rating':     r.get('rating', 0),
                            })
                        else:
                            # Show peer from grouping file even without scraped data
                            rows.append({
                                'Model':      peer_name,
                                'Brand':      peer_brand,
                                'Price (Rs)': None,
                                'Rating':     None,
                            })

                    comp_df_spec = pd.DataFrame(rows)

                    # ── Comparison table ──────────────────────────────────
                    st.markdown("**📋 Comparison Table**")
                    st.dataframe(
                        comp_df_spec.style.format({
                            'Price (Rs)': lambda v: f"Rs {v:,.0f}" if pd.notna(v) and v else "N/A",
                            'Rating':     lambda v: f"{v:.1f}" if pd.notna(v) and v else "N/A",
                        }),
                        use_container_width=True
                    )

                    # ── Grouped bar chart (only rows with data) ───────────
                    chart_df = comp_df_spec.dropna(subset=['Price (Rs)', 'Rating'])
                    chart_df = chart_df[chart_df['Price (Rs)'] > 0]
                    if not chart_df.empty:
                        st.markdown("**📊 Price & Rating Comparison**")
                        # Normalise rating to same scale as price for dual display
                        fig_spec = px.bar(
                            chart_df,
                            x='Model', y='Price (Rs)',
                            color='Brand', text='Price (Rs)',
                            barmode='group',
                            title='Price Comparison (Rs)',
                            labels={'Price (Rs)': 'Price (Rs)', 'Model': 'Model'},
                            color_discrete_sequence=px.colors.qualitative.Set2,
                        )
                        fig_spec.update_traces(texttemplate='Rs %{text:,.0f}', textposition='outside')
                        fig_spec.update_layout(height=380, showlegend=True)
                        st.plotly_chart(fig_spec, use_container_width=True)

                        fig_rat = px.bar(
                            chart_df,
                            x='Model', y='Rating',
                            color='Brand', text='Rating',
                            barmode='group',
                            title='Rating Comparison',
                            labels={'Rating': 'Rating (out of 5)', 'Model': 'Model'},
                            color_discrete_sequence=px.colors.qualitative.Set2,
                        )
                        fig_rat.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                        fig_rat.update_layout(height=380, yaxis_range=[0, 5.5], showlegend=True)
                        st.plotly_chart(fig_rat, use_container_width=True)

                    # ── Auto insight line ─────────────────────────────────
                    st.markdown("**💡 Quick Insight**")
                    insights = []
                    for _, pr in comp_df_spec.iterrows():
                        if pr['Model'] == fmt_model(target_company, t_model):
                            continue
                        p_price  = pr.get('Price (Rs)')
                        p_rating = pr.get('Rating')
                        if pd.notna(p_price) and pd.notna(t_price) and t_price > 0 and p_price > 0:
                            pdiff = t_price - p_price
                            rdiff = (p_rating or 0) - (t_rating or 0)
                            if pdiff > 500:
                                rating_note = (
                                    f" while maintaining a slightly higher rating ({p_rating:.1f} vs {t_rating:.1f})"
                                    if rdiff > 0.05 else ""
                                )
                                insights.append(
                                    f"🔴 {pr['Model']} is ₹{pdiff:,.0f} cheaper than "
                                    f"{fmt_model(target_company, t_model)}{rating_note}."
                                )
                            elif pdiff < -500:
                                insights.append(
                                    f"🟢 {fmt_model(target_company, t_model)} is ₹{abs(pdiff):,.0f} cheaper than {pr['Model']}."
                                )
                    if insights:
                        for ins in insights:
                            st.markdown(ins)
                    else:
                        st.info("Prices are similar across spec-matched models — no significant gap detected.")

# ============================================================================
# COMPETITOR ADVANTAGES SECTION
# ============================================================================
elif section == "⚔️ Competitor Advantages":
    st.markdown(f'<h1 class="main-header">⚔️ Competitor Advantages vs {target_company}</h1>', unsafe_allow_html=True)
    st.markdown(f"Model-level and aspect-based areas where competitors outperform **{target_company}**")

    advantages = detect_competitor_advantages(target_company, filtered_comp, data['sentiment'])

    if not advantages:
        st.success(f"No significant competitor advantages detected against {target_company} at the model level.")
    else:
        adv_df = pd.DataFrame(advantages)

        # ── Summary metrics ───────────────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Advantages Found", len(adv_df))
        c2.metric("High Severity", len(adv_df[adv_df['Severity'] == 'High']))
        c3.metric("Competitors Ahead", adv_df['Competitor'].nunique())

        st.markdown("---")

        # ── Model-level advantage cards ───────────────────────────────────
        st.markdown("### 🔍 Model-Level Competitor Advantages")
        st.caption("Each insight compares a specific competitor model against a specific target model.")

        for competitor in adv_df['Competitor'].unique():
            c_adv = adv_df[adv_df['Competitor'] == competitor]
            high_count = len(c_adv[c_adv['Severity'] == 'High'])
            with st.expander(f"⚠️ {competitor} — {len(c_adv)} advantage(s), {high_count} high severity"):
                for _, row in c_adv.iterrows():
                    icon = "🔴" if row['Severity'] == 'High' else "🟡"
                    c_model = row.get('Competitor_Model', competitor)
                    t_model = row.get('Target_Model', target_company)
                    st.markdown(
                        f"{icon} **{c_model}** — {row['Advantage']} over **{t_model}**  \n"
                        f"&nbsp;&nbsp;&nbsp;&nbsp;_{row['Detail']}_"
                    )

        st.markdown("---")

        # ── Advantages by aspect type bar chart ───────────────────────────
        st.markdown("### 📈 Advantages by Aspect")
        # Strip "(Feature)" / "(Fewer Complaints)" suffix for grouping
        adv_df['Aspect'] = adv_df['Advantage'].str.replace(
            r'\s*\(.*\)', '', regex=True).str.strip()
        type_counts = adv_df['Aspect'].value_counts().reset_index()
        type_counts.columns = ['Aspect', 'Count']
        fig_types = px.bar(
            type_counts, x='Aspect', y='Count', color='Aspect',
            title=f'Competitor Advantages by Aspect vs {target_company}',
            labels={'Count': 'Number of Advantages', 'Aspect': 'Aspect'},
            text='Count',
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_types.update_traces(textposition='outside')
        fig_types.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_types, use_container_width=True)

        # ── Full table ────────────────────────────────────────────────────
        st.markdown("### 📋 Full Advantages Table")
        display_cols = ['Competitor_Model', 'Target_Model', 'Advantage', 'Detail', 'Severity']
        display_cols = [c for c in display_cols if c in adv_df.columns]

        def highlight_severity(row):
            color = '#ffcccc' if row['Severity'] == 'High' else '#fff3cd'
            return [f'background-color: {color}'] * len(row)

        st.dataframe(
            adv_df[display_cols].style.apply(highlight_severity, axis=1),
            use_container_width=True
        )


# ============================================================================
# STRENGTHS & WEAKNESSES SECTION
# ============================================================================
elif section == "💪 Strengths & Weaknesses":
    st.markdown(f'<h1 class="main-header">💪 {target_company} — Strengths & Weaknesses</h1>', unsafe_allow_html=True)

    weaknesses = detect_target_weaknesses(target_company, filtered_comp, data['sentiment'], data['negative_kw'])
    strengths  = detect_target_strengths(target_company,  filtered_comp, data['sentiment'], data['positive_kw'])

    # ── Summary row ───────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Strengths Found",  len(strengths))
    c2.metric("Weaknesses Found", len(weaknesses))
    high_s = len([s for s in strengths  if s['Impact']   == 'High'])
    high_w = len([w for w in weaknesses if w['Severity'] == 'High'])
    c3.metric("High-Impact Strengths",  high_s)
    c4.metric("High-Severity Weaknesses", high_w)

    st.markdown("---")

    col_s, col_w = st.columns(2)

    # ── Strengths ─────────────────────────────────────────────────────────
    with col_s:
        st.markdown("### ✅ Strengths")
        if not strengths:
            st.info("No significant strengths detected yet.")
        else:
            for s in strengths:
                icon = "🟢" if s['Impact'] == 'High' else "🔵"
                st.success(f"{icon} **{s['Strength']}**\n\n_{s['Source']}_ — {s['Detail']}")

    # ── Weaknesses ────────────────────────────────────────────────────────
    with col_w:
        st.markdown("### ❌ Weaknesses")
        if not weaknesses:
            st.info("No significant weaknesses detected.")
        else:
            for w in weaknesses:
                icon = "🔴" if w['Severity'] == 'High' else "🟡"
                st.error(f"{icon} **{w['Weakness']}**\n\n_{w['Source']}_ — {w['Detail']}")

    st.markdown("---")

    # ── Strengths bar chart ───────────────────────────────────────────────
    if strengths:
        st.markdown("### 📊 Strengths by Source")
        s_df = pd.DataFrame(strengths)
        s_src = s_df['Source'].value_counts().reset_index()
        s_src.columns = ['Source', 'Count']
        fig_s = px.bar(
            s_src, x='Source', y='Count',
            color='Source', text='Count',
            title=f'{target_company} Strengths by Source',
            color_discrete_sequence=['#2ecc71', '#27ae60', '#1abc9c', '#16a085']
        )
        fig_s.update_traces(textposition='outside')
        fig_s.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig_s, use_container_width=True)

    # ── Weaknesses bar chart ──────────────────────────────────────────────
    if weaknesses:
        st.markdown("### 📊 Weaknesses by Source")
        w_df = pd.DataFrame(weaknesses)
        w_src = w_df['Source'].value_counts().reset_index()
        w_src.columns = ['Source', 'Count']
        fig_w = px.bar(
            w_src, x='Source', y='Count',
            color='Source', text='Count',
            title=f'{target_company} Weaknesses by Source',
            color_discrete_sequence=['#e74c3c', '#c0392b', '#e67e22', '#d35400']
        )
        fig_w.update_traces(textposition='outside')
        fig_w.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig_w, use_container_width=True)

    # ── SWOT-style summary table ──────────────────────────────────────────
    st.markdown("### 🗂️ SWOT-Style Summary")
    max_rows = max(len(strengths), len(weaknesses), 1)
    swot_data = {
        'Strengths': [s['Strength'] for s in strengths] + [''] * (max_rows - len(strengths)),
        'Weaknesses': [w['Weakness'] for w in weaknesses] + [''] * (max_rows - len(weaknesses)),
    }
    st.dataframe(pd.DataFrame(swot_data), use_container_width=True)


# ============================================================================
# STRATEGY RECOMMENDATIONS SECTION  (model-specific)
# ============================================================================
elif section == "🧠 Strategy Recommendations":
    st.markdown(f'<h1 class="main-header">🧠 {target_company} — Strategy Recommendations</h1>', unsafe_allow_html=True)

    weaknesses = detect_target_weaknesses(target_company, filtered_comp, data['sentiment'], data['negative_kw'])
    strengths  = detect_target_strengths(target_company,  filtered_comp, data['sentiment'], data['positive_kw'])
    advantages = detect_competitor_advantages(target_company, filtered_comp, data['sentiment'])

    strategies = generate_all_strategies(
        target_company, weaknesses, strengths, advantages,
        data['negative_kw'], data['opportunities']
    )

    # ── Model-specific strategic actions ─────────────────────────────────
    model_actions = model_strategic_actions(target_company, data['models'], data['negative_kw'])

    st.markdown("### 🎯 Model-Specific Recommended Actions")
    if model_actions:
        for action in model_actions:
            st.warning(f"• {action}")
    else:
        st.info("No model-level data available. Add amazon_sample.csv or flipkart.csv for model-specific recommendations.")

    st.markdown("---")

    # ── Category strategies ───────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("Product Strategies",   len(strategies['product']))
    c2.metric("Pricing Strategies",   len(strategies['pricing']))
    c3.metric("Marketing Strategies", len(strategies['marketing']))

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔧 Product Strategy")
        for item in strategies['product']:
            st.info(f"• {item}")
    with col2:
        st.markdown("### 💰 Pricing Strategy")
        for item in strategies['pricing']:
            st.warning(f"• {item}")
    with col3:
        st.markdown("### 📣 Marketing Strategy")
        for item in strategies['marketing']:
            st.success(f"• {item}")

    st.markdown("---")

    # ── Full strategy table ───────────────────────────────────────────────
    st.markdown("### 📋 All Strategies")
    all_rows = (
        [{'Category': 'Model-Specific', 'Strategy': s} for s in model_actions] +
        [{'Category': 'Product',        'Strategy': s} for s in strategies['product']] +
        [{'Category': 'Pricing',        'Strategy': s} for s in strategies['pricing']] +
        [{'Category': 'Marketing',      'Strategy': s} for s in strategies['marketing']]
    )
    st.dataframe(pd.DataFrame(all_rows), use_container_width=True)


# ============================================================================
# MARKET OPPORTUNITY INSIGHTS SECTION
# ============================================================================
elif section == "🌍 Market Opportunity Insights":
    st.markdown(f'<h1 class="main-header">🌍 Market Opportunity Insights</h1>', unsafe_allow_html=True)
    st.markdown(f"Trending topics from Reddit & YouTube discussions — opportunities for **{target_company}**")

    if data['opportunities'].empty:
        st.warning("No opportunity data found. Run step7_opportunity_detection.py first.")
    else:
        opp_df = data['opportunities'].copy()

        # ── Summary metrics ───────────────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        c1.metric("Opportunities Detected", len(opp_df))
        c2.metric("Total Mentions", int(opp_df['Mentions'].sum()))
        c3.metric("Top Opportunity", opp_df.iloc[0]['Opportunity'])

        st.markdown("---")

        # ── Horizontal bar chart ──────────────────────────────────────────
        st.markdown("### 🔥 Trending Market Opportunities")
        fig_opp = px.bar(
            opp_df.sort_values('Mentions'),
            x='Mentions', y='Opportunity',
            orientation='h',
            color='Mentions',
            color_continuous_scale='Viridis',
            text='Mentions',
            title='Market Opportunities by Mention Count (Reddit + YouTube)',
            labels={'Mentions': 'Mentions', 'Opportunity': 'Opportunity'}
        )
        fig_opp.update_traces(textposition='outside')
        fig_opp.update_layout(height=500)
        st.plotly_chart(fig_opp, use_container_width=True)

        # ── Pie chart ─────────────────────────────────────────────────────
        st.markdown("### 🥧 Opportunity Share")
        fig_pie = px.pie(
            opp_df, values='Mentions', names='Opportunity',
            title='Share of Discussion by Opportunity',
            hole=0.4
        )
        fig_pie.update_layout(height=450)
        st.plotly_chart(fig_pie, use_container_width=True)

        # ── Opportunity cards ─────────────────────────────────────────────
        st.markdown("### 💡 Opportunity Breakdown")
        total_mentions = opp_df['Mentions'].sum()
        cols = st.columns(2)
        for i, (_, row) in enumerate(opp_df.iterrows()):
            with cols[i % 2]:
                pct = row.get('Percentage', round(row['Mentions'] / total_mentions * 100, 1) if total_mentions else 0)
                st.info(f"**{row['Opportunity']}**\n\n{row['Mentions']} mentions — {pct}% of discussions")

        # ── Actionable recommendations for target ─────────────────────────
        st.markdown("---")
        st.markdown(f"### 🎯 How {target_company} Can Capitalise")
        top3 = opp_df.head(3)
        for _, row in top3.iterrows():
            opp_lower = row['Opportunity'].lower()
            if 'gaming' in opp_lower:
                tip = f"Launch a dedicated gaming laptop line with high-refresh displays and RGB branding."
            elif 'battery' in opp_lower or 'lightweight' in opp_lower:
                tip = f"Develop ultra-slim models with 15+ hour battery life targeting mobile professionals."
            elif 'ai' in opp_lower or 'creator' in opp_lower:
                tip = f"Introduce AI-optimised or creator-focused SKUs with dedicated NPU/GPU."
            elif 'budget' in opp_lower or 'student' in opp_lower:
                tip = f"Release a budget-friendly lineup targeting students and first-time buyers."
            else:
                tip = f"Invest in R&D and marketing for the {row['Opportunity']} segment."
            st.success(f"**{row['Opportunity']}** ({row['Mentions']} mentions)\n\n{tip}")


# ============================================================================
# COMPETITOR COMPARISON SECTION  (model-level)
# ============================================================================
elif section == "🆚 Competitor Comparison":
    st.markdown(f'<h1 class="main-header">🆚 {target_company} vs Competitors — Model Level</h1>', unsafe_allow_html=True)

    if data['models'].empty:
        st.warning("No model-level data found.")
    else:
        cmp_df = build_model_comparison(data['models'], target_company, competitors)

        if cmp_df.empty:
            st.warning("No models found for selected brands.")
        else:
            # ── Model comparison table ────────────────────────────────────
            st.markdown("### 📋 Brand — Model Comparison Table")
            st.dataframe(
                cmp_df[['model_label', 'brand', 'price', 'rating', 'type']]
                .rename(columns={'model_label': 'Brand — Model', 'brand': 'Brand',
                                 'price': 'Price (Rs)', 'rating': 'Rating', 'type': 'Type'})
                .reset_index(drop=True),
                use_container_width=True
            )

            st.markdown("---")

            # ── Price comparison ──────────────────────────────────────────
            st.markdown("### 💰 Price Comparison by Model")
            fig_price = px.bar(
                cmp_df.sort_values('price', ascending=False),
                x='model_label', y='price', color='type',
                color_discrete_map={'Target': '#e74c3c', 'Competitor': '#3498db'},
                text='price',
                title=f'Price per Model — {target_company} vs Competitors',
                labels={'model_label': 'Brand — Model', 'price': 'Price (Rs)'}
            )
            fig_price.update_traces(texttemplate='Rs %{text:,.0f}', textposition='outside')
            fig_price.update_layout(height=460, xaxis_tickangle=-30)
            st.plotly_chart(fig_price, use_container_width=True)

            # ── Rating comparison ─────────────────────────────────────────
            st.markdown("### ⭐ Rating Comparison by Model")
            fig_rating = px.bar(
                cmp_df.sort_values('rating', ascending=False),
                x='model_label', y='rating', color='type',
                color_discrete_map={'Target': '#e74c3c', 'Competitor': '#3498db'},
                text='rating',
                title=f'Rating per Model — {target_company} vs Competitors',
                labels={'model_label': 'Brand — Model', 'rating': 'Rating'}
            )
            fig_rating.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_rating.update_layout(height=460, yaxis_range=[0, 5.5], xaxis_tickangle=-30)
            st.plotly_chart(fig_rating, use_container_width=True)

            # ── Model weakness reasons per target model ───────────────────
            st.markdown("---")
            st.markdown(f"### 🔍 {target_company} Model Weakness Reasons")
            target_models = get_target_models(data['models'], target_company)
            for _, mrow in target_models.iterrows():
                model_name = mrow['laptop_name']
                reviews = get_model_reviews(data['models'], target_company, model_name)
                weaknesses = detect_model_weaknesses(reviews)
                with st.expander(f"{target_company} {model_name} — Weakness Analysis"):
                    if weaknesses:
                        for label, count in list(weaknesses.items())[:6]:
                            st.error(f"• {label} ({count} keyword hits)")
                    else:
                        st.success("No significant complaints detected in reviews.")

            # ── Radar: price + rating normalised ─────────────────────────
            st.markdown("---")
            st.markdown("### 🕸️ Multi-Metric Radar — Model Level")
            if len(cmp_df) > 1:
                def norm(s):
                    mn, mx = s.min(), s.max()
                    return (s - mn) / (mx - mn) if mx != mn else s * 0
                radar = cmp_df[['model_label', 'price', 'rating', 'type']].copy()
                radar['price_n']  = norm(radar['price'])
                radar['rating_n'] = norm(radar['rating'])
                fig_radar = go.Figure()
                for _, row in radar.iterrows():
                    color = '#e74c3c' if row['type'] == 'Target' else '#3498db'
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[row['price_n'], row['rating_n']],
                        theta=['Price', 'Rating'],
                        fill='toself', name=row['model_label'], line_color=color
                    ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    title=f'Normalised Price & Rating — All Models',
                    height=500
                )
                st.plotly_chart(fig_radar, use_container_width=True)


# ============================================================================
# MARKET OVERVIEW SECTION  (model-level)
# ============================================================================
elif section == "📈 Market Overview":
    st.markdown('<h1 class="main-header">📈 Market Overview — Model Level</h1>', unsafe_allow_html=True)
    st.markdown(f"**{target_company}** models vs competitor models ({', '.join(competitors)})")

    if data['models'].empty:
        st.warning("No model-level data found. Ensure amazon_sample.csv or flipkart.csv exist.")
    else:
        cmp_df = build_model_comparison(data['models'], target_company, competitors)

        if cmp_df.empty:
            st.warning("No models found for selected brands.")
        else:
            # ── Full model comparison table ───────────────────────────────
            st.markdown("### 📋 Model Comparison Table")
            st.dataframe(
                cmp_df[['model_label', 'brand', 'price', 'rating', 'type']]
                .rename(columns={'model_label': 'Brand — Model', 'brand': 'Brand',
                                 'price': 'Price (Rs)', 'rating': 'Rating', 'type': 'Type'})
                .reset_index(drop=True),
                use_container_width=True
            )

            st.markdown("---")

            # ── Price by model chart ──────────────────────────────────────
            st.markdown("### 💰 Price Comparison by Model")
            fig_mp = px.bar(
                cmp_df.sort_values('price', ascending=False),
                x='model_label', y='price',
                color='type',
                color_discrete_map={'Target': '#e74c3c', 'Competitor': '#3498db'},
                text='price',
                title=f'Price per Model — {target_company} vs Competitors',
                labels={'model_label': 'Brand — Model', 'price': 'Price (Rs)', 'type': 'Type'}
            )
            fig_mp.update_traces(texttemplate='Rs %{text:,.0f}', textposition='outside')
            fig_mp.update_layout(height=480, xaxis_tickangle=-30, showlegend=True)
            st.plotly_chart(fig_mp, use_container_width=True)

            # ── Rating by model chart ─────────────────────────────────────
            st.markdown("### ⭐ Rating Comparison by Model")
            fig_mr = px.bar(
                cmp_df.sort_values('rating', ascending=False),
                x='model_label', y='rating',
                color='type',
                color_discrete_map={'Target': '#e74c3c', 'Competitor': '#3498db'},
                text='rating',
                title=f'Rating per Model — {target_company} vs Competitors',
                labels={'model_label': 'Brand — Model', 'rating': 'Rating', 'type': 'Type'}
            )
            fig_mr.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_mr.update_layout(height=480, yaxis_range=[0, 5.5], xaxis_tickangle=-30)
            st.plotly_chart(fig_mr, use_container_width=True)

            # ── Price vs Rating scatter ───────────────────────────────────
            st.markdown("### 📊 Price vs Rating — All Models")
            fig_sc = px.scatter(
                cmp_df, x='price', y='rating',
                color='type', text='model_label',
                color_discrete_map={'Target': '#e74c3c', 'Competitor': '#3498db'},
                title=f'Price vs Rating — {target_company} vs Competitors',
                labels={'price': 'Price (Rs)', 'rating': 'Rating', 'type': 'Type'},
                hover_data=['brand', 'laptop_name', 'price', 'rating']
            )
            fig_sc.update_traces(textposition='top center')
            fig_sc.update_layout(height=520)
            st.plotly_chart(fig_sc, use_container_width=True)

            # ── Model leaders ─────────────────────────────────────────────
            st.markdown("### 🏆 Model Leaders")
            c1, c2, c3 = st.columns(3)
            most_exp = cmp_df.loc[cmp_df['price'].idxmax()]
            best_rat = cmp_df.loc[cmp_df['rating'].idxmax()]
            best_val = cmp_df.loc[(cmp_df['rating'] / cmp_df['price'].replace(0, float('nan'))).idxmax()]
            c1.success(f"Most Expensive\n\n{most_exp['model_label']}\n\nRs {most_exp['price']:,.0f}")
            c2.success(f"Best Rated\n\n{best_rat['model_label']}\n\n{best_rat['rating']:.1f}/5.0")
            c3.success(f"Best Value\n\n{best_val['model_label']}\n\nRs {best_val['price']:,.0f} @ {best_val['rating']:.1f}")


# ============================================================================
# SENTIMENT ANALYSIS SECTION
# ============================================================================
elif section == "😊 Sentiment Analysis":
    st.markdown('<h1 class="main-header">😊 Sentiment Analysis</h1>', unsafe_allow_html=True)
    st.markdown(f"Sentiment for **{target_company}** vs {', '.join(competitors)}")

    if data['sentiment'].empty:
        st.warning("⚠️ No sentiment data available. Please run Step 2 analysis first.")
    else:
        # Use pre-split filtered data from Step 3
        df_filtered = filtered_sent.copy() if not filtered_sent.empty else data['sentiment'].copy()
        # Overall Sentiment
        st.markdown("### 📊 Overall Sentiment Distribution")

        # Parse percentages
        df_filtered['Positive_Pct'] = df_filtered['Positive'].str.rstrip('%').astype(float)
        df_filtered['Negative_Pct'] = df_filtered['Negative'].str.rstrip('%').astype(float)
        df_filtered['Neutral_Pct']  = df_filtered['Neutral'].str.rstrip('%').astype(float)

        # Stacked bar chart
        fig_sentiment = go.Figure()

        fig_sentiment.add_trace(go.Bar(
            name='Positive',
            x=df_filtered['Brand'],
            y=df_filtered['Positive_Pct'],
            marker_color='#2ecc71'
        ))

        fig_sentiment.add_trace(go.Bar(
            name='Neutral',
            x=df_filtered['Brand'],
            y=df_filtered['Neutral_Pct'],
            marker_color='#95a5a6'
        ))

        fig_sentiment.add_trace(go.Bar(
            name='Negative',
            x=df_filtered['Brand'],
            y=df_filtered['Negative_Pct'],
            marker_color='#e74c3c'
        ))

        fig_sentiment.update_layout(
            barmode='stack',
            title=f'Sentiment Distribution — {target_company} vs Competitors',
            xaxis_title='Brand',
            yaxis_title='Percentage (%)',
            height=500
        )

        st.plotly_chart(fig_sentiment, use_container_width=True)

        # Brand Sentiment Cards
        st.markdown("### 🎯 Brand Sentiment Breakdown")

        for idx, row in df_filtered.iterrows():
            with st.expander(f"📊 {row['Brand']} - Sentiment Details"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("✅ Positive", row['Positive'])
                
                with col2:
                    st.metric("⚪ Neutral", row['Neutral'])
                
                with col3:
                    st.metric("❌ Negative", row['Negative'])
                
                # Sentiment score
                sentiment_score = row['Positive_Pct'] - row['Negative_Pct']
                if sentiment_score > 50:
                    st.success(f"🎉 Excellent sentiment score: +{sentiment_score:.1f}%")
                elif sentiment_score > 0:
                    st.info(f"👍 Good sentiment score: +{sentiment_score:.1f}%")
                else:
                    st.warning(f"⚠️ Needs improvement: {sentiment_score:.1f}%")


# ============================================================================
# CUSTOMER COMPLAINTS SECTION
# ============================================================================
elif section == "⚠️ Customer Complaints":
    st.markdown('<h1 class="main-header">⚠️ Customer Complaint Keywords</h1>', unsafe_allow_html=True)
    
    if data['negative_kw'].empty:
        st.warning("⚠️ No complaint data available. Please run Step 3 analysis first.")
    else:
        st.markdown("### 🔴 Top Customer Issues")
        
        # Top complaints bar chart
        top_complaints = data['negative_kw'].head(10)
        
        fig_complaints = px.bar(
            top_complaints,
            x='Count',
            y='Keyword',
            orientation='h',
            title='Top 10 Customer Complaints',
            labels={'Count': 'Number of Mentions', 'Keyword': 'Issue'},
            color='Count',
            color_continuous_scale='Reds'
        )
        fig_complaints.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_complaints, use_container_width=True)
        
        # Issue categories
        st.markdown("### 📋 Issue Categories")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔋 Hardware Issues")
            hardware_issues = []
            for idx, row in top_complaints.iterrows():
                keyword = row['Keyword'].lower()
                if any(word in keyword for word in ['battery', 'fan', 'heating', 'screen', 'keyboard']):
                    hardware_issues.append(f"• **{row['Keyword']}**: {row['Count']} mentions")
            
            if hardware_issues:
                for issue in hardware_issues:
                    st.markdown(issue)
            else:
                st.info("No major hardware issues detected")
        
        with col2:
            st.markdown("#### ⚡ Performance Issues")
            performance_issues = []
            for idx, row in top_complaints.iterrows():
                keyword = row['Keyword'].lower()
                if any(word in keyword for word in ['slow', 'lag', 'performance', 'speed', 'ram']):
                    performance_issues.append(f"• **{row['Keyword']}**: {row['Count']} mentions")
            
            if performance_issues:
                for issue in performance_issues:
                    st.markdown(issue)
            else:
                st.info("No major performance issues detected")
        
        # Action items
        st.markdown("### 🎯 Recommended Actions")
        
        st.error("**High Priority Issues:**")
        for idx, row in top_complaints.head(3).iterrows():
            st.markdown(f"- Address **{row['Keyword']}** ({row['Count']} mentions)")


# ============================================================================
# SOCIAL MEDIA INSIGHTS SECTION
# ============================================================================
elif section == "💬 Social Media Insights":
    st.markdown('<h1 class="main-header">💬 Social Media Insights</h1>', unsafe_allow_html=True)
    
    st.markdown("### 📱 Reddit + YouTube Discussion Analysis")
    
    # Trending Topics
    if not data['opportunities'].empty:
        st.markdown("#### 🔥 Trending Topics")
        
        fig_trending = px.bar(
            data['opportunities'].head(10),
            x='Mentions',
            y='Opportunity',
            orientation='h',
            title='Top Trending Topics from Social Media',
            labels={'Mentions': 'Number of Mentions', 'Opportunity': 'Topic'},
            color='Mentions',
            color_continuous_scale='Viridis'
        )
        fig_trending.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_trending, use_container_width=True)
        
        # Topic breakdown
        st.markdown("#### 📊 Topic Distribution")
        
        fig_pie = px.pie(
            data['opportunities'].head(8),
            values='Mentions',
            names='Opportunity',
            title='Discussion Topic Distribution'
        )
        fig_pie.update_layout(height=500)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Positive keywords
    if not data['positive_kw'].empty:
        st.markdown("#### ✅ Most Praised Features")
        
        col1, col2, col3 = st.columns(3)
        
        top_positive = data['positive_kw'].head(9)
        for idx, (i, row) in enumerate(top_positive.iterrows()):
            with [col1, col2, col3][idx % 3]:
                st.success(f"**{row['Keyword']}**\n\n{row['Count']} mentions")
    
    # Key insights
    st.markdown("### 💡 Key Insights from Social Media")
    
    if not data['opportunities'].empty:
        top_3 = data['opportunities'].head(3)
        
        for idx, row in top_3.iterrows():
            st.info(f"**{row['Opportunity']}** is trending with {row['Mentions']} mentions ({row['Percentage']}%)")


# ============================================================================
# COMPETITIVE STRATEGY SECTION
# ============================================================================
elif section == "🎯 Competitive Strategy":
    st.markdown('<h1 class="main-header">🎯 Competitive Strategy</h1>', unsafe_allow_html=True)
    
    if data['strategies'].empty:
        st.warning("⚠️ No strategy data available. Please run Step 6 analysis first.")
    else:
        st.markdown("### 🤖 AI-Generated Strategy Suggestions")
        
        # Brand selector — default to target_company
        available_brands = data['strategies']['Brand'].tolist()
        default_idx = available_brands.index(target_company) if target_company in available_brands else 0
        selected_brand = st.selectbox(
            "Select a brand to view strategy:",
            available_brands,
            index=default_idx
        )
        
        brand_strategy = data['strategies'][data['strategies']['Brand'] == selected_brand].iloc[0]
        
        st.markdown(f"## 📊 {selected_brand} Strategy")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Competitor Advantages", brand_strategy['Competitor_Advantages'])
        
        with col2:
            st.metric("Action Items", brand_strategy['Action_Items'])
        
        with col3:
            st.metric("Strategy Keywords", len(brand_strategy['Strategy_Keywords'].split(',')))
        
        # Strategy Keywords
        st.markdown("### 🎯 Strategy Keywords")
        
        keywords = brand_strategy['Strategy_Keywords'].split(',')
        cols = st.columns(3)
        
        for idx, keyword in enumerate(keywords):
            with cols[idx % 3]:
                st.info(f"**{keyword.strip()}**")
        
        # Detailed recommendations
        st.markdown("### 📋 Detailed Recommendations")
        
        # Load detailed strategy from report if available
        try:
            with open('competitive_strategies_report.txt', 'r', encoding='utf-8') as f:
                report = f.read()
                
                # Extract brand section
                brand_section_start = report.find(f"{selected_brand.upper()} STRATEGY")
                if brand_section_start != -1:
                    brand_section_end = report.find("=" * 70, brand_section_start + 1)
                    brand_section = report[brand_section_start:brand_section_end]
                    
                    st.text_area("Strategy Details", brand_section, height=400)
        except:
            st.info("Detailed strategy report not available")
        
        # All brands comparison
        st.markdown("### 📊 All Brands Strategy Overview")
        
        fig_strategies = px.bar(
            data['strategies'],
            x='Brand',
            y='Competitor_Advantages',
            title='Competitor Advantages by Brand',
            labels={'Competitor_Advantages': 'Number of Advantages', 'Brand': 'Brand'},
            color='Competitor_Advantages',
            color_continuous_scale='Oranges'
        )
        fig_strategies.update_layout(height=400)
        st.plotly_chart(fig_strategies, use_container_width=True)

# ============================================================================
# RAG CHAT SECTION
# ============================================================================
elif section == "🤖 Ask AI (RAG)":
    st.markdown('<h1 class="main-header">🤖 Ask AI — Market Intelligence Chat</h1>', unsafe_allow_html=True)
    st.markdown("Ask any question about the laptop market data. The AI retrieves relevant insights from all analysis results.")

    # Lazy import so other sections load fast
    try:
        from rag_engine import ask, rebuild_index, get_rag_components

        # Initialise index once per session
        with st.spinner("🔄 Loading AI model and knowledge base..."):
            try:
                get_rag_components()
                st.success("✅ AI ready — knowledge base loaded!")
            except Exception as e:
                st.error(f"❌ Could not load RAG engine: {e}")
                st.info("Make sure you have run all analysis steps (1–7) first.")
                st.stop()

        # Rebuild button
        if st.button("🔄 Rebuild Knowledge Base"):
            with st.spinner("Rebuilding index from latest analysis data..."):
                n = rebuild_index()
            st.success(f"✅ Index rebuilt with {n} document chunks!")

        st.markdown("---")

        # Suggested questions
        st.markdown("### 💡 Suggested Questions")
        suggestions = [
            "Which brand has the best rating?",
            "What are the top customer complaints?",
            "What strategy should HP follow?",
            "Which laptop segment is growing fastest?",
            "What do customers say about battery life?",
            "Which brand offers the best value for money?",
            "What are the main issues with gaming laptops?",
            "What strategy should Lenovo follow to beat Dell?",
        ]

        cols = st.columns(4)
        for i, suggestion in enumerate(suggestions):
            if cols[i % 4].button(suggestion, key=f"sug_{i}"):
                st.session_state['rag_query'] = suggestion

        st.markdown("---")

        # Chat interface
        st.markdown("### 💬 Chat with Your Data")

        # Initialise chat history
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []

        # Pre-fill from suggestion click
        default_query = st.session_state.pop('rag_query', '')

        user_input = st.text_input(
            "Ask a question about the laptop market:",
            value=default_query,
            placeholder="e.g. Which brand has the best battery reviews?",
            key="rag_input"
        )

        col_ask, col_clear = st.columns([1, 5])
        ask_clicked   = col_ask.button("🔍 Ask", type="primary")
        clear_clicked = col_clear.button("🗑️ Clear History")

        if clear_clicked:
            st.session_state['chat_history'] = []
            st.rerun()

        if ask_clicked and user_input.strip():
            with st.spinner("🤔 Searching knowledge base..."):
                answer, chunks = ask(user_input)

            st.session_state['chat_history'].append({
                'question': user_input,
                'answer': answer,
                'sources': chunks
            })

        # Display chat history (newest first)
        for entry in reversed(st.session_state['chat_history']):
            st.markdown(f"**🙋 You:** {entry['question']}")
            st.markdown(f"**🤖 AI:** {entry['answer']}")

            with st.expander("📄 View retrieved sources"):
                for i, chunk in enumerate(entry['sources'], 1):
                    st.markdown(f"**Source {i}** (relevance: {chunk['score']:.3f})")
                    st.text(chunk['text'][:300])
                    st.markdown("---")

            st.markdown("---")

    except ImportError:
        st.error("❌ RAG dependencies not installed.")
        st.code("pip install sentence-transformers faiss-cpu", language="bash")
        st.info("Run the command above, then restart the dashboard.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>Laptop Market Analysis Dashboard | Powered by AI & Data Analytics</p>
    <p>Data Sources: Amazon, Flipkart, Reddit, YouTube</p>
</div>
""", unsafe_allow_html=True)
