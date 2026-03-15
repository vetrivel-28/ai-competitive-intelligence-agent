# 🛒 How to Scrape Amazon - Complete Guide

## 📋 What You'll Get

A CSV file (`amazon.csv`) with these columns:
- **laptop_name** - Full product title
- **brand** - ASUS, Dell, HP, Lenovo, etc.
- **price** - Price in INR
- **rating** - Customer rating (1-5 stars)
- **specifications** - RAM, processor, storage, screen size, etc.
- **review_text** - Customer review content (up to 3 reviews)
- **comment_text** - Review titles/headlines (up to 3)

---

## 🚀 TWO METHODS TO SCRAPE

### Method 1: Selenium (RECOMMENDED - More Reliable)

**Why use this?**
- ✅ Opens real Chrome browser
- ✅ Bypasses bot detection
- ✅ Gets reviews and detailed specs
- ✅ Higher success rate

**How to run:**

1. **Double-click this file:**
   ```
   run_amazon_selenium.bat
   ```

2. **Follow the prompts:**
   - Enter search query: `gaming laptop`
   - Number of products: `10`
   - Headless mode: `y` (runs in background)

3. **Wait 2-5 minutes**

4. **Check `amazon.csv`**

---

### Method 2: Simple Scraper (Faster but may be blocked)

**Why use this?**
- ⚡ Faster (no browser)
- 💻 Less resource intensive
- ⚠️ May be blocked by Amazon

**How to run:**

1. **Double-click:**
   ```
   run_amazon_scraper.bat
   ```

2. **Enter details and wait**

---

## 📝 Step-by-Step Example

### Using Selenium (Recommended):

```bash
# Step 1: Run the scraper
run_amazon_selenium.bat

# Step 2: Enter query
Enter search query: gaming laptop under 80000

# Step 3: Enter count
How many products: 15

# Step 4: Headless mode
Run in background? y

# Step 5: Wait...
⏳ Scraping in progress...

# Step 6: Done!
✅ Data saved to amazon.csv
```

---

## ⏱️ Time Estimates

| Products | Time (Selenium) | Time (Simple) |
|----------|----------------|---------------|
| 5        | 1-2 min        | 30 sec        |
| 10       | 2-4 min        | 1 min         |
| 20       | 5-8 min        | 2 min         |
| 50       | 15-20 min      | 5 min         |

*Selenium is slower but more reliable*

---

## 📊 Sample Output (amazon.csv)

```csv
laptop_name,brand,price,rating,specifications,review_text,comment_text
"ASUS ROG Strix G15 Gaming Laptop, AMD Ryzen 7, RTX 4060",ASUS,89999,4.5,"AMD Ryzen 7 | 16GB RAM | 512GB SSD | RTX 4060","Great laptop for gaming and video editing. The cooling system works well. || Battery life could be better but performance is excellent.","Best gaming laptop in this price range || Excellent performance"
"Dell XPS 15 9530 Intel Core i7 13th Gen",Dell,125000,4.7,"Intel i7 13th Gen | 32GB RAM | 1TB SSD | 15.6 inch","Premium build quality. Display is stunning. || Perfect for professional work.","Worth every penny || Best laptop I've owned"
```

---

## 🔧 Troubleshooting

### Problem: "No data scraped"

**Solutions:**
1. Use Selenium method (more reliable)
2. Try with VPN
3. Reduce number of products
4. Check internet connection
5. Try different search query

### Problem: "Chrome driver error"

**Solutions:**
1. Update Chrome browser
2. Run: `pip install --upgrade selenium webdriver-manager`
3. Restart computer

### Problem: "Timeout errors"

**Solutions:**
1. Increase timeout in code
2. Check internet speed
3. Try fewer products
4. Run during off-peak hours

### Problem: "Missing reviews/comments"

**Solutions:**
- Normal! Not all products have reviews
- Selenium gets reviews for first 5 products only (to save time)
- Some products may have review access restricted

---

## ⚙️ Advanced Configuration

### Change number of products with reviews:

Edit `scrapers/amazon_scraper_selenium.py`, line 95:
```python
if product_link and idx <= 5:  # Change 5 to desired number
```

### Change timeout:

Edit line 73:
```python
time.sleep(3)  # Change 3 to desired seconds
```

### Change headless mode default:

Edit `scrape_amazon_selenium.py`, line 27:
```python
headless = headless_input != 'n'  # Change logic here
```

---

## 📈 Tips for Best Results

1. **Use specific queries:**
   - ✅ "gaming laptop under 80000"
   - ✅ "business laptop i7 16gb"
   - ❌ "laptop" (too broad)

2. **Start small:**
   - Test with 5-10 products first
   - Then increase if working well

3. **Best times to scrape:**
   - Early morning (6-9 AM IST)
   - Late night (11 PM - 2 AM IST)
   - Weekdays better than weekends

4. **Use VPN if blocked:**
   - Change location to India
   - Try different servers

5. **Be patient:**
   - Don't interrupt the process
   - Let it complete fully

---

## ⚠️ Important Legal Notes

1. **Personal Use Only**: Don't use for commercial purposes
2. **Respect Terms**: Follow Amazon's Terms of Service
3. **Rate Limiting**: Script includes delays to be respectful
4. **No Reselling**: Don't sell scraped data
5. **Check Legality**: Ensure compliance with local laws

---

## 🎯 What to Do After Scraping

### 1. Open the CSV file:
```
amazon.csv
```

### 2. Analyze in Excel/Google Sheets:
- Sort by price
- Filter by brand
- Check ratings
- Read reviews

### 3. Use in Dashboard:
- Load CSV into the main dashboard
- Run sentiment analysis
- Extract keywords
- Generate strategies

### 4. Export for reports:
- Create charts
- Make presentations
- Share insights

---

## 🔄 Integration with Main Dashboard

The scraped data can be loaded into the main dashboard:

```python
import pandas as pd

# Load scraped data
df = pd.read_csv('amazon.csv')

# Use in dashboard
# (Dashboard will auto-detect and analyze)
```

---

## ✅ Success Checklist

Before you start:
- [ ] Chrome browser installed
- [ ] Internet connection stable
- [ ] Enough disk space (CSV files are small)

After scraping:
- [ ] `amazon.csv` file exists
- [ ] File has 7 columns
- [ ] Data looks correct
- [ ] No error messages

---

## 🆘 Need Help?

If you're stuck:

1. Check error messages carefully
2. Try the other scraping method
3. Reduce number of products
4. Check internet connection
5. Try with VPN
6. Update Chrome browser
7. Restart computer

---

## 🚀 Quick Start Commands

**Selenium (Recommended):**
```bash
run_amazon_selenium.bat
```

**Simple Scraper:**
```bash
run_amazon_scraper.bat
```

**Manual Python:**
```bash
python scrape_amazon_selenium.py gaming laptop
```

---

**Ready to scrape? Choose a method above and start!** 🎉
