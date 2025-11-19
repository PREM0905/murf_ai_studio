# backend/advanced_assistant.py

import os
import requests
from datetime import datetime
import json
import base64
import hashlib

def identify_song(lyrics_snippet):
    """Identify song from lyrics using free services"""
    from free_music import identify_song_free
    
    # Try Genius API first if available
    api_key = os.getenv("GENIUS_API_KEY")
    if api_key:
        try:
            url = "https://api.genius.com/search"
            headers = {"Authorization": f"Bearer {api_key}"}
            params = {"q": lyrics_snippet}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()
            
            if data['response']['hits']:
                song = data['response']['hits'][0]['result']
                title = song['title']
                artist = song['primary_artist']['name']
                return f"That sounds like '{title}' by {artist}."
        except:
            pass
    
    # Fallback to free services
    return identify_song_free(lyrics_snippet)

def get_latest_news(query="general", count=3):
    """Fetch latest news using NewsAPI"""
    api_key = os.getenv("NEWS_API_KEY")  # ADD THIS TO .env FILE
    if not api_key:
        return "I can provide news updates, but need NEWS_API_KEY configured in .env file."
    
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
                news_items.append(f"{title} from {source}")
            
            return f"Here are the latest headlines: " + ". ".join(news_items)
        else:
            return "Sorry, I couldn't fetch the latest news right now."
    except Exception as e:
        return "I'm having trouble accessing the news right now."

def get_weather(city="New York"):
    """Fetch weather using OpenWeatherMap API"""
    api_key = os.getenv("WEATHER_API_KEY")  # ADD THIS TO .env FILE
    if not api_key:
        return "I can provide weather updates, but need WEATHER_API_KEY configured in .env file."
    
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
        return "I'm having trouble accessing weather data right now."

def translate_text(text, target_lang="es"):
    """Translate text using free translation services"""
    from free_translation import translate_text_free
    return translate_text_free(text, target_lang)

def get_stock_price(symbol):
    """Get stock price using Alpha Vantage API"""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return "I can check stock prices, but need ALPHA_VANTAGE_API_KEY configured."
    
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Global Quote' in data:
            quote = data['Global Quote']
            price = quote['05. price']
            change = quote['09. change']
            return f"{symbol} is trading at ${price}, change: {change}"
        else:
            return f"Sorry, I couldn't find stock data for {symbol}."
    except Exception as e:
        return "I'm having trouble accessing stock data right now."

def search_wikipedia(query):
    """Search Wikipedia"""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'extract' in data:
            return data['extract'][:300] + "..."
        else:
            return f"I couldn't find information about {query} on Wikipedia."
    except Exception as e:
        return "I'm having trouble accessing Wikipedia right now."

