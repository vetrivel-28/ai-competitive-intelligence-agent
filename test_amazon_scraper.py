"""Quick test of Amazon detailed scraper"""
from scrapers.amazon_scraper import scrape_amazon_detailed

print("Testing Amazon Detailed Scraper...")
print("=" * 60)

# Test with just 2 products
df = scrape_amazon_detailed("laptop", max_products=2, save_csv=False)

if not df.empty:
    print("\n✅ Scraper working!")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nSample data:")
    print(df.to_string())
else:
    print("\n⚠️ No data returned - this is normal if Amazon blocks the request")
    print("Try running with VPN or adjusting headers")
