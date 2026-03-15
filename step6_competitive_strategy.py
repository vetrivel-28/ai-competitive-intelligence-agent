"""
Step 6: Competitive Strategy Engine
Generates brand-specific strategies by comparing against competitors
"""

import pandas as pd
import numpy as np

def load_all_analysis():
    """Load all previous analysis results"""
    
    print("=" * 70)
    print("STEP 6: COMPETITIVE STRATEGY ENGINE")
    print("=" * 70)
    
    print("\n📂 Loading analysis results...")
    
    data = {}
    
    # Load competitor analysis
    try:
        competitor_df = pd.read_csv('competitor_analysis.csv')
        data['competitor'] = competitor_df
        print("   ✅ Competitor analysis loaded")
    except:
        print("   ❌ Competitor analysis not found")
        return None
    
    # Load sentiment analysis
    try:
        sentiment_df = pd.read_csv('brand_sentiment_analysis.csv')
        data['sentiment'] = sentiment_df
        print("   ✅ Sentiment analysis loaded")
    except:
        print("   ⚠️ Sentiment analysis not found")
        data['sentiment'] = pd.DataFrame()
    
    # Load keywords
    try:
        positive_kw = pd.read_csv('positive_keywords.csv')
        negative_kw = pd.read_csv('negative_keywords.csv')
        data['positive_keywords'] = positive_kw
        data['negative_keywords'] = negative_kw
        print("   ✅ Keyword analysis loaded")
    except:
        print("   ⚠️ Keyword analysis not found")
        data['positive_keywords'] = pd.DataFrame()
        data['negative_keywords'] = pd.DataFrame()
    
    return data

def identify_competitor_advantages(brand, competitor_df):
    """Identify what competitors do better than this brand"""
    
    advantages = []
    
    brand_data = competitor_df[competitor_df['Brand'] == brand]
    if brand_data.empty:
        return advantages
    
    brand_price = brand_data['Avg_Price'].values[0]
    brand_rating = brand_data['Avg_Rating'].values[0]
    brand_value = brand_data['Value_Score'].values[0] if 'Value_Score' in brand_data.columns else 0
    
    # Compare with each competitor
    competitors = competitor_df[competitor_df['Brand'] != brand]
    
    for _, comp in competitors.iterrows():
        comp_brand = comp['Brand']
        
        # Price advantage
        if comp['Avg_Price'] < brand_price * 0.9:  # 10% cheaper
            price_diff = brand_price - comp['Avg_Price']
            advantages.append({
                'competitor': comp_brand,
                'advantage': 'Lower Price',
                'detail': f'₹{price_diff:,.0f} cheaper on average',
                'gap': price_diff
            })
        
        # Rating advantage
        if comp['Avg_Rating'] > brand_rating + 0.1:
            rating_diff = comp['Avg_Rating'] - brand_rating
            advantages.append({
                'competitor': comp_brand,
                'advantage': 'Better Rating',
                'detail': f'{rating_diff:.2f} points higher',
                'gap': rating_diff
            })
        
        # Value advantage
        if 'Value_Score' in comp and comp['Value_Score'] > brand_value * 1.1:
            advantages.append({
                'competitor': comp_brand,
                'advantage': 'Better Value',
                'detail': f'Higher rating-to-price ratio',
                'gap': comp['Value_Score'] - brand_value
            })
    
    return advantages


