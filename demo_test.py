"""Quick demo of the dashboard functionality"""
import pandas as pd
from analysis.sentiment_analyzer import analyze_sentiment
from analysis.keyword_extractor import extract_keywords
from analysis.competitor_strategy import generate_strategy

print("=" * 60)
print("LAPTOP MARKET INTELLIGENCE DASHBOARD - DEMO")
print("=" * 60)

# Sample data
print("\n📊 Sample Product Data:")
products_data = {
    'source': ['Amazon', 'Amazon', 'Flipkart', 'Flipkart'],
    'title': [
        'ASUS ROG Strix G15 Gaming Laptop RTX 4060',
        'Dell XPS 15 Intel i7 16GB RAM',
        'HP Pavilion Gaming Laptop AMD Ryzen 7',
        'Lenovo IdeaPad Slim 5 14 inch'
    ],
    'price': ['89999', '125000', '75999', '54999'],
    'rating': ['4.5', '4.7', '4.3', '4.6']
}
products_df = pd.DataFrame(products_data)
print(products_df.to_string(index=False))

# Sample discussions
print("\n💬 Sample Discussion Data:")
discussions_data = {
    'source': ['Reddit', 'Reddit', 'Reddit'],
    'title': [
        'Best gaming laptop under 90k?',
        'ASUS ROG vs HP Omen - which is better?',
        'Disappointed with Dell XPS battery life'
    ],
    'text': [
        'Looking for a laptop with RTX 4060 for gaming and video editing',
        'Both have similar specs but ASUS has better cooling',
        'Battery drains too fast, only lasts 3 hours'
    ]
}
discussions_df = pd.DataFrame(discussions_data)
print(discussions_df[['source', 'title']].to_string(index=False))

# Sentiment Analysis
print("\n🎭 SENTIMENT ANALYSIS:")
print("-" * 60)
texts = discussions_df['text'].tolist()
sentiment_df = analyze_sentiment(texts)
print(sentiment_df.to_string(index=False))

sentiment_counts = sentiment_df['label'].value_counts()
print(f"\n📈 Sentiment Summary:")
for label, count in sentiment_counts.items():
    print(f"  {label.capitalize()}: {count} ({count/len(sentiment_df)*100:.1f}%)")

# Keyword Extraction
print("\n🔑 KEYWORD EXTRACTION:")
print("-" * 60)
all_text = products_df['title'].tolist() + discussions_df['title'].tolist()
keywords_df = extract_keywords(all_text, top_n=10)
print(keywords_df.to_string(index=False))

# Strategy Generation
print("\n🎯 COMPETITOR STRATEGY:")
print("-" * 60)
strategy_df = generate_strategy(keywords_df, sentiment_df, products_df)
for idx, row in strategy_df.iterrows():
    print(f"\n📌 {row['category']}")
    print(f"   Insight: {row['insight']}")
    print(f"   Action: {row['action']}")

print("\n" + "=" * 60)
print("✅ Demo Complete! All systems working perfectly.")
print("=" * 60)
print("\n🚀 To launch the full dashboard, run:")
print("   streamlit run app.py")
print("\nOr double-click: run_dashboard.bat")
