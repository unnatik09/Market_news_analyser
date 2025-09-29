import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Scraping Configuration
ECONOMIC_TIMES_MARKET_URL = "https://economictimes.indiatimes.com/markets"
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# LLM Configuration
LLAMA_MODEL = "llama-3.1-8b-instant"  # Primary model
BACKUP_MODELS = [
    "llama3-8b-8192",
    "llama3-70b-8192", 
    "mixtral-8x7b-32768",
    "gemma-7b-it"
]  # Backup models to try if primary fails
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# App Configuration
APP_TITLE = "📈 Stock Market News Summarizer"
APP_DESCRIPTION = "Get AI-powered summaries of today's market news from The Economic Times"