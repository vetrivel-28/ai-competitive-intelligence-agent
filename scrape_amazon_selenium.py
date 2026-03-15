"""
Run Amazon scraper with Selenium (more reliable)
"""

from scrapers.amazon_scraper_selenium import scrape_amazon_selenium
import sys

def main():
    print("\n" + "=" * 70)
    print("AMAZON LAPTOP SCRAPER (SELENIUM)")
    print("=" * 70)
    print("\nThis scraper uses Chrome browser for better reliability")
    print("Chrome will open automatically (or run in background if headless)")
    
    # Get search query
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("\nEnter search query (e.g., 'gaming laptop'): ").strip()
        if not query:
            query = "laptop"
    
    # Get number of products
    try:
        max_products = int(input("How many products to scrape? (default 10): ").strip() or "10")
    except:
        max_products = 10
    
    # Headless mode
    headless_input = input("Run in background (headless)? (y/n, default y): ").strip().lower()
    headless = headless_input != 'n'
    
    print(f"\n⚙️ Configuration:")
    print(f"   Query: {query}")
    print(f"   Products: {max_products}")
    print(f"   Mode: {'Headless (background)' if headless else 'Visible browser'}")
    print(f"\n⏳ Starting scraper...\n")
    
    # Scrape
    df = scrape_amazon_selenium(query, max_products=max_products, save_csv=True, headless=headless)
    
    # Display results
    if not df.empty:
        print("\n" + "=" * 70)
        print("✅ SCRAPING COMPLETE!")
        print("=" * 70)
        print(f"\n📦 Total products: {len(df)}")
        print(f"📁 File: amazon.csv")
        print("\n📊 Column Summary:")
        for col in df.columns:
            non_na = (df[col] != 'N/A').sum()
            print(f"  - {col}: {non_na}/{len(df)} entries")
        
        print("\n📋 Sample Data:")
        print("-" * 70)
        for idx, row in df.head(3).iterrows():
            print(f"\n{idx + 1}. {row['laptop_name'][:60]}")
            print(f"   Brand: {row['brand']} | Price: ₹{row['price']} | Rating: {row['rating']}")
        
        print("\n" + "=" * 70)
        print("✅ Check amazon.csv for complete data!")
        print("=" * 70)
    else:
        print("\n❌ No data scraped. Please try again or check your internet connection.")

if __name__ == "__main__":
    main()
