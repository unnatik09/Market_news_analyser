# 📈 Stock Market News Summarizer

AI-powered Streamlit app that scrapes Economic Times market news and generates intelligent summaries using Llama via Groq API.

## 🚀 Quick Start

1. **Setup:**
   ```bash
   python setup.py
   ```

2. **Add your Groq API key to `.env`:**
   ```
   GROQ_API_KEY=your_actual_groq_api_key
   ```

3. **Run:**
   ```bash
   source venv/bin/activate
   streamlit run app.py
   ```

## ✨ Features

- 📰 Auto-scrapes Economic Times market section
- 🤖 AI summaries with smart model fallback
- 📊 Market sentiment analysis  
- 🎨 Clean Streamlit interface
- 📱 Real-time news refresh

## 🔑 Get API Key

Get your free Groq API key: [console.groq.com](https://console.groq.com/)

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Scraping:** BeautifulSoup + Requests  
- **AI:** Groq/Llama models
- **Data:** Pandas.