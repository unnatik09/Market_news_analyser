import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import List, Dict, Optional
from config import ECONOMIC_TIMES_MARKET_URL, REQUEST_HEADERS

class EconomicTimesScraper:
    """Scraper for Economic Times market section"""
    
    def __init__(self):
        self.base_url = ECONOMIC_TIMES_MARKET_URL
        self.headers = REQUEST_HEADERS
        
    def get_market_news(self) -> List[Dict[str, str]]:
        """
        Scrape market news articles from Economic Times
        
        Returns:
            List of dictionaries containing article data
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Find news articles - ET uses various selectors for news items
            news_containers = soup.find_all(['div', 'article'], class_=re.compile(r'story|article|news'))
            
            for container in news_containers[:20]:  # Limit to 20 articles
                article_data = self._extract_article_data(container)
                if article_data and self._is_relevant_article(article_data['title']):
                    articles.append(article_data)
            
            # If no articles found with the above method, try alternative selectors
            if not articles:
                articles = self._fallback_scraping(soup)
            
            return articles[:15]  # Return top 15 articles
            
        except Exception as e:
            print(f"Error scraping Economic Times: {str(e)}")
            return []
    
    def _extract_article_data(self, container) -> Optional[Dict[str, str]]:
        """Extract article data from a container element"""
        try:
            # Try to find title
            title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'a'])
            if not title_elem:
                return None
                
            title = title_elem.get_text(strip=True)
            if len(title) < 10:  # Filter out very short titles
                return None
            
            # Try to find link
            link_elem = title_elem if title_elem.name == 'a' else container.find('a')
            link = ""
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('/'):
                    link = f"https://economictimes.indiatimes.com{href}"
                elif href.startswith('http'):
                    link = href
            
            # Try to find summary/description
            summary_elem = container.find(['p', 'div'], class_=re.compile(r'summary|desc|content'))
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # Try to find timestamp
            time_elem = container.find(['time', 'span'], class_=re.compile(r'time|date'))
            timestamp = time_elem.get_text(strip=True) if time_elem else ""
            
            return {
                'title': title,
                'summary': summary,
                'link': link,
                'timestamp': timestamp,
                'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"Error extracting article data: {str(e)}")
            return None
    
    def _fallback_scraping(self, soup) -> List[Dict[str, str]]:
        """Fallback method to scrape articles if primary method fails"""
        articles = []
        
        # Try to find any links that might be news articles
        links = soup.find_all('a', href=True)
        
        for link in links[:30]:  # Check first 30 links
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # Filter for likely news article links
            if (len(title) > 20 and 
                any(keyword in title.lower() for keyword in 
                    ['stock', 'market', 'share', 'sensex', 'nifty', 'rupee', 'trading', 'investment'])):
                
                full_link = href if href.startswith('http') else f"https://economictimes.indiatimes.com{href}"
                
                articles.append({
                    'title': title,
                    'summary': "",
                    'link': full_link,
                    'timestamp': "",
                    'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return articles
    
    def _is_relevant_article(self, title: str) -> bool:
        """Check if article is relevant to stock/market news"""
        market_keywords = [
            'stock', 'share', 'market', 'sensex', 'nifty', 'bse', 'nse',
            'trading', 'investment', 'equity', 'rupee', 'earnings', 'ipo',
            'mutual fund', 'portfolio', 'commodity', 'gold', 'silver'
        ]
        
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in market_keywords)
    
    def get_article_content(self, url: str) -> str:
        """
        Fetch full content of an article
        
        Args:
            url: Article URL
            
        Returns:
            Article content text
        """
        try:
            if not url:
                return ""
                
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find the main content
            content_selectors = [
                'div.article-content',
                'div.story-content',
                'div.news-content',
                'article',
                'div[data-module="ArticleContent"]'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script and style elements
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    content = content_elem.get_text(strip=True)
                    break
            
            # Fallback: get all paragraph text
            if not content:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            return content[:2000]  # Limit content length
            
        except Exception as e:
            print(f"Error fetching article content: {str(e)}")
            return ""