# 🚀 Quick Start - Dashboard

## Launch Dashboard in 3 Steps

### Step 1: Double-Click
```
run_dashboard.bat
```

### Step 2: Wait
Dashboard will install packages and start automatically

### Step 3: Browse
Dashboard opens at: **http://localhost:8501**

---

## Dashboard Sections

### 🏠 Home
Overview and key metrics

### 📈 Market Overview
- Brand Price Comparison
- Brand Rating Comparison
- Market Leaders

### 😊 Sentiment Analysis
- Sentiment distribution by brand
- Positive/Negative/Neutral breakdown

### ⚠️ Customer Complaints
- Top 10 customer issues
- Hardware vs Performance problems

### 💬 Social Media Insights
- Trending topics from Reddit + YouTube
- Most praised features

### 🎯 Competitive Strategy
- AI-generated strategies for each brand
- Select brand to view recommendations

---

## Key Features

✅ Interactive charts
✅ Real-time filtering
✅ Brand comparison
✅ Trend analysis
✅ Strategic recommendations

---

## Troubleshooting

**Dashboard won't start?**
```bash
pip install streamlit plotly pandas
streamlit run dashboard.py
```

**Port already in use?**
```bash
streamlit run dashboard.py --server.port 8502
```

**No data showing?**
- Run all analysis steps first (Step 1-7)
- Check CSV files exist

---

## That's It!

Your interactive dashboard is ready to explore all market insights visually.

**Enjoy! 🎉**
