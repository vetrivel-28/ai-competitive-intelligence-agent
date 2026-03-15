"""
Reddit scraper for laptop discussions using JSON API
Saves to reddit.csv with columns: post_title, post_text, laptop_name, sentiment_context
"""

import requests
import pandas as pd
import time
import re

def extract_laptop_name(text):
    """Extract laptop name/model from text"""
    # Common laptop patterns
    patterns = [
        r'(Dell\s+\w+\s*\d+)',
        r'(HP\s+\w+\s*\d+)',
        r'(Lenovo\s+\w+\s*\d+)',
        r'(ASUS\s+\w+\s*\d+)',
        r'(Acer\s+\w+\s*\d+)',
        r'(MSI\s+\w+\s*\d+)',
        r'(MacBook\s+\w+)',
        r'(ThinkPad\s+\w+\d+)',
        r'(Inspiron\s+\d+)',
        r'(Pavilion\s+\d+)',
        r'(ROG\s+\w+)',
        r'(Predator\s+\w+)',
        r'(Legion\s+\w+\d*)',
        r'(XPS\s+\d+)',
        r'(Spectre\s+\w+)',
        r'(Envy\s+\d+)',
        r'(IdeaPad\s+\w+)',
        r'(VivoBook\s+\w+)',
        r'(ZenBook\s+\w+)',
    ]
    
    combined_text = text.lower()
    for pattern in patterns:
        match = re.search(pattern, combined_text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Fallback: check for brand names
    brands = ['Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'MSI', 'Apple', 'MacBook', 'ThinkPad', 
              'Surface', 'Razer', 'Alienware', 'LG', 'Samsung']
    for brand in brands:
        if brand.lower() in combined_text:
            return brand
    
    return 'Generic Laptop'

def analyze_sentiment_context(text):
    """Analyze sentiment context from post text"""
    text_lower = text.lower()
    
    positive_words = ['great', 'excellent', 'amazing', 'love', 'best', 'perfect', 'good', 
                      'recommend', 'happy', 'satisfied', 'awesome', 'fantastic', 'worth',
                      'solid', 'reliable', 'impressive', 'outstanding']
    negative_words = ['bad', 'terrible', 'worst', 'hate', 'poor', 'disappointed', 'issue',
                      'problem', 'broken', 'fail', 'regret', 'avoid', 'waste', 'horrible',
                      'awful', 'useless', 'defect']
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return f"Positive ({positive_count} positive indicators)"
    elif negative_count > positive_count:
        return f"Negative ({negative_count} negative indicators)"
    else:
        return "Neutral/Mixed"

def scrape_reddit(query, max_posts=20, save_csv=True, headless=True):
    """
    Scrape Reddit discussions about laptops using JSON API
    Returns: DataFrame with columns: post_title, post_text, laptop_name, sentiment_context
    """
    
    print("=" * 70)
    print("REDDIT SCRAPER (JSON API)")
    print("=" * 70)
    print(f"\n🔍 Query: {query}")
    print(f"📊 Target: {max_posts} posts")
    print(f"⏳ Fetching data...\n")
    
    posts = []
    
    try:
        # Use Reddit's JSON API
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Try multiple subreddits
        subreddits = ['laptops', 'SuggestALaptop', 'GamingLaptops', 'laptop']
        
        for subreddit in subreddits:
            if len(posts) >= max_posts:
                break
                
            try:
                # Search in specific subreddit
                url = f"https://www.reddit.com/r/{subreddit}/search.json?q={query}&restrict_sr=1&limit=100"
                print(f"🌐 Searching r/{subreddit}...")
                
                response = requests.get(url, headers=headers, timeout=15)
                time.sleep(2)  # Be nice to Reddit's servers
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data and 'children' in data['data']:
                        for post in data['data']['children']:
                            if len(posts) >= max_posts:
                                break
                            
                            try:
                                post_data = post['data']
                                
                                post_title = post_data.get('title', '').strip()
                                post_text = post_data.get('selftext', '').strip()
                                
                                # Skip if no title
                                if not post_title:
                                    continue
                                
                                # Extract laptop name
                                combined_text = f"{post_title} {post_text}"
                                laptop_name = extract_laptop_name(combined_text)
                                
                                # Analyze sentiment
                                sentiment_context = analyze_sentiment_context(combined_text)
                                
                                posts.append({
                                    'post_title': post_title,
                                    'post_text': post_text,
                                    'laptop_name': laptop_name,
                                    'sentiment_context': sentiment_context
                                })
                                
                                print(f"   ✅ {post_title[:60]}...")
                                
                            except Exception as e:
                                continue
                        
                        print(f"   📦 Found {len([p for p in posts if subreddit in str(p)])} posts from r/{subreddit}")
                
            except Exception as e:
                print(f"   ⚠️ Could not access r/{subreddit}: {e}")
                continue
        
        # If still no posts, try general search
        if len(posts) == 0:
            try:
                url = f"https://www.reddit.com/search.json?q={query}&limit=100"
                print(f"\n🌐 Trying general Reddit search...")
                
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data and 'children' in data['data']:
                        for post in data['data']['children'][:max_posts]:
                            try:
                                post_data = post['data']
                                
                                post_title = post_data.get('title', '').strip()
                                post_text = post_data.get('selftext', '').strip()
                                
                                if not post_title:
                                    continue
                                
                                combined_text = f"{post_title} {post_text}"
                                laptop_name = extract_laptop_name(combined_text)
                                sentiment_context = analyze_sentiment_context(combined_text)
                                
                                posts.append({
                                    'post_title': post_title,
                                    'post_text': post_text,
                                    'laptop_name': laptop_name,
                                    'sentiment_context': sentiment_context
                                })
                                
                                print(f"   ✅ {post_title[:60]}...")
                                
                            except Exception as e:
                                continue
            except Exception as e:
                print(f"   ⚠️ General search failed: {e}")
        
        print(f"\n✅ Successfully scraped {len(posts)} posts")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
    
    # Create DataFrame
    df = pd.DataFrame(posts)
    
    # Save to CSV
    if save_csv and not df.empty:
        filename = 'reddit.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n💾 Data saved to {filename}")
    
    return df

if __name__ == "__main__":
    # Test run
    df = scrape_reddit("laptop recommendations", max_posts=10, headless=False)
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(df)


if __name__ == "__main__":
    # Test run
    df = scrape_reddit("laptop recommendations", max_posts=10)
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    print(df)
