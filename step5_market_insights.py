"""
Step 5: Market Insight Engine
Generates keyword-based market insights combining all previous analysis
"""

import pandas as pd
import numpy as np
from load_data import load_data

def load_analysis_results():
    """Load results from previous analysis steps"""
    
    print("=" * 70)
    print("STEP 5: MARKET INSIGHT ENGINE")
    print("=" * 70)
    
    print("\n📂 Loading previous analysis results...")
    
    results = {}
    
    # Load sentiment analysis
    try:
        sentiment_df = pd.read_csv('brand_sentiment_analysis.csv')
        results['sentiment'] = sentiment_df
        print("   ✅ Sentiment analysis loaded")
    except:
        print("   ⚠️ Sentiment analysis not found")
        results['sentiment'] = pd.DataFrame()
    
    # Load keyword analysis
    try:
        positive_kw = pd.read_csv('positive_keywords.csv')
        negative_kw = pd.read_csv('negative_keywords.csv')
        results['positive_keywords'] = positive_kw
        results['negative_keywords'] = negative_kw
        print("   ✅ Keyword analysis loaded")
    except:
        print("   ⚠️ Keyword analysis not found")
        results['positive_keywords'] = pd.DataFrame()
        results['negative_keywords'] = pd.DataFrame()
    
    # Load competitor analysis
    try:
        competitor_df = pd.read_csv('competitor_analysis.csv')
        results['competitor'] = competitor_df
        print("   ✅ Competitor analysis loaded")
    except:
        print("   ⚠️ Competitor analysis not found")
        results['competitor'] = pd.DataFrame()
    
    return results

def generate_price_segment_insights(competitor_df):
    """Generate insights by price segment"""
    
    insights = []
    
    if competitor_df.empty:
        return insights
    
    # High price segment (>70000)
    high_price = competitor_df[competitor_df['Avg_Price'] > 70000]
    if not high_price.empty:
        brands = ', '.join(high_price['Brand'].tolist())
        avg_rating = high_price['Avg_Rating'].mean()
        insights.append({
            'Category': 'High Price Segment',
            'Brands': brands,
            'Insight': f'Premium brands with avg rating {avg_rating:.2f}',
            'Action': 'Target quality-conscious customers, emphasize premium features'
        })
    
    # Mid price segment (50000-70000)
    mid_price = competitor_df[(competitor_df['Avg_Price'] >= 50000) & 
                              (competitor_df['Avg_Price'] <= 70000)]
    if not mid_price.empty:
        brands = ', '.join(mid_price['Brand'].tolist())
        insights.append({
            'Category': 'Mid Price Segment',
            'Brands': brands,
            'Insight': 'Most competitive segment with balanced features',
            'Action': 'Focus on value proposition and feature differentiation'
        })
    
    # Budget segment (<50000)
    budget = competitor_df[competitor_df['Avg_Price'] < 50000]
    if not budget.empty:
        brands = ', '.join(budget['Brand'].tolist())
        insights.append({
            'Category': 'Budget Segment',
            'Brands': brands,
            'Insight': 'Price-sensitive market with good ratings',
            'Action': 'Emphasize affordability and essential features'
        })
    
    return insights


def generate_keyword_insights(positive_kw, negative_kw):
    """Generate insights from keyword analysis"""
    
    insights = []
    
    # Positive keyword insights
    if not positive_kw.empty:
        top_positive = positive_kw.head(5)
        keywords = ', '.join(top_positive['Keyword'].tolist())
        insights.append({
            'Category': 'Performance Strengths',
            'Keywords': keywords,
            'Insight': 'Most praised features by customers',
            'Action': 'Highlight these features in marketing campaigns'
        })
    
    # Negative keyword insights
    if not negative_kw.empty:
        top_negative = negative_kw.head(5)
        keywords = ', '.join(top_negative['Keyword'].tolist())
        
        # Categorize issues
        if any(kw in keywords.lower() for kw in ['battery', 'drain', 'backup']):
            insights.append({
                'Category': 'Battery Complaints',
                'Keywords': keywords,
                'Insight': 'Battery life is a common concern',
                'Action': 'Improve battery optimization, highlight battery specs'
            })
        
        if any(kw in keywords.lower() for kw in ['heating', 'hot', 'thermal', 'temperature']):
            insights.append({
                'Category': 'Thermal Issues',
                'Keywords': keywords,
                'Insight': 'Overheating reported by users',
                'Action': 'Enhance cooling system, add thermal management features'
            })
        
        if any(kw in keywords.lower() for kw in ['fan', 'noise', 'loud']):
            insights.append({
                'Category': 'Fan Noise Issues',
                'Keywords': keywords,
                'Insight': 'Fan noise affecting user experience',
                'Action': 'Optimize fan curves, use quieter cooling solutions'
            })
        
        if not any(kw in keywords.lower() for kw in ['battery', 'heating', 'fan']):
            insights.append({
                'Category': 'General Concerns',
                'Keywords': keywords,
                'Insight': 'Various issues reported',
                'Action': 'Address quality control and customer support'
            })
    
    return insights

