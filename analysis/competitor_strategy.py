import pandas as pd

def generate_strategy(keywords_df, sentiment_df, products_df):
    """Generate competitor strategy based on analysis"""
    
    strategies = []
    
    # Price positioning strategy
    if not products_df.empty:
        strategies.append({
            'category': 'Pricing',
            'insight': 'Analyze competitor price ranges',
            'action': 'Position products competitively based on market data'
        })
    
    # Keyword-based content strategy
    if not keywords_df.empty:
        top_keywords = keywords_df.head(5)['keyword'].tolist()
        strategies.append({
            'category': 'Content Marketing',
            'insight': f'Top trending keywords: {", ".join(top_keywords)}',
            'action': 'Create content targeting these high-value keywords'
        })
    
    # Sentiment-based improvement strategy
    if not sentiment_df.empty:
        negative_ratio = (sentiment_df['label'] == 'negative').sum() / len(sentiment_df)
        if negative_ratio > 0.3:
            strategies.append({
                'category': 'Product Improvement',
                'insight': f'{negative_ratio*100:.1f}% negative sentiment detected',
                'action': 'Address common pain points in product features'
            })
    
    return pd.DataFrame(strategies)
