# Laptop Market Intelligence Dashboard

AI-powered dashboard for analyzing laptop market data from multiple sources.

## Features

- Multi-source data scraping (Amazon, Flipkart, Reddit, YouTube)
- Sentiment analysis of reviews and discussions
- Keyword extraction for competitor insights
- AI-generated strategy recommendations
- Interactive visualizations

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download NLTK data (first time only):
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

3. Run the dashboard:
```bash
streamlit run app.py
```

## Usage

1. Enter search query (e.g., "gaming laptop")
2. Select data sources
3. Click "Fetch Data"
4. Explore insights across tabs

## Note

- Web scraping may require adjustments based on website structure changes
- YouTube scraper requires API key for full functionality
- Respect rate limits and terms of service
