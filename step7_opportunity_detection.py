"""
Step 7: Market Opportunity Detection
Finds emerging opportunities from Reddit and YouTube discussions
"""

import pandas as pd
import numpy as np
from collections import Counter
import re

def load_discussion_data():
    """Load Reddit and YouTube discussion data"""
    
    print("=" * 70)
    print("STEP 7: MARKET OPPORTUNITY DETECTION")
    print("=" * 70)
    
    print("\n📂 Loading discussion data...")
    
    data = {}
    
    # Load Reddit data
    try:
        reddit_df = pd.read_csv('reddit.csv')
        data['reddit'] = reddit_df
        print(f"   ✅ Reddit data loaded: {len(reddit_df)} posts")
    except:
        print("   ❌ Reddit data not found")
        data['reddit'] = pd.DataFrame()
    
    # Load YouTube data
    try:
        youtube_df = pd.read_csv('youtube.csv')
        data['youtube'] = youtube_df
        print(f"   ✅ YouTube data loaded: {len(youtube_df)} comments")
    except:
        print("   ❌ YouTube data not found")
        data['youtube'] = pd.DataFrame()
    
    return data

def extract_opportunity_keywords(text):
    """Extract opportunity-related keywords from text"""
    
    if pd.isna(text) or text == '':
        return []
    
    text_lower = str(text).lower()
    keywords = []
    
    # Opportunity categories with patterns
    opportunities = {
        'Gaming Laptops': [
            'gaming', 'game', 'fps', 'rtx', 'graphics', 'gpu', 'nvidia', 
            'amd radeon', 'gaming laptop', 'esports', 'valorant', 'fortnite'
        ],
        'Long Battery Life': [
            'battery life', 'battery', 'long battery', 'all day battery',
            'battery backup', 'hours battery', '10 hour', 'battery drain'
        ],
        'Lightweight Design': [
            'lightweight', 'light weight', 'portable', 'thin', 'slim',
            'carry', 'travel', 'compact', 'portability'
        ],
        'Creator Laptops': [
            'video editing', 'photo editing', 'content creation', 'creator',
            'adobe', 'premiere', 'photoshop', 'rendering', '4k editing'
        ],
        'Student Laptops': [
            'student', 'college', 'university', 'study', 'notes',
            'online classes', 'zoom', 'learning', 'education'
        ],
        'Business Laptops': [
            'business', 'work', 'office', 'professional', 'productivity',
            'excel', 'powerpoint', 'meetings', 'corporate'
        ],
        'Budget Laptops': [
            'budget', 'cheap', 'affordable', 'under 50000', 'under 40000',
            'best value', 'low price', 'economical'
        ],
        'Premium Laptops': [
            'premium', 'high end', 'flagship', 'luxury', 'expensive',
            'top tier', 'best laptop', 'ultimate'
        ],
        '2-in-1 Convertible': [
            '2 in 1', 'convertible', 'touchscreen', 'tablet mode',
            'flip', 'yoga', 'touch screen'
        ],
        'AI/ML Laptops': [
            'machine learning', 'ai', 'deep learning', 'data science',
            'python', 'tensorflow', 'cuda', 'programming'
        ]
    }
    
    # Check for each opportunity
    for opportunity, patterns in opportunities.items():
        for pattern in patterns:
            if pattern in text_lower:
                keywords.append(opportunity)
                break  # Only add once per opportunity
    
    return keywords


def analyze_reddit_opportunities(reddit_df):
    """Analyze Reddit discussions for opportunities"""
    
    print("\n" + "-" * 70)
    print("Analyzing Reddit discussions...")
    print("-" * 70)
    
    opportunities = []
    
    if reddit_df.empty:
        print("   ⚠️ No Reddit data to analyze")
        return opportunities
    
    for idx, row in reddit_df.iterrows():
        text = str(row.get('post_title', '')) + ' ' + str(row.get('post_text', ''))
        keywords = extract_opportunity_keywords(text)
        opportunities.extend(keywords)
    
    print(f"   ✅ Analyzed {len(reddit_df)} Reddit posts")
    print(f"   📊 Found {len(opportunities)} opportunity mentions")
    
    return opportunities

