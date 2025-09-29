import streamlit as st
import pandas as pd
from datetime import datetime
import time
from scraper import EconomicTimesScraper
from summarizer import NewsSummarizer
from config import APP_TITLE, APP_DESCRIPTION

def init_session_state():
    """Initialize session state variables"""
    if 'articles' not in st.session_state:
        st.session_state.articles = []
    if 'summary_data' not in st.session_state:
        st.session_state.summary_data = None
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None

def setup_page():
    """Setup the Streamlit page configuration"""
    st.set_page_config(
        page_title="Stock Market News Summarizer",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_header():
    """Render the app header"""
    st.title(APP_TITLE)
    st.markdown(APP_DESCRIPTION)
    st.divider()

def render_sidebar():
    """Render the sidebar with controls"""
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key Input
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Enter your Groq API key to use AI summarization"
        )
        
        # Refresh button
        col1, col2 = st.columns(2)
        with col1:
            refresh_clicked = st.button("🔄 Refresh News", use_container_width=True)
        with col2:
            clear_clicked = st.button("🗑️ Clear Cache", use_container_width=True)
        
        # Settings
        st.subheader("⚙️ Settings")
        show_individual_summaries = st.checkbox("Show Individual Article Summaries", value=True)
        max_articles = st.slider("Max Articles to Display", 5, 20, 10)
        
        # Last refresh time
        if st.session_state.last_refresh:
            st.info(f"Last refreshed: {st.session_state.last_refresh}")
        
        return api_key, refresh_clicked, clear_clicked, show_individual_summaries, max_articles

def scrape_news():
    """Scrape news articles"""
    with st.spinner("🔍 Scraping latest market news from Economic Times..."):
        scraper = EconomicTimesScraper()
        articles = scraper.get_market_news()
        
        if articles:
            st.session_state.articles = articles
            st.session_state.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success(f"✅ Found {len(articles)} market news articles!")
        else:
            st.error("❌ No articles found. Please try again later.")
        
        return articles

def generate_summaries(api_key, articles):
    """Generate AI summaries"""
    if not api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar to generate AI summaries.")
        return None
    
    try:
        with st.spinner("🤖 Generating AI-powered summaries..."):
            summarizer = NewsSummarizer(api_key)
            summary_data = summarizer.summarize_articles(articles)
            sentiment_data = summarizer.get_market_sentiment(articles)
            
            # Combine summary and sentiment data
            summary_data['sentiment'] = sentiment_data
            
            st.session_state.summary_data = summary_data
            st.success("✅ AI summaries generated successfully!")
            
        return summary_data
        
    except Exception as e:
        st.error(f"❌ Error generating summaries: {str(e)}")
        return None

def render_summary_section(summary_data):
    """Render the summary section"""
    if not summary_data:
        return
    
    st.header("📊 Market Summary")
    
    # Create columns for summary and sentiment
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Overall Market Summary")
        st.write(summary_data.get('summary', 'No summary available'))
        
        st.subheader("🔍 Key Insights")
        st.write(summary_data.get('key_insights', 'No insights available'))
    
    with col2:
        st.subheader("📈 Market Sentiment")
        sentiment = summary_data.get('sentiment', {})
        
        sentiment_emoji = {
            'Bullish': '🟢',
            'Bearish': '🔴',
            'Neutral': '🟡',
            'Unknown': '⚪'
        }
        
        sentiment_value = sentiment.get('sentiment', 'Unknown')
        confidence = sentiment.get('confidence', 'Unknown')
        
        st.metric(
            "Sentiment", 
            f"{sentiment_emoji.get(sentiment_value, '⚪')} {sentiment_value}",
            delta=f"Confidence: {confidence}"
        )
        
        st.write("**Explanation:**")
        st.write(sentiment.get('explanation', 'No explanation available'))

def render_articles_section(articles, api_key, show_individual_summaries, max_articles):
    """Render the articles section"""
    if not articles:
        return
    
    st.header(f"📰 Latest Market News ({len(articles)} articles)")
    
    # Display articles
    for i, article in enumerate(articles[:max_articles]):
        with st.expander(f"📄 {article['title']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if article.get('summary'):
                    st.write("**Preview:**")
                    st.write(article['summary'][:200] + "..." if len(article['summary']) > 200 else article['summary'])
                
                # Individual AI summary
                if show_individual_summaries and api_key:
                    if st.button(f"🤖 Get AI Summary", key=f"summary_{i}"):
                        try:
                            with st.spinner("Generating summary..."):
                                summarizer = NewsSummarizer(api_key)
                                individual_summary = summarizer.summarize_individual_article(article)
                                st.write("**AI Summary:**")
                                st.info(individual_summary)
                        except Exception as e:
                            st.error(f"Error generating summary: {str(e)}")
            
            with col2:
                if article.get('link'):
                    st.link_button("🔗 Read Full Article", article['link'])
                
                if article.get('timestamp'):
                    st.write(f"**Time:** {article['timestamp']}")
                
                st.write(f"**Scraped:** {article.get('scraped_at', 'Unknown')}")

def render_analytics_section(articles):
    """Render analytics section"""
    if not articles:
        return
    
    st.header("📊 News Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Articles", len(articles))
    
    with col2:
        articles_with_links = sum(1 for a in articles if a.get('link'))
        st.metric("Articles with Links", articles_with_links)
    
    with col3:
        articles_with_summary = sum(1 for a in articles if a.get('summary'))
        st.metric("Articles with Preview", articles_with_summary)
    
    with col4:
        avg_title_length = sum(len(a['title']) for a in articles) // len(articles)
        st.metric("Avg Title Length", f"{avg_title_length} chars")
    
    # Create a simple dataframe for display
    if st.checkbox("📋 Show Articles Table"):
        df_data = []
        for article in articles:
            df_data.append({
                'Title': article['title'][:80] + "..." if len(article['title']) > 80 else article['title'],
                'Has Link': "✅" if article.get('link') else "❌",
                'Has Preview': "✅" if article.get('summary') else "❌",
                'Timestamp': article.get('timestamp', 'N/A')
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

def main():
    """Main application function"""
    setup_page()
    init_session_state()
    render_header()
    
    # Sidebar
    api_key, refresh_clicked, clear_clicked, show_individual_summaries, max_articles = render_sidebar()
    
    # Handle button clicks
    if clear_clicked:
        st.session_state.articles = []
        st.session_state.summary_data = None
        st.session_state.last_refresh = None
        st.rerun()
    
    if refresh_clicked or not st.session_state.articles:
        articles = scrape_news()
    else:
        articles = st.session_state.articles
    
    # Generate summaries if articles are available and API key is provided
    if articles and api_key and not st.session_state.summary_data:
        summary_data = generate_summaries(api_key, articles)
    else:
        summary_data = st.session_state.summary_data
    
    # Render main content
    if articles:
        # Summary section
        if summary_data:
            render_summary_section(summary_data)
            st.divider()
        
        # Articles section
        render_articles_section(articles, api_key, show_individual_summaries, max_articles)
        st.divider()
        
        # Analytics section
        render_analytics_section(articles)
        
    else:
        st.info("👆 Click 'Refresh News' in the sidebar to get started!")
    
    # Footer
    st.divider()
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("**📈 Built with Streamlit & Groq/Llama**")

if __name__ == "__main__":
    main()