"""
Step 2: Sentiment Analysis
Performs sentiment analysis on all data sources and outputs brand-wise sentiment percentages
"""

import pandas as pd
import numpy as np
from textblob import TextBlob
from load_data import load_data

def analyze_sentiment(text):
    """
    Analyze sentiment of a single text
    Returns: 'Positive', 'Negative', or 'Neutral'
    """
    if pd.isna(text) or text == '' or text == 'N/A':
        return 'Neutral'
    
    try:
        blob = TextBlob(str(text))
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'Positive'
        elif polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    except:
        return 'Neutral'

def perform_sentiment_analysis(data):
    """
    Perform sentiment analysis on all data sources
    Returns: dict with analyzed dataframes
    """
    
    print("=" * 70)
    print("STEP 2: SENTIMENT ANALYSIS")
    print("=" * 70)
    
    results = {}
    
    # Analyze Amazon reviews
    print("\n" + "-" * 70)
    print("Analyzing Amazon Reviews...")
    print("-" * 70)
    
    if not data['amazon'].empty:
        amazon_df = data['amazon'].copy()
        
        # Combine review and comment text
        amazon_df['combined_text'] = (
            amazon_df.get('review_text', '').fillna('') + ' ' + 
            amazon_df.get('comment_text', '').fillna('')
        ).str.strip()
        
        print(f"📊 Analyzing {len(amazon_df)} Amazon products...")
        amazon_df['sentiment'] = amazon_df['combined_text'].apply(analyze_sentiment)
        
        sentiment_counts = amazon_df['sentiment'].value_counts()
        print(f"   ✅ Positive: {sentiment_counts.get('Positive', 0)}")
        print(f"   ❌ Negative: {sentiment_counts.get('Negative', 0)}")
        print(f"   ⚪ Neutral: {sentiment_counts.get('Neutral', 0)}")
        
        results['amazon'] = amazon_df
    else:
        print("⚠️ No Amazon data to analyze")
        results['amazon'] = pd.DataFrame()
    
    # Analyze Flipkart reviews
    print("\n" + "-" * 70)
    print("Analyzing Flipkart Reviews...")
    print("-" * 70)
    
    if not data['flipkart'].empty:
        flipkart_df = data['flipkart'].copy()
        
        print(f"📊 Analyzing {len(flipkart_df)} Flipkart products...")
        flipkart_df['sentiment'] = flipkart_df['reviews_comments'].fillna('').apply(analyze_sentiment)
        
        sentiment_counts = flipkart_df['sentiment'].value_counts()
        print(f"   ✅ Positive: {sentiment_counts.get('Positive', 0)}")
        print(f"   ❌ Negative: {sentiment_counts.get('Negative', 0)}")
        print(f"   ⚪ Neutral: {sentiment_counts.get('Neutral', 0)}")
        
        results['flipkart'] = flipkart_df
    else:
        print("⚠️ No Flipkart data to analyze")
        results['flipkart'] = pd.DataFrame()
    
    # Analyze Reddit posts
    print("\n" + "-" * 70)
    print("Analyzing Reddit Posts...")
    print("-" * 70)
    
    if not data['reddit'].empty:
        reddit_df = data['reddit'].copy()
        
        # Combine title and text
        reddit_df['combined_text'] = (
            reddit_df['post_title'].fillna('') + ' ' + 
            reddit_df['post_text'].fillna('')
        ).str.strip()
        
        print(f"📊 Analyzing {len(reddit_df)} Reddit posts...")
        reddit_df['sentiment'] = reddit_df['combined_text'].apply(analyze_sentiment)
        
        sentiment_counts = reddit_df['sentiment'].value_counts()
        print(f"   ✅ Positive: {sentiment_counts.get('Positive', 0)}")
        print(f"   ❌ Negative: {sentiment_counts.get('Negative', 0)}")
        print(f"   ⚪ Neutral: {sentiment_counts.get('Neutral', 0)}")
        
        results['reddit'] = reddit_df
    else:
        print("⚠️ No Reddit data to analyze")
        results['reddit'] = pd.DataFrame()
    
    # Analyze YouTube comments
    print("\n" + "-" * 70)
    print("Analyzing YouTube Comments...")
    print("-" * 70)
    
    if not data['youtube'].empty:
        youtube_df = data['youtube'].copy()
        
        print(f"📊 Analyzing {len(youtube_df)} YouTube comments...")
        youtube_df['sentiment'] = youtube_df['comment'].fillna('').apply(analyze_sentiment)
        
        sentiment_counts = youtube_df['sentiment'].value_counts()
        print(f"   ✅ Positive: {sentiment_counts.get('Positive', 0)}")
        print(f"   ❌ Negative: {sentiment_counts.get('Negative', 0)}")
        print(f"   ⚪ Neutral: {sentiment_counts.get('Neutral', 0)}")
        
        results['youtube'] = youtube_df
    else:
        print("⚠️ No YouTube data to analyze")
        results['youtube'] = pd.DataFrame()
    
    return results