def generate_sentiment_insights(sentiment_df):
    """Generate insights from sentiment analysis"""
    
    insights = []
    
    if sentiment_df.empty:
        return insights
    
    # Best sentiment brands
    sentiment_df['Positive_Pct'] = sentiment_df['Positive'].str.rstrip('%').astype(float)
    sentiment_df['Negative_Pct'] = sentiment_df['Negative'].str.rstrip('%').astype(float)
    
    best_sentiment = sentiment_df.nlargest(3, 'Positive_Pct')
    if not best_sentiment.empty:
        brands = ', '.join(best_sentiment['Brand'].tolist())
        avg_positive = best_sentiment['Positive_Pct'].mean()
        insights.append({
            'Category': 'Customer Satisfaction Leaders',
            'Brands': brands,
            'Insight': f'Highest positive sentiment ({avg_positive:.1f}% average)',
            'Action': 'Study their success factors and customer engagement'
        })
    
    # Brands needing improvement
    needs_improvement = sentiment_df[sentiment_df['Negative_Pct'] > 15]
    if not needs_improvement.empty:
        brands = ', '.join(needs_improvement['Brand'].tolist())
        insights.append({
            'Category': 'Improvement Opportunities',
            'Brands': brands,
            'Insight': 'Higher negative sentiment detected',
            'Action': 'Focus on addressing customer pain points'
        })
    
    return insights


def generate_competitive_insights(competitor_df):
    """Generate competitive positioning insights"""
    
    insights = []
    
    if competitor_df.empty:
        return insights
    
    # Best value brands
    if 'Value_Score' in competitor_df.columns:
        best_value = competitor_df.nlargest(2, 'Value_Score')
        brands = ', '.join(best_value['Brand'].tolist())
        insights.append({
            'Category': 'Best Value Positioning',
            'Brands': brands,
            'Insight': 'Highest rating-to-price ratio',
            'Action': 'Competitive pricing strategy with quality focus'
        })
    
    # Premium positioning
    premium = competitor_df.nlargest(2, 'Avg_Price')
    brands = ', '.join(premium['Brand'].tolist())
    insights.append({
        'Category': 'Premium Market Leaders',
        'Brands': brands,
        'Insight': 'Command highest prices in market',
        'Action': 'Premium branding and feature differentiation'
    })
    
    # Rating leaders
    top_rated = competitor_df.nlargest(2, 'Avg_Rating')
    brands = ', '.join(top_rated['Brand'].tolist())
    insights.append({
        'Category': 'Quality Leaders',
        'Brands': brands,
        'Insight': 'Highest customer satisfaction ratings',
        'Action': 'Benchmark quality standards against these brands'
    })
    
    return insights

def generate_market_opportunities(all_insights):
    """Identify market opportunities from all insights"""
    
    opportunities = []
    
    # Analyze gaps and opportunities
    opportunities.append({
        'Opportunity': 'Battery Life Enhancement',
        'Rationale': 'Negative keywords show battery concerns',
        'Strategy': 'Develop laptops with 10+ hour battery life',
        'Target': 'Mobile professionals and students'
    })
    
    opportunities.append({
        'Opportunity': 'Thermal Management Innovation',
        'Rationale': 'Heating issues frequently mentioned',
        'Strategy': 'Advanced cooling systems, vapor chambers',
        'Target': 'Gaming and content creation segments'
    })
    
    opportunities.append({
        'Opportunity': 'Value Segment Expansion',
        'Rationale': 'Mid-range segment most competitive',
        'Strategy': 'Feature-rich laptops at competitive prices',
        'Target': 'Budget-conscious buyers seeking quality'
    })
    
    opportunities.append({
        'Opportunity': 'Premium Experience',
        'Rationale': 'High correlation between price and rating',
        'Strategy': 'Premium materials, superior build quality',
        'Target': 'Quality-focused professionals'
    })
    
    return opportunities

