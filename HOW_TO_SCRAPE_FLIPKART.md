# 🛒 How to Scrape Flipkart - Complete Guide

## 📋 What You'll Get

A CSV file (`flipkart.csv`) with these columns:
- **laptop_name** - Full product title
- **brand** - ASUS, Dell, HP, Lenovo, etc.
- **price** - Price in INR
- **rating** - Customer rating (1-5 stars)
- **specifications** - RAM, processor, storage, screen size, etc.
- **reviews_comments** - Customer reviews and comments (up to 5)

---

## 🚀 TWO METHODS TO SCRAPE

### Method 1: Selenium (RECOMMENDED - More Reliable)

**Why use this?**
- ✅ Opens real Chrome browser
- ✅ Bypasses bot detection
- ✅ Handles login popups automatically
- ✅ Gets reviews and detailed specs
- ✅ Higher success rate

**How to run:**

1. **Double-click this file:**
   ```
   run_flipkart_selenium.bat
   ```

2. **Follow the prompts:**
   - Enter search query: `gaming laptop`
   - Number of products: `10`
   - Headless mode: `y` (runs in background)

3. **Wait 2-5 minutes**

4. **Check `flipkart.csv`**

---

### Method 2: Simple Scraper (Faster but may be blocked)

**Why use this?**
- ⚡ Faster (no browser)
- 💻 Less resource intensive
- ⚠️ May be blocked by Flipkart

**How to run:**

1. **Double-click:**
   ```
   run_flipkart_scraper.bat
   ```

2. **Enter details and wait**

---

## 📝 Step-by-Step Example

### Using Selenium (Recommended):

```bash
# Step 1: Run the scraper
run_flipkart_selenium.bat

# Step 2: Enter query
Enter search query: gaming laptop under 70000

# Step 3: Enter count
How many products: 15

# Step 4: Headless mode
Run in background? y

# Step 5: Wait...
⏳ Scraping in progress...

# Step 6: Done!
✅ Data saved to flipkart.csv
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

## 📊 Sample Output (flipkart.csv)

```csv
laptop_name,brand,price,rating,specifications,reviews_comments
"ASUS ROG Strix G15 Gaming Laptop (AMD Ryzen 7, 16GB, RTX 4060)",ASUS,89999,4.5,"AMD Ryzen 7 5800H | 16GB DDR4 RAM | 512GB SSD | NVIDIA RTX 4060 | 15.6 inch FHD 144Hz","Great laptop for gaming || Cooling is excellent || Battery could be better || Value for money || Highly recommended"
"Dell Inspiron 15 3000 Intel Core i5 11th Gen",Dell,45999,4.3,"Intel i5 11th Gen | 8GB RAM | 512GB SSD | 15.6 inch FHD","Good for office work || Decent performance || Screen quality is good"
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

### Problem: "Login popup blocking"

**Solutions:**
- Selenium automatically closes popups
- Wait a few seconds for popup to close
- If persists, run in non-headless mode to see what's happening

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

Edit `scrapers/flipkart_scraper_selenium.py`, line 95:
```python
if product_link and idx <= 5:  # Change 5 to desired number
```

### Change timeout:

Edit line 73:
```python
time.sleep(4)  # Change 4 to desired seconds
```

### Change headless mode default:

Edit `scrape_flipkart_selenium.py`, line 27:
```python
headless = headless_input != 'n'  # Change logic here
```

---

## 📈 Tips for Best Results

1. **Use specific queries:**
   - ✅ "gaming laptop under 70000"
   - ✅ "business laptop i5 8gb"
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
   - Flipkart has popups that need time to close

---

## ⚠️ Important Legal Notes

1. **Personal Use Only**: Don't use for commercial purposes
2. **Respect Terms**: Follow Flipkart's Terms of Service
3. **Rate Limiting**: Script includes delays to be respectful
4. **No Reselling**: Don't sell scraped data
5. **Check Legality**: Ensure compliance with local laws

---

## 🎯 What to Do After Scraping

### 1. Open the CSV file:
```
flipkart.csv
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

### 4. Compare with Amazon:
- Load both amazon.csv and flipkart.csv
- Compare prices
- Analyze rating differences
- Find best deals

---

## 🔄 Integration with Main Dashboard

The scraped data can be loaded into the main dashboard:

```python
import pandas as pd

# Load scraped data
df_flipkart = pd.read_csv('flipkart.csv')
df_amazon = pd.read_csv('amazon.csv')

# Combine for analysis
df_combined = pd.concat([df_flipkart, df_amazon])

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
- [ ] `flipkart.csv` file exists
- [ ] File has 6 columns
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
run_flipkart_selenium.bat
```

**Simple Scraper:**
```bash
run_flipkart_scraper.bat
```

**Manual Python:**
```bash
python scrape_flipkart_selenium.py gaming laptop
```

---

## 📊 Flipkart vs Amazon Comparison

| Feature | Flipkart | Amazon |
|---------|----------|--------|
| Columns | 6 | 7 |
| Reviews | Combined | Separate |
| Popups | Login popup | None |
| Speed | Similar | Similar |
| Reliability | High (Selenium) | High (Selenium) |

Both scrapers work great! Use both to get comprehensive market data.

---

**Ready to scrape? Choose a method above and start!** 🎉