def analyze_youtube_opportunities(youtube_df):
    """Analyze YouTube comments for opportunities"""
    
    print("\n" + "-" * 70)
    print("Analyzing YouTube comments...")
    print("-" * 70)
    
    opportunities = []
    
    if youtube_df.empty:
        print("   ⚠️ No YouTube data to analyze")
        return opportunities
    
    for idx, row in youtube_df.iterrows():
        text = str(row.get('video_title', '')) + ' ' + str(row.get('comment', ''))
        keywords = extract_opportunity_keywords(text)
        opportunities.extend(keywords)
    
    print(f"   ✅ Analyzed {len(youtube_df)} YouTube comments")
    print(f"   📊 Found {len(opportunities)} opportunity mentions")
    
    return opportunities

def rank_opportunities(all_opportunities):
    """Rank opportunities by frequency"""
    
    if not all_opportunities:
        return pd.DataFrame()
    
    # Count occurrences
    opportunity_counts = Counter(all_opportunities)
    
    # Create DataFrame
    opportunities_df = pd.DataFrame(
        opportunity_counts.most_common(),
        columns=['Opportunity', 'Mentions']
    )
    
    # Calculate percentage
    total = opportunities_df['Mentions'].sum()
    opportunities_df['Percentage'] = (opportunities_df['Mentions'] / total * 100).round(1)
    
    return opportunities_df


def generate_opportunity_insights(opportunities_df):
    """Generate insights from opportunity data"""
    
    insights = []
    
    if opportunities_df.empty:
        return insights
    
    top_opportunities = opportunities_df.head(5)
    
    for idx, row in top_opportunities.iterrows():
        opportunity = row['Opportunity']
        mentions = row['Mentions']
        percentage = row['Percentage']
        
        # Generate insight based on opportunity type
        if 'Gaming' in opportunity:
            insights.append({
                'opportunity': opportunity,
                'demand_level': 'High' if mentions > 10 else 'Medium',
                'target_audience': 'Gamers, esports enthusiasts',
                'key_features': 'High-end GPU, fast refresh rate display, RGB lighting',
                'price_range': '₹60,000 - ₹1,50,000',
                'mentions': mentions
            })
        
        elif 'Battery' in opportunity:
            insights.append({
                'opportunity': opportunity,
                'demand_level': 'High' if mentions > 8 else 'Medium',
                'target_audience': 'Mobile professionals, students',
                'key_features': '10+ hour battery, fast charging, power efficiency',
                'price_range': '₹40,000 - ₹80,000',
                'mentions': mentions
            })
        
        elif 'Lightweight' in opportunity:
            insights.append({
                'opportunity': opportunity,
                'demand_level': 'High' if mentions > 8 else 'Medium',
                'target_audience': 'Travelers, mobile workers',
                'key_features': 'Under 1.5kg, thin profile, durable build',
                'price_range': '₹50,000 - ₹1,00,000',
                'mentions': mentions
            })
        
        elif 'Creator' in opportunity:
            insights.append({
                'opportunity': opportunity,
                'demand_level': 'High' if mentions > 8 else 'Medium',
                'target_audience': 'Content creators, video editors',
                'key_features': 'High-end CPU/GPU, color-accurate display, 16GB+ RAM',
                'price_range': '₹80,000 - ₹2,00,000',
                'mentions': mentions
            })
        
        elif 'Student' in opportunity:
            insights.append({
                'opportunity': opportunity,
                'demand_level': 'High' if mentions > 8 else 'Medium',
                'target_audience': 'Students, educators',
                'key_features': 'Affordable, good battery, webcam, lightweight',
                'price_range': '₹30,000 - ₹60,000',
                'mentions': mentions
            })
        
        elif 'Business' in opportunity:
            insights.append({
                'opportunity': opportunity,
                'demand_level': 'High' if mentions > 8 else 'Medium',
                'target_audience': 'Professionals, corporate users',
                'key_features': 'Security features, durability, professional design',
                'price_range': '₹50,000 - ₹1,20,000',
                'mentions': mentions
            })
        
        else:
            insights.append({
                'opportunity': opportunity,
                'demand_level': 'Medium',
                'target_audience': 'General users',
                'key_features': 'Balanced features',
                'price_range': '₹40,000 - ₹80,000',
                'mentions': mentions
            })
    
    return insights