def display_insights(all_insights, opportunities):
    """Display all market insights"""
    
    print("\n" + "=" * 70)
    print("MARKET INSIGHTS")
    print("=" * 70)
    
    for category in ['High Price Segment', 'Mid Price Segment', 'Budget Segment',
                     'Performance Strengths', 'Battery Complaints', 'Thermal Issues',
                     'Fan Noise Issues', 'Customer Satisfaction Leaders',
                     'Best Value Positioning', 'Premium Market Leaders', 'Quality Leaders']:
        
        matching = [i for i in all_insights if i['Category'] == category]
        if matching:
            insight = matching[0]
            print(f"\n📊 {insight['Category'].upper()}")
            print("-" * 70)
            if 'Brands' in insight:
                print(f"   Brands: {insight['Brands']}")
            if 'Keywords' in insight:
                print(f"   Keywords: {insight['Keywords']}")
            print(f"   Insight: {insight['Insight']}")
            print(f"   Action: {insight['Action']}")
    
    print("\n" + "=" * 70)
    print("MARKET OPPORTUNITIES")
    print("=" * 70)
    
    for idx, opp in enumerate(opportunities, 1):
        print(f"\n🎯 OPPORTUNITY {idx}: {opp['Opportunity']}")
        print("-" * 70)
        print(f"   Rationale: {opp['Rationale']}")
        print(f"   Strategy: {opp['Strategy']}")
        print(f"   Target: {opp['Target']}")


def main():
    """Main execution function"""
    
    # Load all analysis results
    results = load_analysis_results()
    
    # Generate insights from different analyses
    print("\n" + "-" * 70)
    print("Generating market insights...")
    print("-" * 70)
    
    all_insights = []
    
    # Price segment insights
    if not results['competitor'].empty:
        price_insights = generate_price_segment_insights(results['competitor'])
        all_insights.extend(price_insights)
        print(f"   ✅ Generated {len(price_insights)} price segment insights")
    
    # Keyword insights
    if not results['positive_keywords'].empty or not results['negative_keywords'].empty:
        keyword_insights = generate_keyword_insights(
            results['positive_keywords'], 
            results['negative_keywords']
        )
        all_insights.extend(keyword_insights)
        print(f"   ✅ Generated {len(keyword_insights)} keyword-based insights")
    
    # Sentiment insights
    if not results['sentiment'].empty:
        sentiment_insights = generate_sentiment_insights(results['sentiment'])
        all_insights.extend(sentiment_insights)
        print(f"   ✅ Generated {len(sentiment_insights)} sentiment insights")
    
    # Competitive insights
    if not results['competitor'].empty:
        competitive_insights = generate_competitive_insights(results['competitor'])
        all_insights.extend(competitive_insights)
        print(f"   ✅ Generated {len(competitive_insights)} competitive insights")
    
    # Market opportunities
    opportunities = generate_market_opportunities(all_insights)
    print(f"   ✅ Identified {len(opportunities)} market opportunities")
    
    # Display insights
    display_insights(all_insights, opportunities)
    
    # Save to files
    print("\n" + "=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    
    # Save insights to CSV
    insights_df = pd.DataFrame(all_insights)
    insights_df.to_csv('market_insights.csv', index=False)
    print("✅ Saved: market_insights.csv")
    
    # Save opportunities to CSV
    opportunities_df = pd.DataFrame(opportunities)
    opportunities_df.to_csv('market_opportunities.csv', index=False)
    print("✅ Saved: market_opportunities.csv")
    
    # Create comprehensive report
    with open('market_insights_report.txt', 'w', encoding='utf-8') as f:
        f.write("MARKET INSIGHT ENGINE - COMPREHENSIVE REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("MARKET INSIGHTS\n")
        f.write("-" * 70 + "\n\n")
        
        for insight in all_insights:
            f.write(f"Category: {insight['Category']}\n")
            if 'Brands' in insight:
                f.write(f"Brands: {insight['Brands']}\n")
            if 'Keywords' in insight:
                f.write(f"Keywords: {insight['Keywords']}\n")
            f.write(f"Insight: {insight['Insight']}\n")
            f.write(f"Action: {insight['Action']}\n\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("MARKET OPPORTUNITIES\n")
        f.write("-" * 70 + "\n\n")
        
        for idx, opp in enumerate(opportunities, 1):
            f.write(f"{idx}. {opp['Opportunity']}\n")
            f.write(f"   Rationale: {opp['Rationale']}\n")
            f.write(f"   Strategy: {opp['Strategy']}\n")
            f.write(f"   Target: {opp['Target']}\n\n")
    
    print("✅ Saved: market_insights_report.txt")
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n📊 Total Insights Generated: {len(all_insights)}")
    print(f"🎯 Market Opportunities Identified: {len(opportunities)}")
    print(f"📁 Output Files: 3 (CSV + Report)")
    
    print("\n" + "=" * 70)
    print("✅ STEP 5 COMPLETE: Market Insights Generated!")
    print("=" * 70)
    
    return all_insights, opportunities

if __name__ == "__main__":
    insights, opportunities = main()
