"""
Strategy Recommendation Engine
Generates Product, Pricing, and Marketing strategies based on analysis data.
"""

# ── Strategy templates keyed by weakness/advantage type ──────────────────────

PRODUCT_STRATEGIES = {
    'battery':      'Improve battery optimization and capacity',
    'thermal':      'Improve cooling system and thermal management',
    'heating':      'Improve cooling system and thermal management',
    'fan':          'Reduce fan noise with better thermal design',
    'ram':          'Offer higher RAM configurations as standard',
    'performance':  'Upgrade CPU/GPU options for better performance',
    'display':      'Improve display quality and refresh rate',
    'keyboard':     'Improve keyboard feel and key travel',
    'build':        'Improve build quality and chassis materials',
    'camera':       'Upgrade webcam resolution and quality',
    'weight':       'Reduce chassis weight for better portability',
    'slow':         'Optimize software and storage for faster boot times',
    'default':      'Focus on overall product quality improvements',
}

PRICING_STRATEGIES = {
    'Higher Price Segment':     ['Reduce mid-range pricing', 'Offer competitive bundles', 'Introduce entry-level SKUs'],
    'Lower Price Segment':      ['Justify premium with added features', 'Introduce premium tier products'],
    'Better Value':             ['Match competitor value-for-money ratio', 'Bundle accessories to increase perceived value'],
    'Lower Price':              ['Introduce budget-friendly variants', 'Offer seasonal discounts and trade-in programs'],
    'default':                  ['Review pricing strategy across all segments', 'Offer flexible EMI and financing options'],
}

MARKETING_STRATEGIES = {
    'gaming':       'Focus marketing on gaming performance and FPS benchmarks',
    'display':      'Promote display quality and high refresh rate screens',
    'battery':      'Market long battery life for on-the-go users',
    'lightweight':  'Promote portability and slim design',
    'creator':      'Target content creators with editing performance campaigns',
    'student':      'Run student discount campaigns and education bundles',
    'business':     'Promote reliability and enterprise support',
    'performance':  'Highlight benchmark scores in performance marketing',
    'build':        'Showcase premium build quality in unboxing campaigns',
    'default':      'Increase brand visibility through social media and influencer reviews',
}


def generate_product_strategies(weaknesses, neg_keywords):
    """Generate product strategies from weaknesses and negative keywords."""
    strategies = set()

    # From weaknesses
    for w in weaknesses:
        text = w.get('Weakness', '').lower()
        for key, strategy in PRODUCT_STRATEGIES.items():
            if key in text:
                strategies.add(strategy)

    # From negative keywords
    for _, row in neg_keywords.iterrows() if hasattr(neg_keywords, 'iterrows') else []:
        kw = str(row.get('Keyword', '')).lower()
        for key, strategy in PRODUCT_STRATEGIES.items():
            if key in kw:
                strategies.add(strategy)

    if not strategies:
        strategies.add(PRODUCT_STRATEGIES['default'])

    return sorted(strategies)


def generate_pricing_strategies(weaknesses, advantages):
    """Generate pricing strategies from detected weaknesses and competitor advantages."""
    strategies = set()

    for w in weaknesses:
        weakness_text = w.get('Weakness', '')
        for key, strats in PRICING_STRATEGIES.items():
            if key.lower() in weakness_text.lower():
                strategies.update(strats)

    for a in advantages:
        adv_text = a.get('Advantage', '')
        for key, strats in PRICING_STRATEGIES.items():
            if key.lower() in adv_text.lower():
                strategies.update(strats)

    if not strategies:
        strategies.update(PRICING_STRATEGIES['default'])

    return sorted(strategies)


def generate_marketing_strategies(strengths, opportunities):
    """Generate marketing strategies from strengths and market opportunities."""
    strategies = set()

    # From strengths
    for s in strengths:
        text = s.get('Strength', '').lower()
        for key, strategy in MARKETING_STRATEGIES.items():
            if key in text:
                strategies.add(strategy)

    # From market opportunities
    for _, row in opportunities.iterrows() if hasattr(opportunities, 'iterrows') else []:
        opp = str(row.get('Opportunity', '')).lower()
        for key, strategy in MARKETING_STRATEGIES.items():
            if key in opp:
                strategies.add(strategy)

    if not strategies:
        strategies.add(MARKETING_STRATEGIES['default'])

    return sorted(strategies)


def generate_all_strategies(target, weaknesses, strengths, advantages, neg_kw_df, opportunities_df):
    """
    Master function — returns full strategy dict for the target company.
    """
    return {
        'target': target,
        'product':   generate_product_strategies(weaknesses, neg_kw_df),
        'pricing':   generate_pricing_strategies(weaknesses, advantages),
        'marketing': generate_marketing_strategies(strengths, opportunities_df),
    }


if __name__ == '__main__':
    import pandas as pd
    sample_weaknesses = [{'Weakness': 'battery complaints', 'Severity': 'High', 'Source': 'Keywords', 'Detail': ''}]
    sample_strengths  = [{'Strength': 'gaming performance',  'Impact': 'High',  'Source': 'Keywords', 'Detail': ''}]
    sample_advantages = [{'Advantage': 'Lower Price', 'Competitor': 'Acer', 'Detail': '', 'Severity': 'High'}]
    neg_kw = pd.DataFrame({'Keyword': ['battery', 'fan', 'heating'], 'Count': [10, 8, 6]})
    opps   = pd.DataFrame({'Opportunity': ['Gaming Laptops', 'Lightweight Design'], 'Mentions': [34, 22]})

    result = generate_all_strategies('ASUS', sample_weaknesses, sample_strengths, sample_advantages, neg_kw, opps)
    for category, items in result.items():
        if isinstance(items, list):
            print(f"\n{category.upper()} STRATEGIES:")
            for item in items:
                print(f"  - {item}")
