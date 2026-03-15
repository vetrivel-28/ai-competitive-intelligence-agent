from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import re

def extract_keywords(texts, top_n=20):
    """Extract top keywords using TF-IDF"""
    
    # Clean texts
    cleaned_texts = [re.sub(r'[^a-zA-Z0-9\s]', '', str(text).lower()) for text in texts]
    
    try:
        vectorizer = TfidfVectorizer(
            max_features=top_n,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
        feature_names = vectorizer.get_feature_names_out()
        
        # Get average TF-IDF scores
        avg_scores = tfidf_matrix.mean(axis=0).A1
        keywords_df = pd.DataFrame({
            'keyword': feature_names,
            'score': avg_scores
        }).sort_values('score', ascending=False)
        
        return keywords_df
        
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return pd.DataFrame(columns=['keyword', 'score'])
