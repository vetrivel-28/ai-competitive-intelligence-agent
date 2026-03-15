"""
Step 1: Load and Combine Data
Loads all CSV files and combines them for analysis
"""

import pandas as pd
import os

def load_data():
    """
    Load all CSV files and combine them appropriately
    Returns: dict with combined dataframes
    """
    
    print("=" * 70)
    print("STEP 1: LOADING DATA")
    print("=" * 70)
    
    data = {}
    
    # Check which files exist
    files = {
        'amazon': 'amazon.csv',
        'flipkart': 'flipkart.csv',
        'reddit': 'reddit.csv',
        'youtube': 'youtube.csv'
    }
    
    print("\n📂 Checking for CSV files...")
    for name, filename in files.items():
        if os.path.exists(filename):
            print(f"   ✅ {filename} found")
        else:
            print(f"   ❌ {filename} NOT found")
    
    # Load Amazon data
    print("\n" + "-" * 70)
    print("Loading Amazon Data...")
    print("-" * 70)
    try:
        amazon_df = pd.read_csv('amazon.csv', encoding='utf-8-sig')
        print(f"✅ Loaded {len(amazon_df)} Amazon products")
        print(f"   Columns: {list(amazon_df.columns)}")
        data['amazon'] = amazon_df
    except Exception as e:
        print(f"❌ Error loading Amazon data: {e}")
        data['amazon'] = pd.DataFrame()
    
    # Load Flipkart data
    print("\n" + "-" * 70)
    print("Loading Flipkart Data...")
    print("-" * 70)
    try:
        flipkart_df = pd.read_csv('flipkart.csv', encoding='utf-8-sig')
        print(f"✅ Loaded {len(flipkart_df)} Flipkart products")
        print(f"   Columns: {list(flipkart_df.columns)}")
        data['flipkart'] = flipkart_df
    except Exception as e:
        print(f"❌ Error loading Flipkart data: {e}")
        data['flipkart'] = pd.DataFrame()
    
    # Load Reddit data
    print("\n" + "-" * 70)
    print("Loading Reddit Data...")
    print("-" * 70)
    try:
        reddit_df = pd.read_csv('reddit.csv', encoding='utf-8-sig')
        print(f"✅ Loaded {len(reddit_df)} Reddit posts")
        print(f"   Columns: {list(reddit_df.columns)}")
        data['reddit'] = reddit_df
    except Exception as e:
        print(f"❌ Error loading Reddit data: {e}")
        data['reddit'] = pd.DataFrame()
    
    # Load YouTube data
    print("\n" + "-" * 70)
    print("Loading YouTube Data...")
    print("-" * 70)
    try:
        youtube_df = pd.read_csv('youtube.csv', encoding='utf-8-sig')
        print(f"✅ Loaded {len(youtube_df)} YouTube comments")
        print(f"   Columns: {list(youtube_df.columns)}")
        data['youtube'] = youtube_df
    except Exception as e:
        print(f"❌ Error loading YouTube data: {e}")
        data['youtube'] = pd.DataFrame()
    
    # Combine Amazon and Flipkart for product analysis
    print("\n" + "=" * 70)
    print("COMBINING PRODUCT DATA (Amazon + Flipkart)")
    print("=" * 70)
    
    product_dfs = []
    
    if not data['amazon'].empty:
        amazon_normalized = data['amazon'].copy()
        amazon_normalized['source'] = 'Amazon'
        # Standardize column names
        amazon_normalized = amazon_normalized.rename(columns={
            'product_name': 'laptop_name',
            'product_price': 'price',
            'product_rating': 'rating',
            'product_reviews': 'reviews_comments'
        })
        product_dfs.append(amazon_normalized)
        print(f"✅ Added {len(amazon_normalized)} Amazon products")
    
    if not data['flipkart'].empty:
        flipkart_normalized = data['flipkart'].copy()
        flipkart_normalized['source'] = 'Flipkart'
        product_dfs.append(flipkart_normalized)
        print(f"✅ Added {len(flipkart_normalized)} Flipkart products")
    
    if product_dfs:
        combined_products = pd.concat(product_dfs, ignore_index=True, sort=False)
        data['combined_products'] = combined_products
        print(f"\n📦 Total Combined Products: {len(combined_products)}")
        print(f"   Amazon: {len(combined_products[combined_products['source'] == 'Amazon'])}")
        print(f"   Flipkart: {len(combined_products[combined_products['source'] == 'Flipkart'])}")
        print(f"   Columns: {list(combined_products.columns)}")
    else:
        data['combined_products'] = pd.DataFrame()
        print("❌ No product data to combine")
    
    # Combine Reddit and YouTube for public opinion analysis
    print("\n" + "=" * 70)
    print("COMBINING PUBLIC OPINION DATA (Reddit + YouTube)")
    print("=" * 70)
    
    opinion_dfs = []
    
    if not data['reddit'].empty:
        reddit_normalized = data['reddit'].copy()
        reddit_normalized['source'] = 'Reddit'
        reddit_normalized['content'] = reddit_normalized['post_title'] + ' ' + reddit_normalized['post_text'].fillna('')
        reddit_normalized['sentiment'] = reddit_normalized['sentiment_context']
        opinion_dfs.append(reddit_normalized[['source', 'laptop_name', 'content', 'sentiment']])
        print(f"✅ Added {len(reddit_normalized)} Reddit posts")
    
    if not data['youtube'].empty:
        youtube_normalized = data['youtube'].copy()
        youtube_normalized['source'] = 'YouTube'
        youtube_normalized['content'] = youtube_normalized['comment']
        youtube_normalized['sentiment'] = 'N/A'  # Will be analyzed later
        opinion_dfs.append(youtube_normalized[['source', 'laptop_name', 'content', 'sentiment']])
        print(f"✅ Added {len(youtube_normalized)} YouTube comments")
    
    if opinion_dfs:
        combined_opinions = pd.concat(opinion_dfs, ignore_index=True, sort=False)
        data['combined_opinions'] = combined_opinions
        print(f"\n💬 Total Combined Opinions: {len(combined_opinions)}")
        print(f"   Reddit: {len(combined_opinions[combined_opinions['source'] == 'Reddit'])}")
        print(f"   YouTube: {len(combined_opinions[combined_opinions['source'] == 'YouTube'])}")
        print(f"   Columns: {list(combined_opinions.columns)}")
    else:
        data['combined_opinions'] = pd.DataFrame()
        print("❌ No opinion data to combine")
    
    # Summary
    print("\n" + "=" * 70)
    print("DATA LOADING SUMMARY")
    print("=" * 70)
    print(f"\n📊 Individual Datasets:")
    print(f"   Amazon Products: {len(data.get('amazon', []))}")
    print(f"   Flipkart Products: {len(data.get('flipkart', []))}")
    print(f"   Reddit Posts: {len(data.get('reddit', []))}")
    print(f"   YouTube Comments: {len(data.get('youtube', []))}")
    
    print(f"\n📦 Combined Datasets:")
    print(f"   Product Data (Amazon + Flipkart): {len(data.get('combined_products', []))}")
    print(f"   Opinion Data (Reddit + YouTube): {len(data.get('combined_opinions', []))}")
    
    print("\n" + "=" * 70)
    print("✅ STEP 1 COMPLETE: All data loaded successfully!")
    print("=" * 70)
    
    return data

if __name__ == "__main__":
    # Load all data
    data = load_data()
    
    # Display sample data
    print("\n" + "=" * 70)
    print("SAMPLE DATA PREVIEW")
    print("=" * 70)
    
    if not data['combined_products'].empty:
        print("\n📦 Combined Products (first 3 rows):")
        print("-" * 70)
        print(data['combined_products'].head(3))
    
    if not data['combined_opinions'].empty:
        print("\n💬 Combined Opinions (first 3 rows):")
        print("-" * 70)
        print(data['combined_opinions'].head(3))