def generate_strategy_keywords(brand, advantages, negative_kw, positive_kw):
    """Generate strategic keywords based on gaps and opportunities"""
    
    keywords = []
    
    # Based on competitor advantages
    for adv in advantages:
        if 'Price' in adv['advantage']:
            keywords.extend(['Price Optimization', 'Cost Reduction', 'Value Pricing'])
        if 'Rating' in adv['advantage']:
            keywords.extend(['Quality Improvement', 'Customer Satisfaction', 'Product Excellence'])
        if 'Value' in adv['advantage']:
            keywords.extend(['Feature Enhancement', 'Value Engineering', 'Competitive Pricing'])
    
    # Based on negative keywords (issues to fix)
    if not negative_kw.empty:
        top_negative = negative_kw.head(5)['Keyword'].tolist()
        
        if any('battery' in kw.lower() for kw in top_negative):
            keywords.append('Battery Improvement')
        if any('fan' in kw.lower() or 'noise' in kw.lower() for kw in top_negative):
            keywords.append('Cooling System Upgrade')
        if any('heat' in kw.lower() or 'thermal' in kw.lower() for kw in top_negative):
            keywords.append('Thermal Management')
        if any('performance' in kw.lower() or 'slow' in kw.lower() for kw in top_negative):
            keywords.append('Performance Optimization')
    
    # Based on positive keywords (strengths to market)
    if not positive_kw.empty:
        top_positive = positive_kw.head(5)['Keyword'].tolist()
        
        if any('performance' in kw.lower() for kw in top_positive):
            keywords.append('Performance Marketing')
        if any('screen' in kw.lower() or 'display' in kw.lower() for kw in top_positive):
            keywords.append('Display Quality Marketing')
        if any('build' in kw.lower() or 'quality' in kw.lower() for kw in top_positive):
            keywords.append('Build Quality Emphasis')
    
    # Remove duplicates and limit
    keywords = list(dict.fromkeys(keywords))[:6]
    
    return keywords

def generate_brand_strategy(brand, data):
    """Generate comprehensive strategy for a specific brand"""
    
    competitor_df = data['competitor']
    sentiment_df = data['sentiment']
    positive_kw = data['positive_keywords']
    negative_kw = data['negative_keywords']
    
    strategy = {
        'brand': brand,
        'advantages': [],
        'strategy_keywords': [],
        'action_items': []
    }
    
    # Get brand data
    brand_data = competitor_df[competitor_df['Brand'] == brand]
    if brand_data.empty:
        return None
    
    brand_price = brand_data['Avg_Price'].values[0]
    brand_rating = brand_data['Avg_Rating'].values[0]
    
    # Identify competitor advantages
    advantages = identify_competitor_advantages(brand, competitor_df)
    strategy['advantages'] = advantages
    
    # Generate strategy keywords
    keywords = generate_strategy_keywords(brand, advantages, negative_kw, positive_kw)
    strategy['strategy_keywords'] = keywords

    
    # Generate action items
    action_items = []
    
    # Price-based actions
    if any('Price' in adv['advantage'] for adv in advantages):
        action_items.append({
            'priority': 'High',
            'action': 'Review pricing strategy',
            'detail': 'Competitors offer lower prices - optimize cost structure or add value'
        })
    
    # Rating-based actions
    if any('Rating' in adv['advantage'] for adv in advantages):
        action_items.append({
            'priority': 'High',
            'action': 'Improve product quality',
            'detail': 'Competitors have better ratings - focus on quality and customer satisfaction'
        })
    
    # Keyword-based actions
    if not negative_kw.empty:
        action_items.append({
            'priority': 'Medium',
            'action': 'Address customer pain points',
            'detail': f'Focus on: {", ".join(negative_kw.head(3)["Keyword"].tolist())}'
        })
    
    # Market positioning
    if brand_price > competitor_df['Avg_Price'].median():
        action_items.append({
            'priority': 'Medium',
            'action': 'Justify premium positioning',
            'detail': 'Emphasize unique features and superior quality'
        })
    else:
        action_items.append({
            'priority': 'Medium',
            'action': 'Leverage value positioning',
            'detail': 'Market as best value for money option'
        })
    
    strategy['action_items'] = action_items
    
    return strategy


