"""
Step 3: Keyword Extraction
Extracts keywords from reviews and discussions, separates into positive/negative
"""

import pandas as pd
import numpy as np
from collections import Counter
import re
from textblob import TextBlob
from load_data import load_data

# Laptop-related keywords to focus on
LAPTOP_TOPICS = [
    'battery', 'heating', 'performance', 'display', 'keyboard', 'build quality',
    'screen', 'processor', 'ram', 'storage', 'ssd', 'graphics', 'gpu',
    'trackpad', 'touchpad', 'webcam', 'speakers', 'audio', 'ports',
    'weight', 'design', 'cooling', 'fan', 'temperature', 'speed',
    'gaming', 'video', 'photo', 'editing', 'programming', 'work',
    'price', 'value', 'money', 'warranty', 'support', 'service'
]

def extract_keywords_from_text(text, sentiment='neutral'):
    """Extract relevant keywords from text"""
    if pd.isna(text) or text == '' or text == 'N/A':
        return []
    
    text_lower = str(text).lower()
    keywords = []
    
    # Extract laptop-related topics
    for topic in LAPTOP_TOPICS:
        if topic in text_lower:
            keywords.append(topic)
    
    # Extract common phrases
    phrases = [
        'battery life', 'battery drain', 'battery backup',
        'overheating', 'heating issue', 'gets hot',
        'fan noise', 'loud fan', 'noisy fan',
        'build quality', 'good build', 'poor build',
        'screen quality', 'display quality', 'bright display',
        'keyboard quality', 'comfortable keyboard',
        'fast performance', 'slow performance', 'lag',
        'good value', 'value for money', 'overpriced',
        'thermal throttling', 'thermal management'
    ]
    
    for phrase in phrases:
        if phrase in text_lower:
            keywords.append(phrase)
    
    return keywords


def categorize_keyword_sentiment(keyword, text):
    """Determine if keyword appears in positive or negative context"""
    text_lower = str(text).lower()
    
    # Find context around keyword
    keyword_pos = text_lower.find(keyword)
    if keyword_pos == -1:
        return 'neutral'
    
    # Get surrounding context (50 chars before and after)
    start = max(0, keyword_pos - 50)
    end = min(len(text_lower), keyword_pos + len(keyword) + 50)
    context = text_lower[start:end]
    
    # Analyze sentiment of context
    try:
        blob = TextBlob(context)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    except:
        return 'neutral'

def perform_keyword_extraction(data):
    """Extract keywords from all data sources"""
    
    print("=" * 70)
    print("STEP 3: KEYWORD EXTRACTION")
    print("=" * 70)
    
    all_keywords = {'positive': [], 'negative': [], 'neutral': []}
    
    # Process Amazon reviews
    print("\n" + "-" * 70)
    print("Extracting keywords from Amazon reviews...")
    print("-" * 70)
    
    if not data['amazon'].empty:
        amazon_df = data['amazon']
        for idx, row in amazon_df.iterrows():
            text = str(row.get('review_text', '')) + ' ' + str(row.get('comment_text', ''))
            keywords = extract_keywords_from_text(text)
            
            for keyword in keywords:
                sentiment = categorize_keyword_sentiment(keyword, text)
                all_keywords[sentiment].append(keyword)
        
        print(f"✅ Processed {len(amazon_df)} Amazon reviews")
    
    # Process Flipkart reviews
    print("\n" + "-" * 70)
    print("Extracting keywords from Flipkart reviews...")
    print("-" * 70)
    
    if not data['flipkart'].empty:
        flipkart_df = data['flipkart']
        for idx, row in flipkart_df.iterrows():
            text = str(row.get('reviews_comments', ''))
            keywords = extract_keywords_from_text(text)
            
            for keyword in keywords:
                sentiment = categorize_keyword_sentiment(keyword, text)
                all_keywords[sentiment].append(keyword)
        
        print(f"✅ Processed {len(flipkart_df)} Flipkart reviews")

    
    # Process Reddit posts
    print("\n" + "-" * 70)
    print("Extracting keywords from Reddit posts...")
    print("-" * 70)
    
    if not data['reddit'].empty:
        reddit_df = data['reddit']
        for idx, row in reddit_df.iterrows():
            text = str(row.get('post_title', '')) + ' ' + str(row.get('post_text', ''))
            keywords = extract_keywords_from_text(text)
            
            for keyword in keywords:
                sentiment = categorize_keyword_sentiment(keyword, text)
                all_keywords[sentiment].append(keyword)
        
        print(f"✅ Processed {len(reddit_df)} Reddit posts")
    
    # Process YouTube comments
    print("\n" + "-" * 70)
    print("Extracting keywords from YouTube comments...")
    print("-" * 70)
    
    if not data['youtube'].empty:
        youtube_df = data['youtube']
        for idx, row in youtube_df.iterrows():
            text = str(row.get('comment', ''))
            keywords = extract_keywords_from_text(text)
            
            for keyword in keywords:
                sentiment = categorize_keyword_sentiment(keyword, text)
                all_keywords[sentiment].append(keyword)
        
        print(f"✅ Processed {len(youtube_df)} YouTube comments")
    
    return all_keywords

