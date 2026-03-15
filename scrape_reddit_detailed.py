"""
Standalone script to scrape Reddit laptop discussions
Saves to reddit.csv with columns: post_title, post_text, laptop_name, sentiment_context
"""

from scrapers.reddit_scraper import scrape_reddit
import sys

def main():
    print("=" * 70)
    print("REDDIT LAPTOP DISCUSSION SCRAPER")
    print("=" * 70)
    
    # Get search query
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("\nEnter search query (e.g., 'laptop recommendations', 'best gaming laptop'): ").strip()
        if not query:
            query = "laptop"
    
    # Get number of posts
    try:
        max_posts = int(input("How many posts to scrape? (default 20): ").strip() or "20")
    except:
        max_posts = 20
    
    print(f"\n🔍 Searching for: '{query}'")
    print(f"📊 Target: {max_posts} posts")
    print(f"⏳ This may take a few minutes...\n")
    
    # Scrape data
    df = scrape_reddit(query, max_posts=max_posts, save_csv=True, headless=True)
    
    # Display results
    if not df.empty:
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETE!")
        print("=" * 70)
        print(f"\n📦 Total posts scraped: {len(df)}")
        print(f"📁 File saved: reddit.csv")
        print("\n📋 Column Summary:")
        print(f"  - post_title: {df['post_title'].notna().sum()} entries")
        print(f"  - post_text: {(df['post_text'] != '').sum()} entries")
        print(f"  - laptop_name: {df['laptop_name'].notna().sum()} entries")
        print(f"  - sentiment_context: {df['sentiment_context'].notna().sum()} entries")
        
        print("\n📊 Sample Data (first 3 posts):")
        print("-" * 70)
        for idx, row in df.head(3).iterrows():
            print(f"\n{idx + 1}. {row['post_title'][:60]}...")
            print(f"   Laptop: {row['laptop_name']}")
            print(f"   Sentiment: {row['sentiment_context']}")
            if row['post_text']:
                print(f"   Text: {row['post_text'][:80]}...")
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Check reddit.csv for full data")
        print("=" * 70)
    else:
        print("\n❌ No data scraped. Please check your internet connection or try again.")

if __name__ == "__main__":
    main()
