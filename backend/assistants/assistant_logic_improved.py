# backend/assistant_logic_improved.py

import os
import requests
from datetime import datetime
import json

def get_latest_news(query="general", count=3):
    """Fetch latest news using NewsAPI"""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "News API key not configured. Please add NEWS_API_KEY to your .env file."
    
    try:
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            'apiKey': api_key,
            'country': 'us',
            'pageSize': count,
            'q': query if query != "general" else None
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == 'ok' and data['articles']:
            news_items = []
            for article in data['articles'][:count]:
                title = article['title']
                source = article['source']['name']
                news_items.append(f"{title} - {source}")
            
            return f"Here are the latest news headlines: " + ". ".join(news_items)
        else:
            return "Sorry, I couldn't fetch the latest news right now."
            
    except Exception as e:
        return f"Error fetching news: {str(e)}"

def get_weather(city="New York"):
    """Fetch weather using OpenWeatherMap API"""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Weather API key not configured. Please add WEATHER_API_KEY to your .env file."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            city_name = data['name']
            return f"The weather in {city_name} is {description} with a temperature of {temp} degrees Celsius."
        else:
            return "Sorry, I couldn't fetch the weather information right now."
            
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

def chat_with_openai(user_text):
    """Use OpenAI for general conversation"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file."
    
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful voice assistant. Keep responses concise and conversational."},
                {"role": "user", "content": user_text}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            return "Sorry, I'm having trouble processing that request right now."
            
    except Exception as e:
        return f"Error with AI response: {str(e)}"

def generate_reply(user_text):
    """
    Enhanced assistant logic with dynamic responses
    """
    if not user_text or user_text.strip() == "":
        return "I could not understand. Please repeat."

    text = user_text.lower().strip()

    # ---- BASIC GREETINGS ----
    if any(word in text for word in ["hello", "hi", "hey"]):
        return "Hello! How can I assist you today?"

    # ---- IDENTITY ----
    if "name" in text:
        return "I am Echo, your intelligent voice assistant."

    # ---- TIME ----
    if "time" in text:
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."

    # ---- DATE ----
    if "date" in text or "today" in text:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    # ---- STATUS ----
    if "how are you" in text:
        return "I'm running perfectly and ready to help you!"

    # ---- NEWS ----
    if any(word in text for word in ["news", "headlines", "latest news"]):
        return get_latest_news()

    # ---- WEATHER ----
    if "weather" in text:
        # Try to extract city name
        city = "New York"  # default
        if " in " in text:
            parts = text.split(" in ")
            if len(parts) > 1:
                city = parts[1].strip()
        return get_weather(city)

    # ---- MATH ----
    if any(word in text for word in ["calculate", "plus", "minus", "multiply", "divide", "math"]):
        try:
            # Simple math evaluation (be careful with eval in production)
            import re
            math_expr = re.findall(r'[\d+\-*/\s()]+', text)
            if math_expr:
                # Only allow safe characters
                expr = ''.join(math_expr).strip()
                if re.match(r'^[\d+\-*/\s().]+$', expr):
                    result = eval(expr)
                    return f"The answer is {result}."
        except:
            pass
        return "I can help with basic math. Try asking something like 'what is 2 plus 2?'"

    # ---- JOKES ----
    if "joke" in text:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!"
        ]
        import random
        return random.choice(jokes)

    # ---- CAPABILITIES ----
    if any(word in text for word in ["help", "what can you do", "capabilities"]):
        return "I can help you with time, date, weather, latest news, basic math, jokes, and general conversation. What would you like to know?"

    # ---- DYNAMIC AI RESPONSE ----
    # For anything else, try to use OpenAI for intelligent responses
    return chat_with_openai(user_text)