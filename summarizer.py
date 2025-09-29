from groq import Groq
from typing import List, Dict
from config import GROQ_API_KEY, LLAMA_MODEL, BACKUP_MODELS, MAX_TOKENS, TEMPERATURE

class NewsSummarizer:
    """AI-powered news summarizer using Groq/Llama"""
    
    def __init__(self, api_key: str = None):
        """Initialize the summarizer with Groq API key"""
        self.api_key = api_key or GROQ_API_KEY
        if not self.api_key:
            raise ValueError("Groq API key is required. Please set GROQ_API_KEY in your .env file.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = LLAMA_MODEL
        self.backup_models = BACKUP_MODELS
        
    def _make_api_call(self, messages: List[Dict], max_tokens: int = MAX_TOKENS):
        """Make API call with fallback model support"""
        models_to_try = [self.model] + self.backup_models
        
        for model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=TEMPERATURE
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if "decommissioned" in str(e) or "model_decommissioned" in str(e):
                    print(f"Model {model} is decommissioned, trying next model...")
                    continue
                else:
                    print(f"Error with model {model}: {str(e)}")
                    if model == models_to_try[-1]:  # Last model
                        raise e
                    continue
        
        raise Exception("All models failed or are decommissioned")
        
    def summarize_articles(self, articles: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Generate comprehensive summary of multiple news articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Dictionary containing overall summary and key insights
        """
        if not articles:
            return {"summary": "No articles found to summarize.", "key_points": ""}
        
        # Prepare articles text for summarization
        articles_text = self._prepare_articles_text(articles)
        
        # Generate overall market summary
        overall_summary = self._generate_overall_summary(articles_text)
        
        # Extract key market insights
        key_insights = self._extract_key_insights(articles_text)
        
        return {
            "summary": overall_summary,
            "key_insights": key_insights,
            "articles_count": len(articles)
        }
    
    def summarize_individual_article(self, article: Dict[str, str]) -> str:
        """
        Summarize a single article
        
        Args:
            article: Article dictionary
            
        Returns:
            Article summary
        """
        if not article.get('title'):
            return "Unable to summarize article."
        
        article_text = f"Title: {article['title']}\n"
        if article.get('summary'):
            article_text += f"Content: {article['summary']}\n"
        
        prompt = f"""
        Please provide a concise summary of this stock market news article in 2-3 sentences:
        
        {article_text}
        
        Focus on:
        - Key market movements or events
        - Impact on stocks or sectors
        - Important numbers or percentages mentioned
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are a financial news analyst. Provide clear, concise summaries of stock market news."},
                {"role": "user", "content": prompt}
            ]
            
            return self._make_api_call(messages, max_tokens=200)
            
        except Exception as e:
            print(f"Error summarizing individual article: {str(e)}")
            return "Summary unavailable due to an error."
    
    def _prepare_articles_text(self, articles: List[Dict[str, str]]) -> str:
        """Prepare articles text for summarization"""
        articles_text = ""
        for i, article in enumerate(articles[:10], 1):  # Limit to 10 articles for token management
            articles_text += f"\nArticle {i}:\nTitle: {article['title']}\n"
            if article.get('summary'):
                articles_text += f"Content: {article['summary'][:300]}...\n"
            articles_text += "---\n"
        
        return articles_text
    
    def _generate_overall_summary(self, articles_text: str) -> str:
        """Generate overall market summary"""
        prompt = f"""
        Based on today's stock market news articles below, provide a comprehensive summary of the current market situation in 4-5 sentences.
        
        Focus on:
        - Overall market sentiment and direction
        - Major stock movements or sector performances
        - Key economic factors affecting the market
        - Notable company news or earnings
        
        News Articles:
        {articles_text}
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert financial analyst providing market summaries for Indian stock markets."},
                {"role": "user", "content": prompt}
            ]
            
            return self._make_api_call(messages, max_tokens=MAX_TOKENS)
            
        except Exception as e:
            print(f"Error generating overall summary: {str(e)}")
            return "Unable to generate market summary due to an error."
    
    def _extract_key_insights(self, articles_text: str) -> str:
        """Extract key market insights"""
        prompt = f"""
        From the following stock market news articles, extract the top 5 key insights or takeaways that investors should know about today's market:
        
        {articles_text}
        
        Format as numbered points (1., 2., 3., etc.) and focus on actionable insights, major movements, and important developments.
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are a financial advisor extracting key investment insights from market news."},
                {"role": "user", "content": prompt}
            ]
            
            return self._make_api_call(messages, max_tokens=500)
            
        except Exception as e:
            print(f"Error extracting key insights: {str(e)}")
            return "Unable to extract key insights due to an error."
    
    def get_market_sentiment(self, articles: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Analyze overall market sentiment
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Dictionary with sentiment analysis
        """
        if not articles:
            return {"sentiment": "Neutral", "confidence": "Low", "explanation": "No articles to analyze"}
        
        articles_text = self._prepare_articles_text(articles)
        
        prompt = f"""
        Based on the following stock market news articles, analyze the overall market sentiment:
        
        {articles_text}
        
        Provide:
        1. Overall sentiment: Bullish, Bearish, or Neutral
        2. Confidence level: High, Medium, or Low
        3. Brief explanation (1-2 sentences)
        
        Format your response as:
        Sentiment: [Bullish/Bearish/Neutral]
        Confidence: [High/Medium/Low]
        Explanation: [Your explanation here]
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are a market sentiment analyst. Analyze news to determine market sentiment."},
                {"role": "user", "content": prompt}
            ]
            
            content = self._make_api_call(messages, max_tokens=200)
            
            # Parse the response
            sentiment_data = {"sentiment": "Neutral", "confidence": "Medium", "explanation": content}
            
            if "Sentiment:" in content:
                lines = content.split('\n')
                for line in lines:
                    if line.startswith("Sentiment:"):
                        sentiment_data["sentiment"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Confidence:"):
                        sentiment_data["confidence"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Explanation:"):
                        sentiment_data["explanation"] = line.split(":", 1)[1].strip()
            
            return sentiment_data
            
        except Exception as e:
            print(f"Error analyzing market sentiment: {str(e)}")
            return {
                "sentiment": "Unknown", 
                "confidence": "Low", 
                "explanation": "Unable to analyze sentiment due to an error."
            }