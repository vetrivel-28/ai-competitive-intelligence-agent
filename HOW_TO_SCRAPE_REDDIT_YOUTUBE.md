# Reddit & YouTube Scraping Guide

## 🎯 What Gets Scraped

### Reddit (reddit.csv)
- **post_title**: Title of the Reddit post
- **post_text**: Full text content of the post
- **laptop_name**: Extracted laptop model/brand
- **sentiment_context**: Positive/Negative/Neutral analysis

### YouTube (youtube.csv)
- **video_title**: Title of the YouTube video
- **laptop_name**: Extracted laptop model/brand from video
- **comment**: User comment text
- **reply**: Reply to the comment (if available)

---

## 🚀 How to Run

### Option 1: Double-Click Batch Files (EASIEST)

**For Reddit:**
1. Double-click `run_reddit_scraper.bat`
2. Enter search query (e.g., "laptop recommendations")
3. Enter number of posts (e.g., 20)
4. Wait for scraping to complete
5. Check `reddit.csv` for results

**For YouTube:**
1. Double-click `run_youtube_scraper.bat`
2. Enter search query (e.g., "laptop review")
3. Enter number of videos (e.g., 5)
4. Enter comments per video (e.g., 10)
5. Wait for scraping to complete
6. Check `youtube.csv` for results

### Option 2: Command Line

**Reddit:**
```bash
python scrape_reddit_detailed.py
```

**YouTube:**
```bash
python scrape_youtube_detailed.py
```

---

## 📊 Example Queries

### Reddit Queries
- "laptop recommendations"
- "best gaming laptop"
- "laptop for programming"
- "Dell XPS review"
- "MacBook vs Windows laptop"

### YouTube Queries
- "laptop review"
- "gaming laptop review 2024"
- "best budget laptop"
- "Dell laptop unboxing"
- "laptop comparison"

---

## ⚙️ Features

### Reddit Scraper
✅ Extracts post titles and full text
✅ Identifies laptop models automatically
✅ Analyzes sentiment (Positive/Negative/Neutral)
✅ Handles dynamic content loading
✅ Saves to reddit.csv

### YouTube Scraper
✅ Searches videos by query
✅ Extracts video titles
✅ Scrapes comments from each video
✅ Captures replies to comments
✅ Identifies laptop models from video titles
✅ Saves to youtube.csv

---

## 💡 Tips

1. **Start Small**: Try 5-10 items first to test
2. **Be Patient**: YouTube scraping takes longer (needs to visit each video)
3. **Good Queries**: Use specific terms like "laptop review" or brand names
4. **Headless Mode**: Runs in background by default (faster)
5. **Check Results**: Open CSV files in Excel or any spreadsheet app

---

## 🔧 Troubleshooting

**If scraping fails:**
1. Check your internet connection
2. Try with fewer items (5 instead of 20)
3. Use more specific search queries
4. Wait a few minutes and try again

**If no data appears:**
- Reddit/YouTube might be blocking automated access
- Try running with `headless=False` to see what's happening
- Check if the search query returns results manually first

---

## 📁 Output Files

- `reddit.csv` - Reddit discussions
- `youtube.csv` - YouTube comments and replies

Both files are saved in the same folder as the scripts.