def get_recipe(dish):
    """Get recipe using Spoonacular API"""
    api_key = os.getenv("SPOONACULAR_API_KEY")
    if not api_key:
        return "I can find recipes, but need SPOONACULAR_API_KEY configured."
    
    try:
        url = f"https://api.spoonacular.com/recipes/complexSearch"
        params = {
            'apiKey': api_key,
            'query': dish,
            'number': 1,
            'addRecipeInformation': True
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['results']:
            recipe = data['results'][0]
            title = recipe['title']
            time = recipe.get('readyInMinutes', 'Unknown')
            return f"Recipe for {title}: Ready in {time} minutes. Check the full recipe online."
        else:
            return f"I couldn't find a recipe for {dish}."
    except Exception as e:
        return "I'm having trouble finding recipes right now."

def chat_with_openai(user_text):
    """Use OpenAI for general conversation with enhanced prompts"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return f"I understand you're asking about '{user_text}'. For advanced AI responses, add OPENAI_API_KEY to .env file."
    
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are STUDIO, an advanced voice assistant. Be helpful, concise, and conversational. Handle any request intelligently."},
                {"role": "user", "content": user_text}
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            return "Sorry, I'm having trouble processing that request right now."
    except Exception as e:
        return "I'm having some technical difficulties. Please try again later."

def generate_reply(user_text):
    """
    Advanced assistant logic - handles ANY request intelligently
    """
    if not user_text or user_text.strip() == "":
        return "I could not understand. Please repeat."

    text = user_text.lower().strip()

    # ---- SONG IDENTIFICATION ----
    if any(phrase in text for phrase in ["song goes", "lyrics", "identify song", "what song", "song that goes"]):
        from enhanced_song_api import enhanced_song_handler
        return enhanced_song_handler(text)

    # ---- BASIC GREETINGS ----
    if any(word in text for word in ["hello", "hi", "hey", "good morning", "good evening"]):
        return "Hello! I'm STUDIO, your advanced AI assistant. I can help with songs, news, weather, translations, stocks, recipes, and much more!"

    # ---- IDENTITY ----
    if "name" in text or "who are you" in text:
        return "I am STUDIO, your advanced AI assistant. I can identify songs, get news, weather, translate languages, check stocks, find recipes, and answer any question!"

    # ---- MATH ----
    math_keywords = ["calculate", "plus", "minus", "multiply", "divide", "times", "divided"]
    math_operators = ["+", "-", "*", "/", "plus", "minus", "times", "divided"]
    
    has_math_keyword = any(word in text for word in math_keywords)
    has_numbers = any(char.isdigit() for char in text)
    has_math_operator = any(op in text for op in math_operators)
    
    if has_math_keyword or (has_numbers and has_math_operator):
        try:
            import re
            if any(op in text for op in math_operators):
                math_text = text.replace("plus", "+").replace("minus", "-")
                math_text = math_text.replace("times", "*").replace("multiply", "*")
                math_text = math_text.replace("divided by", "/").replace("divide", "/")
                
                math_expr = re.findall(r'[\d+\-*/\s()]+', math_text)
                if math_expr:
                    expr = ''.join(math_expr).strip()
                    if re.match(r'^[\d+\-*/\s().]+$', expr) and len(expr) > 0:
                        result = eval(expr)
                        return f"The answer is {result}."
        except:
            pass
        return "I can help with math calculations. Try asking 'what is 2 plus 2?'"

    # ---- TIME & DATE ----
    if "time" in text and not has_numbers:
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."
    
    if "date" in text or "today" in text:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    # ---- NEWS ----
    if any(word in text for word in ["news", "headlines", "latest news", "election", "bihar"]):
        from enhanced_news_api import enhanced_news_handler
        return enhanced_news_handler(text)

    # ---- WEATHER ----
    if "weather" in text:
        city = "New York"
        if " in " in text:
            parts = text.split(" in ")
            if len(parts) > 1:
                city = parts[1].strip()
        return get_weather(city)

    # ---- MAPS & NAVIGATION ----
    if any(word in text for word in ["directions", "route", "how to get", "nearby", "near me", "find", "traffic"]):
        from maps_navigation import comprehensive_navigation
        return comprehensive_navigation(text)

    # ---- TRANSLATION ----
    if "translate" in text:
        # Extract text to translate
        if " to " in text:
            parts = text.split(" to ")
            if len(parts) > 1:
                target_lang = parts[1].strip()[:2]  # Get language code
                text_to_translate = parts[0].replace("translate", "").strip()
                return translate_text(text_to_translate, target_lang)
        return "I can translate text. Try: 'translate hello to spanish'"

    # ---- STOCKS ----
    if any(word in text for word in ["stock", "share price", "stock price"]):
        # Extract stock symbol
        words = text.split()
        for i, word in enumerate(words):
            if word in ["stock", "price"] and i > 0:
                symbol = words[i-1].upper()
                return get_stock_price(symbol)
        return "I can check stock prices. Try: 'AAPL stock price'"

    # ---- RECIPES ----
    if any(word in text for word in ["recipe", "cook", "how to make"]):
        dish = text.replace("recipe for", "").replace("how to make", "").replace("cook", "").strip()
        return get_recipe(dish)

    # ---- WIKIPEDIA SEARCH ----
    if "wikipedia" in text or "tell me about" in text:
        query = text.replace("wikipedia", "").replace("tell me about", "").strip()
        return search_wikipedia(query)

    # ---- JOKES ----
    if "joke" in text:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!"
        ]
        import random
        return random.choice(jokes)

    # ---- STATUS ----
    if "how are you" in text:
        return "I'm running perfectly and ready to help with anything! Songs, news, weather, translations, stocks, recipes - you name it!"

    # ---- CAPABILITIES ----
    if any(word in text for word in ["help", "what can you do", "capabilities"]):
        return "I can identify songs from lyrics, get news & weather, provide directions & maps, find nearby places, translate languages, check stock prices, find recipes, search Wikipedia, do math, tell jokes, and answer any question using AI!"

    # ---- DYNAMIC AI RESPONSE FOR EVERYTHING ELSE ----
    return chat_with_openai(user_text)