def calculate_brand_sentiment(results):
    """
    Calculate sentiment percentages by brand across all sources
    Returns: DataFrame with brand sentiment percentages
    """
    
    print("\n" + "=" * 70)
    print("CALCULATING BRAND-WISE SENTIMENT")
    print("=" * 70)
    
    all_data = []
    
    # Collect all data with brand and sentiment
    for source_name, df in results.items():
        if not df.empty and 'brand' in df.columns and 'sentiment' in df.columns:
            temp_df = df[['brand', 'sentiment']].copy()
            temp_df['source'] = source_name
            all_data.append(temp_df)
        elif not df.empty and 'laptop_name' in df.columns and 'sentiment' in df.columns:
            # For Reddit/YouTube, extract brand from laptop_name
            temp_df = df[['laptop_name', 'sentiment']].copy()
            temp_df['brand'] = temp_df['laptop_name']
            temp_df['source'] = source_name
            temp_df = temp_df[['brand', 'sentiment', 'source']]
            all_data.append(temp_df)
    
    if not all_data:
        print("❌ No data available for brand sentiment analysis")
        return pd.DataFrame()
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Clean brand names
    combined_df['brand'] = combined_df['brand'].str.strip()
    combined_df = combined_df[combined_df['brand'] != 'Unknown']
    combined_df = combined_df[combined_df['brand'] != 'Generic Laptop']
    combined_df = combined_df[combined_df['brand'].notna()]
    
    print(f"\n📊 Total entries for analysis: {len(combined_df)}")
    print(f"   Unique brands: {combined_df['brand'].nunique()}")
    
    # Calculate sentiment percentages by brand
    brand_sentiment = []
    
    for brand in combined_df['brand'].unique():
        brand_data = combined_df[combined_df['brand'] == brand]
        total = len(brand_data)
        
        positive = len(brand_data[brand_data['sentiment'] == 'Positive'])
        negative = len(brand_data[brand_data['sentiment'] == 'Negative'])
        neutral = len(brand_data[brand_data['sentiment'] == 'Neutral'])
        
        brand_sentiment.append({
            'Brand': brand,
            'Total': total,
            'Positive': f"{(positive/total*100):.1f}%",
            'Negative': f"{(negative/total*100):.1f}%",
            'Neutral': f"{(neutral/total*100):.1f}%",
            'Positive_Count': positive,
            'Negative_Count': negative,
            'Neutral_Count': neutral
        })
    
    sentiment_df = pd.DataFrame(brand_sentiment)
    sentiment_df = sentiment_df.sort_values('Total', ascending=False)
    
    return sentiment_df

def main():
    """Main execution function"""
    
    # Load data
    print("Loading data from Step 1...")
    data = load_data()
    
    # Perform sentiment analysis
    results = perform_sentiment_analysis(data)
    
    # Calculate brand sentiment
    brand_sentiment_df = calculate_brand_sentiment(results)
    
    # Display results
    print("\n" + "=" * 70)
    print("BRAND SENTIMENT ANALYSIS RESULTS")
    print("=" * 70)
    
    if not brand_sentiment_df.empty:
        print("\n")
        print(brand_sentiment_df[['Brand', 'Total', 'Positive', 'Negative', 'Neutral']].to_string(index=False))
        
        # Save to CSV
        brand_sentiment_df.to_csv('brand_sentiment_analysis.csv', index=False)
        print(f"\n💾 Results saved to: brand_sentiment_analysis.csv")
    else:
        print("\n⚠️ No brand sentiment data available")
    
    # Overall sentiment summary
    print("\n" + "=" * 70)
    print("OVERALL SENTIMENT SUMMARY")
    print("=" * 70)
    
    total_positive = brand_sentiment_df['Positive_Count'].sum() if not brand_sentiment_df.empty else 0
    total_negative = brand_sentiment_df['Negative_Count'].sum() if not brand_sentiment_df.empty else 0
    total_neutral = brand_sentiment_df['Neutral_Count'].sum() if not brand_sentiment_df.empty else 0
    total_all = total_positive + total_negative + total_neutral
    
    if total_all > 0:
        print(f"\n📊 Across all brands and sources:")
        print(f"   ✅ Positive: {total_positive} ({total_positive/total_all*100:.1f}%)")
        print(f"   ❌ Negative: {total_negative} ({total_negative/total_all*100:.1f}%)")
        print(f"   ⚪ Neutral: {total_neutral} ({total_neutral/total_all*100:.1f}%)")
        print(f"   📈 Total analyzed: {total_all}")
    
    # Source-wise breakdown
    print("\n" + "-" * 70)
    print("Source-wise Sentiment Breakdown:")
    print("-" * 70)
    
    for source_name, df in results.items():
        if not df.empty and 'sentiment' in df.columns:
            sentiment_counts = df['sentiment'].value_counts()
            total = len(df)
            print(f"\n{source_name.upper()}:")
            print(f"   ✅ Positive: {sentiment_counts.get('Positive', 0)} ({sentiment_counts.get('Positive', 0)/total*100:.1f}%)")
            print(f"   ❌ Negative: {sentiment_counts.get('Negative', 0)} ({sentiment_counts.get('Negative', 0)/total*100:.1f}%)")
            print(f"   ⚪ Neutral: {sentiment_counts.get('Neutral', 0)} ({sentiment_counts.get('Neutral', 0)/total*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("✅ STEP 2 COMPLETE: Sentiment Analysis Done!")
    print("=" * 70)
    
    return results, brand_sentiment_df

if __name__ == "__main__":
    results, brand_sentiment = main()
