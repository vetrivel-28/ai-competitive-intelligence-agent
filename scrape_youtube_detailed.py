"""
Standalone script to scrape YouTube laptop review comments
Saves to youtube.csv with columns: video_title, laptop_name, comment, reply
"""

from scrapers.youtube_scraper import scrape_youtube
import sys

def main():
    print("=" * 70)
    print("YOUTUBE LAPTOP REVIEW SCRAPER")
    print("=" * 70)
    
    # Get search query
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("\nEnter search query (e.g., 'laptop review', 'gaming laptop review'): ").strip()
        if not query:
            query = "laptop review"
    
    # Get number of videos
    try:
        max_videos = int(input("How many videos to scrape? (default 5): ").strip() or "5")
    except:
        max_videos = 5
    
    # Get comments per video
    try:
        comments_per_video = int(input("Comments per video? (default 10): ").strip() or "10")
    except:
        comments_per_video = 10
    
    print(f"\n🔍 Searching for: '{query}'")
    print(f"📊 Target: {max_videos} videos, {comments_per_video} comments each")
    print(f"⏳ This may take several minutes...")
    print(f"💡 TIP: Browser will be visible for better reliability\n")
    
    # Scrape data (non-headless for better success)
    df = scrape_youtube(query, max_videos=max_videos, comments_per_video=comments_per_video, 
                        save_csv=True, headless=False)
    
    # Display results
    if not df.empty:
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETE!")
        print("=" * 70)
        print(f"\n📦 Total comments scraped: {len(df)}")
        print(f"📁 File saved: youtube.csv")
        print("\n📋 Column Summary:")
        print(f"  - video_title: {df['video_title'].notna().sum()} entries")
        print(f"  - laptop_name: {df['laptop_name'].notna().sum()} entries")
        print(f"  - comment: {df['comment'].notna().sum()} entries")
        print(f"  - reply: {(df['reply'] != 'N/A').sum()} entries with replies")
        
        print("\n📊 Sample Data (first 3 comments):")
        print("-" * 70)
        for idx, row in df.head(3).iterrows():
            print(f"\n{idx + 1}. Video: {row['video_title'][:50]}...")
            print(f"   Laptop: {row['laptop_name']}")
            print(f"   Comment: {row['comment'][:80]}...")
            if row['reply'] != 'N/A':
                print(f"   Reply: {row['reply'][:60]}...")
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Check youtube.csv for full data")
        print("=" * 70)
    else:
        print("\n❌ No data scraped. Please check your internet connection or try again.")

if __name__ == "__main__":
    main()
