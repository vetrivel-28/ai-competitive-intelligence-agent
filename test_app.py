"""Test script to verify all components work"""
import sys

print("Testing imports...")

try:
    import streamlit as st
    print("✓ Streamlit imported")
except Exception as e:
    print(f"✗ Streamlit error: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print("✓ Pandas imported")
except Exception as e:
    print(f"✗ Pandas error: {e}")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
    print("✓ BeautifulSoup imported")
except Exception as e:
    print(f"✗ BeautifulSoup error: {e}")
    sys.exit(1)

try:
    from textblob import TextBlob
    print("✓ TextBlob imported")
except Exception as e:
    print(f"✗ TextBlob error: {e}")
    sys.exit(1)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    print("✓ Scikit-learn imported")
except Exception as e:
    print(f"✗ Scikit-learn error: {e}")
    sys.exit(1)

try:
    import plotly.express as px
    print("✓ Plotly imported")
except Exception as e:
    print(f"✗ Plotly error: {e}")
    sys.exit(1)

print("\nTesting scrapers...")
try:
    from scrapers.amazon_scraper import scrape_amazon
    from scrapers.flipkart_scraper import scrape_flipkart
    from scrapers.reddit_scraper import scrape_reddit
    from scrapers.youtube_scraper import scrape_youtube
    print("✓ All scrapers imported")
except Exception as e:
    print(f"✗ Scraper error: {e}")
    sys.exit(1)

print("\nTesting analysis modules...")
try:
    from analysis.sentiment_analyzer import analyze_sentiment
    from analysis.keyword_extractor import extract_keywords
    from analysis.competitor_strategy import generate_strategy
    print("✓ All analysis modules imported")
except Exception as e:
    print(f"✗ Analysis error: {e}")
    sys.exit(1)

print("\nTesting sentiment analysis...")
try:
    test_texts = ["This laptop is amazing!", "Terrible product", "It's okay"]
    result = analyze_sentiment(test_texts)
    print(f"✓ Sentiment analysis works: {len(result)} results")
    print(result)
except Exception as e:
    print(f"✗ Sentiment analysis error: {e}")
    sys.exit(1)

print("\nTesting keyword extraction...")
try:
    test_texts = ["gaming laptop with RTX 4090", "best laptop for programming", "affordable gaming laptop"]
    result = extract_keywords(test_texts, top_n=5)
    print(f"✓ Keyword extraction works: {len(result)} keywords")
    print(result)
except Exception as e:
    print(f"✗ Keyword extraction error: {e}")
    sys.exit(1)

print("\n✅ All tests passed! The application is ready to run.")
print("\nTo start the dashboard, run:")
print("streamlit run app.py")
