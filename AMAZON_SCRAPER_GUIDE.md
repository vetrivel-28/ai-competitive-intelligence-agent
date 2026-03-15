# 🛒 Amazon Detailed Scraper Guide

## What It Does

Scrapes detailed laptop information from Amazon India and saves to `amazon.csv` with these columns:

- **laptop_name** - Full product name
- **brand** - Extracted brand (ASUS, Dell, HP, Lenovo, etc.)
- **price** - Price in INR
- **rating** - Customer rating (out of 5)
- **specifications** - Technical specs (RAM, processor, storage, etc.)
- **review_text** - Customer review content (up to 3 reviews)
- **comment_text** - Review titles/comments (up to 3)

---

## 🚀 How to Run

### Method 1: Double-Click (Easiest)
```
run_amazon_scraper.bat
```

### Method 2: Command Line
```bash
python scrape_amazon_detailed.py
```

### Method 3: With Search Query
```bash
python scrape_amazon_detailed.py gaming laptop
```

---

## 📝 Usage Example

1. Run the script
2. Enter search query: `gaming laptop`
3. Enter number of products: `20`
4. Wait 2-5 minutes (depends on number of products)
5. Check `amazon.csv` for results

---

## ⚙️ How It Works

1. **Search Page**: Scrapes product listings from Amazon search results
2. **Product Pages**: Visits each product page for detailed info
3. **Reviews**: Extracts review text and comments
4. **CSV Export**: Saves all data to `amazon.csv`

---

## ⏱️ Time Estimates

- 10 products: ~2-3 minutes
- 20 products: ~4-6 minutes
- 50 products: ~10-15 minutes

*Includes respectful delays to avoid rate limiting*

---

## 📊 Sample Output

```csv
laptop_name,brand,price,rating,specifications,review_text,comment_text
"ASUS ROG Strix G15 Gaming Laptop",ASUS,89999,4.5,"Intel Core i7 | 16GB RAM | RTX 4060","Great laptop for gaming...","Best gaming laptop"
"Dell XPS 15 Laptop",Dell,125000,4.7,"Intel i7 | 32GB RAM | 1TB SSD","Excellent build quality...","Premium laptop"
```

---

## ⚠️ Important Notes

1. **Rate Limiting**: Script includes 2-second delays between requests
2. **Amazon Changes**: Website structure may change, requiring updates
3. **Internet Required**: Needs stable internet connection
4. **Legal**: For personal use only, respect Amazon's terms of service
5. **VPN**: May help if scraping is blocked

---

## 🔧 Troubleshooting

**No data scraped?**
- Check internet connection
- Try with VPN
- Reduce number of products
- Amazon may be blocking requests

**Missing reviews/comments?**
- Some products don't have reviews
- Amazon may limit access to review pages
- Try fewer products for better success rate

**Timeout errors?**
- Increase timeout in code (line 15, 30)
- Check internet speed
- Try again later

---

## 🎯 Tips for Best Results

1. Use specific search terms: "gaming laptop under 80000"
2. Start with 10-20 products to test
3. Run during off-peak hours
4. Use VPN if getting blocked
5. Check CSV file after completion

---

## 📁 Output File

**Location**: `amazon.csv` (same folder as script)

**Encoding**: UTF-8 with BOM (opens correctly in Excel)

**Format**: CSV (comma-separated values)

---

## 🔄 Integration with Dashboard

The detailed scraper is separate from the main dashboard. To use in dashboard:

1. Run detailed scraper to get `amazon.csv`
2. Load CSV in dashboard for analysis
3. Or use the simple `scrape_amazon()` function for quick results

---

## ✅ Success Checklist

- [ ] Script runs without errors
- [ ] `amazon.csv` file created
- [ ] File contains expected columns
- [ ] Data looks correct (prices, ratings, etc.)
- [ ] Reviews and comments populated (if available)

---

**Ready to scrape? Run `run_amazon_scraper.bat` now!** 🚀
