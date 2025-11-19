import sys
import os
import requests
import re
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def get_weather(city="Mumbai"):
    """Get weather using simple API"""
    try:
        # Use a simple weather API
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            weather = response.text.strip()
            if weather and "Unknown" not in weather:
                return f"Weather in {city}: {weather}"
            else:
                return f"Could not find weather for {city}"
        else:
            return f"Weather service unavailable"
            
    except Exception as e:
        return f"Weather error: Unable to fetch data"

def get_news(topic="general"):
    """Get news using NewsAPI"""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "News API key not configured"
    
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'apiKey': api_key,
            'country': 'us',
            'pageSize': 3,
            'q': topic if topic != "general" else None
        }
        
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data['status'] == 'ok' and data['articles']:
            article = data['articles'][0]
            title = article['title']
            source = article['source']['name']
            return f"Latest news: {title} (Source: {source})"
        else:
            return "Could not fetch news"
            
    except Exception as e:
        return "News service unavailable"

def generate_reply(user_text):
    """Main assistant logic"""
    if not user_text or user_text.strip() == "":
        return "I could not understand. Please repeat."

    text = user_text.lower().strip()
    
    # Greetings
    if any(word in text for word in ["hello", "hi", "hey"]):
        return "Hello! I'm STUDIO, your intelligent assistant. I can help with weather, news, and general queries."
    
    # Time and date
    if "time" in text:
        return f"Current time: {datetime.now().strftime('%I:%M %p')}"
    if "date" in text or "today" in text:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
    
    # Weather
    if "weather" in text:
        city_patterns = [
            r"weather in ([a-zA-Z\s]+)",
            r"weather for ([a-zA-Z\s]+)",
            r"weather of ([a-zA-Z\s]+)"
        ]
        
        city = None
        for pattern in city_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                break
        
        if not city:
            city = "Mumbai"
        
        return get_weather(city)
    
    # News
    if "news" in text:
        topic_patterns = [
            r"news about ([a-zA-Z\s]+)",
            r"news on ([a-zA-Z\s]+)",
            r"([a-zA-Z\s]+) news"
        ]
        
        topic = "general"
        for pattern in topic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                break
        
        return get_news(topic)
    
    # Navigation
    if any(word in text for word in ["navigate", "directions", "route"]):
        dest_patterns = [
            r"navigate to ([a-zA-Z\s,]+)",
            r"directions to ([a-zA-Z\s,]+)",
            r"route to ([a-zA-Z\s,]+)"
        ]
        
        destination = None
        for pattern in dest_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                destination = match.group(1).strip()
                break
        
        if destination:
            maps_url = f"https://www.google.com/maps/search/{destination.replace(' ', '+')}"
            return f"Navigation to {destination}:\n1. Opening Google Maps...\n2. Finding route...\n3. Ready!\n\nGoogle Maps: {maps_url}"
        else:
            return "Please specify destination. Example: 'Navigate to Mumbai'"
    
    # Capabilities
    if "help" in text or "what can you do" in text:
        return "I can help with:\n• Weather reports\n• Latest news\n• Navigation\n• Time and date\n• General questions"
    
    # Default
    return f"I understand: '{user_text}'. I can help with weather, news, navigation, and general queries. What would you like to know?"