"""
Standalone script to scrape detailed Amazon laptop data
Saves to amazon.csv with columns: laptop_name, brand, price, rating, specifications, review_text, comment_text
"""

from scrapers.amazon_scraper import scrape_amazon_detailed
import sys

def main():
    print("=" * 70)
    print("AMAZON LAPTOP DETAILED SCRAPER")
    print("=" * 70)
    
    # Get search query
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("\nEnter search query (e.g., 'gaming laptop'): ").strip()
        if not query:
            query = "laptop"
    
    # Get number of products
    try:
        max_products = int(input("How many products to scrape? (default 20): ").strip() or "20")
    except:
        max_products = 20
    
    print(f"\n🔍 Searching for: '{query}'")
    print(f"📊 Target: {max_products} products")
    print(f"⏳ This may take a few minutes...\n")
    
    # Scrape data
    df = scrape_amazon_detailed(query, max_products=max_products, save_csv=True)
    
    # Display results
    if not df.empty:
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETE!")
        print("=" * 70)
        print(f"\n📦 Total products scraped: {len(df)}")
        print(f"📁 File saved: amazon.csv")
        print("\n📋 Column Summary:")
        print(f"  - laptop_name: {df['laptop_name'].notna().sum()} entries")
        print(f"  - brand: {df['brand'].notna().sum()} entries")
        print(f"  - price: {(df['price'] != 'N/A').sum()} entries")
        print(f"  - rating: {(df['rating'] != 'N/A').sum()} entries")
        print(f"  - specifications: {(df['specifications'] != 'N/A').sum()} entries")
        print(f"  - review_text: {(df['review_text'] != 'N/A').sum()} entries")
        print(f"  - comment_text: {(df['comment_text'] != 'N/A').sum()} entries")
        
        print("\n📊 Sample Data (first 3 rows):")
        print("-" * 70)
        for idx, row in df.head(3).iterrows():
            print(f"\n{idx + 1}. {row['laptop_name'][:60]}...")
            print(f"   Brand: {row['brand']}")
            print(f"   Price: ₹{row['price']}")
            print(f"   Rating: {row['rating']}")
            print(f"   Specs: {row['specifications'][:80]}...")
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Check amazon.csv for full data")
        print("=" * 70)
    else:
        print("\n❌ No data scraped. Please check your internet connection or try again.")

if __name__ == "__main__":
    main()