def display_brand_strategy(strategy):
    """Display strategy for a brand"""
    
    print(f"\n{'=' * 70}")
    print(f"{strategy['brand'].upper()} STRATEGY")
    print("=" * 70)
    
    # Competitor Advantages
    if strategy['advantages']:
        print(f"\n🔍 COMPETITOR ADVANTAGES:")
        print("-" * 70)
        for adv in strategy['advantages']:
            print(f"   • {adv['advantage']} ({adv['competitor']})")
            print(f"     {adv['detail']}")
    else:
        print(f"\n✅ MARKET LEADER: No significant competitor advantages identified")
    
    # Strategy Keywords
    if strategy['strategy_keywords']:
        print(f"\n🎯 SUGGESTED STRATEGY KEYWORDS:")
        print("-" * 70)
        for idx, keyword in enumerate(strategy['strategy_keywords'], 1):
            print(f"   {idx}. {keyword}")
    
    # Action Items
    if strategy['action_items']:
        print(f"\n📋 ACTION ITEMS:")
        print("-" * 70)
        for item in strategy['action_items']:
            print(f"   [{item['priority']}] {item['action']}")
            print(f"   → {item['detail']}")
            print()

def main():
    """Main execution function"""
    
    # Load all analysis
    data = load_all_analysis()
    
    if data is None or data['competitor'].empty:
        print("\n❌ Cannot generate strategies - competitor analysis required")
        return None
    
    # Generate strategies for each brand
    print("\n" + "-" * 70)
    print("Generating competitive strategies...")
    print("-" * 70)
    
    brands = data['competitor']['Brand'].tolist()
    all_strategies = []
    
    for brand in brands:
        strategy = generate_brand_strategy(brand, data)
        if strategy:
            all_strategies.append(strategy)
            print(f"   ✅ Strategy generated for {brand}")
    
    # Display all strategies
    for strategy in all_strategies:
        display_brand_strategy(strategy)
    
    # Save results
    print("\n" + "=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    
    # Save strategies to CSV
    strategies_data = []
    for strategy in all_strategies:
        strategies_data.append({
            'Brand': strategy['brand'],
            'Competitor_Advantages': len(strategy['advantages']),
            'Strategy_Keywords': ', '.join(strategy['strategy_keywords']),
            'Action_Items': len(strategy['action_items'])
        })
    
    strategies_df = pd.DataFrame(strategies_data)
    strategies_df.to_csv('competitive_strategies.csv', index=False)
    print("✅ Saved: competitive_strategies.csv")

    
    # Create detailed report
    with open('competitive_strategies_report.txt', 'w', encoding='utf-8') as f:
        f.write("COMPETITIVE STRATEGY ENGINE - DETAILED REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        for strategy in all_strategies:
            f.write(f"{strategy['brand'].upper()} STRATEGY\n")
            f.write("-" * 70 + "\n\n")
            
            f.write("COMPETITOR ADVANTAGES:\n")
            if strategy['advantages']:
                for adv in strategy['advantages']:
                    f.write(f"  • {adv['advantage']} ({adv['competitor']}): {adv['detail']}\n")
            else:
                f.write("  • No significant competitor advantages\n")
            f.write("\n")
            
            f.write("STRATEGY KEYWORDS:\n")
            for keyword in strategy['strategy_keywords']:
                f.write(f"  • {keyword}\n")
            f.write("\n")
            
            f.write("ACTION ITEMS:\n")
            for item in strategy['action_items']:
                f.write(f"  [{item['priority']}] {item['action']}\n")
                f.write(f"  → {item['detail']}\n\n")
            
            f.write("\n" + "=" * 70 + "\n\n")
    
    print("✅ Saved: competitive_strategies_report.txt")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n📊 Strategies Generated: {len(all_strategies)} brands")
    print(f"📁 Output Files: 2 (CSV + Report)")
    
    # Overall insights
    total_advantages = sum(len(s['advantages']) for s in all_strategies)
    total_keywords = sum(len(s['strategy_keywords']) for s in all_strategies)
    total_actions = sum(len(s['action_items']) for s in all_strategies)
    
    print(f"\n📈 Total Analysis:")
    print(f"   Competitor Advantages Identified: {total_advantages}")
    print(f"   Strategy Keywords Generated: {total_keywords}")
    print(f"   Action Items Created: {total_actions}")
    
    print("\n" + "=" * 70)
    print("✅ STEP 6 COMPLETE: Competitive Strategies Generated!")
    print("=" * 70)
    
    return all_strategies

if __name__ == "__main__":
    strategies = main()
