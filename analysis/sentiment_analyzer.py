from textblob import TextBlob
import pandas as pd

def analyze_sentiment(text_data):
    """Analyze sentiment of text data"""
    sentiments = []
    
    for text in text_data:
        if pd.isna(text) or text == '':
            sentiments.append({'polarity': 0, 'subjectivity': 0, 'label': 'neutral'})
            continue
            
        blob = TextBlob(str(text))
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            label = 'positive'
        elif polarity < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        sentiments.append({
            'polarity': polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'label': label
        })
    
    return pd.DataFrame(sentiments)
