import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scrapers.amazon_scraper import scrape_amazon
from scrapers.flipkart_scraper import scrape_flipkart
from scrapers.reddit_scraper import scrape_reddit
from scrapers.youtube_scraper import scrape_youtube
from analysis.sentiment_analyzer import analyze_sentiment
from analysis.keyword_extractor import extract_keywords
from analysis.competitor_strategy import generate_strategy

st.set_page_config(page_title="Laptop Market Intelligence", layout="wide")

st.title("🖥️ Laptop Market Intelligence Dashboard")

# Sidebar
with st.sidebar:
    st.header("Data Sources")
    search_query = st.text_input("Search Query", "gaming laptop")
    sources = st.multiselect("Select Sources", 
                            ["Amazon", "Flipkart", "Reddit", "YouTube"],
                            default=["Amazon", "Flipkart"])
    
    if st.button("Fetch Data"):
        with st.spinner("Scraping data..."):
            all_products = []
            all_discussions = []
            
            if "Amazon" in sources:
                amazon_data = scrape_amazon(search_query)
                all_products.append(amazon_data)
            
            if "Flipkart" in sources:
                flipkart_data = scrape_flipkart(search_query)
                all_products.append(flipkart_data)
            
            if "Reddit" in sources:
                reddit_data = scrape_reddit(search_query)
                all_discussions.append(reddit_data)
            
            if "YouTube" in sources:
                youtube_data = scrape_youtube(search_query)
                all_discussions.append(youtube_data)
            
            # Combine data
            st.session_state.products_df = pd.concat(all_products, ignore_index=True) if all_products else pd.DataFrame()
            st.session_state.discussions_df = pd.concat(all_discussions, ignore_index=True) if all_discussions else pd.DataFrame()
            
            # Analyze sentiment
            if not st.session_state.discussions_df.empty:
                texts = st.session_state.discussions_df['text'].fillna('') + ' ' + st.session_state.discussions_df['title'].fillna('')
                st.session_state.sentiment_df = analyze_sentiment(texts)
            else:
                st.session_state.sentiment_df = pd.DataFrame()
            
            # Extract keywords
            all_text = []
            if not st.session_state.products_df.empty:
                all_text.extend(st.session_state.products_df['title'].tolist())
            if not st.session_state.discussions_df.empty:
                all_text.extend(st.session_state.discussions_df['title'].tolist())
            
            if all_text:
                st.session_state.keywords_df = extract_keywords(all_text)
            else:
                st.session_state.keywords_df = pd.DataFrame()
            
            # Generate strategy
            st.session_state.strategy_df = generate_strategy(
                st.session_state.keywords_df,
                st.session_state.sentiment_df,
                st.session_state.products_df
            )
            
            st.session_state.data_fetched = True
            st.session_state.search_query = search_query
            st.success("Data fetched successfully!")

# Main content
if st.session_state.get('data_fetched'):
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💬 Sentiment", "🔑 Keywords", "🎯 Strategy"])
    
    with tab1:
        st.header("Market Overview")
        
        products_df = st.session_state.get('products_df', pd.DataFrame())
        discussions_df = st.session_state.get('discussions_df', pd.DataFrame())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Products Analyzed", len(products_df))
        with col2:
            st.metric("Discussions Found", len(discussions_df))
        with col3:
            if not products_df.empty:
                avg_rating = products_df['rating'].apply(lambda x: float(str(x).split()[0]) if str(x) != 'N/A' else 0).mean()
                st.metric("Avg Rating", f"{avg_rating:.1f}")
            else:
                st.metric("Avg Rating", "N/A")
        
        if not products_df.empty:
            st.subheader("Products by Source")
            source_counts = products_df['source'].value_counts()
            fig = px.pie(values=source_counts.values, names=source_counts.index, title="Data Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Product Data")
            st.dataframe(products_df, use_container_width=True)
    
    with tab2:
        st.header("Sentiment Analysis")
        
        sentiment_df = st.session_state.get('sentiment_df', pd.DataFrame())
        
        if not sentiment_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                sentiment_counts = sentiment_df['label'].value_counts()
                fig = px.bar(x=sentiment_counts.index, y=sentiment_counts.values,
                           labels={'x': 'Sentiment', 'y': 'Count'},
                           title="Sentiment Distribution",
                           color=sentiment_counts.index,
                           color_discrete_map={'positive': 'green', 'neutral': 'gray', 'negative': 'red'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                avg_polarity = sentiment_df['polarity'].mean()
                st.metric("Average Polarity", f"{avg_polarity:.2f}")
                st.metric("Positive %", f"{(sentiment_df['label'] == 'positive').sum() / len(sentiment_df) * 100:.1f}%")
                st.metric("Negative %", f"{(sentiment_df['label'] == 'negative').sum() / len(sentiment_df) * 100:.1f}%")
            
            st.subheader("Polarity Distribution")
            fig = px.histogram(sentiment_df, x='polarity', nbins=30, title="Sentiment Polarity Histogram")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sentiment data available. Try including Reddit or YouTube sources.")
    
    with tab3:
        st.header("Keyword Extraction")
        
        keywords_df = st.session_state.get('keywords_df', pd.DataFrame())
        
        if not keywords_df.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(keywords_df.head(15), x='score', y='keyword', orientation='h',
                           title="Top Keywords by TF-IDF Score")
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Top Keywords")
                st.dataframe(keywords_df.head(20), use_container_width=True)
        else:
            st.info("No keywords extracted. Fetch data to see results.")
    
    with tab4:
        st.header("Competitor Strategy")
        
        strategy_df = st.session_state.get('strategy_df', pd.DataFrame())
        
        if not strategy_df.empty:
            for idx, row in strategy_df.iterrows():
                with st.expander(f"📌 {row['category']}", expanded=True):
                    st.write(f"**Insight:** {row['insight']}")
                    st.write(f"**Recommended Action:** {row['action']}")
        else:
            st.info("No strategy generated yet.")
else:
    st.info("👈 Configure settings and click 'Fetch Data' to begin analysis")