def display_opportunities(opportunities_df, insights):
    """Display opportunity analysis results"""
    
    print("\n" + "=" * 70)
    print("MARKET OPPORTUNITY KEYWORDS")
    print("=" * 70)
    
    if opportunities_df.empty:
        print("\n⚠️ No opportunities detected")
        return
    
    print("\n📊 TOP OPPORTUNITIES (Ranked by Mentions):")
    print("-" * 70)
    
    for idx, row in opportunities_df.head(10).iterrows():
        print(f"   {idx + 1}. {row['Opportunity']}: {row['Mentions']} mentions ({row['Percentage']}%)")
    
    print("\n" + "=" * 70)
    print("OPPORTUNITY INSIGHTS")
    print("=" * 70)
    
    for insight in insights:
        print(f"\n🎯 {insight['opportunity'].upper()}")
        print("-" * 70)
        print(f"   Demand Level: {insight['demand_level']}")
        print(f"   Target Audience: {insight['target_audience']}")
        print(f"   Key Features: {insight['key_features']}")
        print(f"   Price Range: {insight['price_range']}")
        print(f"   Mentions: {insight['mentions']}")

def main():
    """Main execution function"""
    
    # Load discussion data
    data = load_discussion_data()
    
    if data['reddit'].empty and data['youtube'].empty:
        print("\n❌ No discussion data available for analysis")
        return None
    
    # Analyze opportunities
    reddit_opportunities = analyze_reddit_opportunities(data['reddit'])
    youtube_opportunities = analyze_youtube_opportunities(data['youtube'])
    
    # Combine all opportunities
    all_opportunities = reddit_opportunities + youtube_opportunities
    
    print("\n" + "-" * 70)
    print("Ranking opportunities...")
    print("-" * 70)
    print(f"   📊 Total opportunity mentions: {len(all_opportunities)}")
    print(f"   📊 From Reddit: {len(reddit_opportunities)}")
    print(f"   📊 From YouTube: {len(youtube_opportunities)}")
    
    # Rank opportunities
    opportunities_df = rank_opportunities(all_opportunities)
    
    # Generate insights
    insights = generate_opportunity_insights(opportunities_df)
    
    # Display results
    display_opportunities(opportunities_df, insights)
    
    # Save results
    print("\n" + "=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    
    if not opportunities_df.empty:
        opportunities_df.to_csv('market_opportunities_detected.csv', index=False)
        print("✅ Saved: market_opportunities_detected.csv")
    
    if insights:
        insights_df = pd.DataFrame(insights)
        insights_df.to_csv('opportunity_insights.csv', index=False)
        print("✅ Saved: opportunity_insights.csv")

    
    # Create detailed report
    with open('opportunity_detection_report.txt', 'w', encoding='utf-8') as f:
        f.write("MARKET OPPORTUNITY DETECTION REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("TOP MARKET OPPORTUNITIES\n")
        f.write("-" * 70 + "\n\n")
        
        for idx, row in opportunities_df.head(10).iterrows():
            f.write(f"{idx + 1}. {row['Opportunity']}\n")
            f.write(f"   Mentions: {row['Mentions']} ({row['Percentage']}%)\n\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("OPPORTUNITY INSIGHTS\n")
        f.write("-" * 70 + "\n\n")
        
        for insight in insights:
            f.write(f"{insight['opportunity'].upper()}\n")
            f.write(f"  Demand Level: {insight['demand_level']}\n")
            f.write(f"  Target Audience: {insight['target_audience']}\n")
            f.write(f"  Key Features: {insight['key_features']}\n")
            f.write(f"  Price Range: {insight['price_range']}\n")
            f.write(f"  Mentions: {insight['mentions']}\n\n")
    
    print("✅ Saved: opportunity_detection_report.txt")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n📊 Opportunities Detected: {len(opportunities_df)}")
    print(f"📊 Total Mentions: {len(all_opportunities)}")
    print(f"📊 Insights Generated: {len(insights)}")
    print(f"📁 Output Files: 3 (2 CSV + 1 Report)")
    
    if not opportunities_df.empty:
        top_3 = opportunities_df.head(3)['Opportunity'].tolist()
        print(f"\n🎯 Top 3 Opportunities:")
        for idx, opp in enumerate(top_3, 1):
            print(f"   {idx}. {opp}")
    
    print("\n" + "=" * 70)
    print("✅ STEP 7 COMPLETE: Market Opportunities Detected!")
    print("=" * 70)
    
    return opportunities_df, insights

if __name__ == "__main__":
    opportunities, insights = main()
