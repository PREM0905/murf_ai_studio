# backend/enhanced_news_api.py

import os
import requests
from datetime import datetime

def get_indian_news(query="general"):
    """Get news from India and neighboring countries"""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return get_free_news(query)
    
    try:
        # Try India-specific news first
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'apiKey': api_key,
            'country': 'in',
            'pageSize': 5,
            'q': query if query != "general" else None
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if data.get('status') == 'ok' and data.get('articles'):
            news_items = []
            for article in data['articles'][:3]:
                title = article.get('title', '')
                source = article.get('source', {}).get('name', 'Unknown')
                if title:
                    news_items.append(f"{title} - {source}")
            
            if news_items:
                return f"Latest news from India: " + ". ".join(news_items)
        
        # Fallback to global news
        return get_global_news(query)
        
    except Exception as e:
        return get_free_news(query)

def get_global_news(query="general"):
    """Get global news including specific queries"""
    api_key = os.getenv("NEWS_API_KEY")
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            'apiKey': api_key,
            'q': query,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 5
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if data.get('status') == 'ok' and data.get('articles'):
            news_items = []
            for article in data['articles'][:3]:
                title = article.get('title', '')
                source = article.get('source', {}).get('name', 'Unknown')
                if title and query.lower() in title.lower():
                    news_items.append(f"{title} - {source}")
            
            if news_items:
                return f"News about {query}: " + ". ".join(news_items)
        
        return get_free_news(query)
        
    except Exception as e:
        return get_free_news(query)

def get_free_news(query="general"):
    """Free news sources as fallback"""
    try:
        # Use RSS feeds for free news
        if "bihar" in query.lower() or "election" in query.lower():
            return "For Bihar election results, I recommend checking Times of India, NDTV, or Election Commission of India website for the most current information."
        
        if "india" in query.lower():
            return "For Indian news, I recommend checking Times of India, The Hindu, or NDTV for current updates."
        
        # Generic news response
        return f"For news about {query}, I recommend checking reliable news sources like BBC, Reuters, or local news websites for the most current information."
        
    except Exception as e:
        return "I'm having trouble accessing news right now. Please check reliable news websites for current information."

def enhanced_news_handler(user_query):
    """Enhanced news handling with better coverage"""
    query = user_query.lower().strip()
    
    # Specific query handling
    if "bihar" in query and "election" in query:
        return get_global_news("Bihar election results")
    elif "election" in query:
        return get_global_news("election results India")
    elif "india" in query:
        return get_indian_news("India")
    elif any(country in query for country in ["pakistan", "bangladesh", "nepal", "sri lanka"]):
        country = next(c for c in ["pakistan", "bangladesh", "nepal", "sri lanka"] if c in query)
        return get_global_news(country)
    else:
        return get_indian_news(query)