def analyze_keywords(all_keywords):
    """Analyze and rank keywords by sentiment"""
    
    print("\n" + "=" * 70)
    print("KEYWORD ANALYSIS RESULTS")
    print("=" * 70)
    
    results = {}
    
    # Positive keywords
    if all_keywords['positive']:
        positive_counter = Counter(all_keywords['positive'])
        positive_df = pd.DataFrame(positive_counter.most_common(20), 
                                   columns=['Keyword', 'Count'])
        results['positive'] = positive_df
        
        print("\n✅ TOP 20 POSITIVE KEYWORDS:")
        print("-" * 70)
        for idx, row in positive_df.iterrows():
            print(f"   {idx+1}. {row['Keyword']}: {row['Count']} mentions")
    else:
        print("\n⚠️ No positive keywords found")
        results['positive'] = pd.DataFrame()
    
    # Negative keywords
    if all_keywords['negative']:
        negative_counter = Counter(all_keywords['negative'])
        negative_df = pd.DataFrame(negative_counter.most_common(20), 
                                   columns=['Keyword', 'Count'])
        results['negative'] = negative_df
        
        print("\n❌ TOP 20 NEGATIVE KEYWORDS:")
        print("-" * 70)
        for idx, row in negative_df.iterrows():
            print(f"   {idx+1}. {row['Keyword']}: {row['Count']} mentions")
    else:
        print("\n⚠️ No negative keywords found")
        results['negative'] = pd.DataFrame()

    
    # Neutral keywords
    if all_keywords['neutral']:
        neutral_counter = Counter(all_keywords['neutral'])
        neutral_df = pd.DataFrame(neutral_counter.most_common(20), 
                                 columns=['Keyword', 'Count'])
        results['neutral'] = neutral_df
        
        print("\n⚪ TOP 20 NEUTRAL KEYWORDS:")
        print("-" * 70)
        for idx, row in neutral_df.head(10).iterrows():
            print(f"   {idx+1}. {row['Keyword']}: {row['Count']} mentions")
    else:
        results['neutral'] = pd.DataFrame()
    
    return results

def main():
    """Main execution function"""
    
    # Load data
    print("Loading data from Step 1...")
    data = load_data()
    
    # Extract keywords
    all_keywords = perform_keyword_extraction(data)
    
    # Analyze keywords
    results = analyze_keywords(all_keywords)
    
    # Save results
    print("\n" + "=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)
    
    if not results['positive'].empty:
        results['positive'].to_csv('positive_keywords.csv', index=False)
        print("✅ Saved: positive_keywords.csv")
    
    if not results['negative'].empty:
        results['negative'].to_csv('negative_keywords.csv', index=False)
        print("✅ Saved: negative_keywords.csv")
    
    if not results['neutral'].empty:
        results['neutral'].to_csv('neutral_keywords.csv', index=False)
        print("✅ Saved: neutral_keywords.csv")
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("KEYWORD EXTRACTION SUMMARY")
    print("=" * 70)
    
    total_positive = len(all_keywords['positive'])
    total_negative = len(all_keywords['negative'])
    total_neutral = len(all_keywords['neutral'])
    total_all = total_positive + total_negative + total_neutral
    
    print(f"\n📊 Total keywords extracted: {total_all}")
    print(f"   ✅ Positive context: {total_positive} ({total_positive/total_all*100:.1f}%)")
    print(f"   ❌ Negative context: {total_negative} ({total_negative/total_all*100:.1f}%)")
    print(f"   ⚪ Neutral context: {total_neutral} ({total_neutral/total_all*100:.1f}%)")
    
    print(f"\n📈 Unique keywords:")
    print(f"   ✅ Positive: {len(set(all_keywords['positive']))}")
    print(f"   ❌ Negative: {len(set(all_keywords['negative']))}")
    print(f"   ⚪ Neutral: {len(set(all_keywords['neutral']))}")
    
    print("\n" + "=" * 70)
    print("✅ STEP 3 COMPLETE: Keyword Extraction Done!")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    results = main()
