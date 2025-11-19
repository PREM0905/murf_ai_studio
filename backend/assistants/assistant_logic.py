# backend/assistant_logic.py

import sys
import os
import requests
from datetime import datetime
import json
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities.response_cache import response_cache

# Load environment first
load_dotenv()

# --- Add GPT Client + Tools ---
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from tools.weather import get_weather
from tools.fetch_news import get_latest_news
# Import maps functions with fallback
try:
    from integrations.navigation.maps_navigation import get_directions, find_nearby, search_location
    def check_traffic(location):
        return {"traffic": "moderate", "location": location}
except ImportError:
    def get_directions(origin, destination):
        return {"error": "Maps service unavailable"}
    def find_nearby(location, place_type):
        return {"error": "Maps service unavailable"}
    def search_location(query):
        return {"error": "Maps service unavailable"}
    def check_traffic(location):
        return {"error": "Traffic service unavailable"}


def get_latest_news(query="general", count=3):
    """Fetch latest news using NewsAPI"""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "I can provide news updates, but I need a News API key to be configured. For now, I can help with other things like time, weather, or general questions."
    
    try:
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            'apiKey': api_key,
            'country': 'us',
            'pageSize': count,
            'q': query if query != "general" else None
        }
        
        response = requests.get(url, params=params, timeout=3)
        data = response.json()
        
        if data['status'] == 'ok' and data['articles']:
            # Return only first headline for speed
            article = data['articles'][0]
            title = article['title']
            source = article['source']['name']
            return f"Latest: {title} from {source}"
        else:
            return "Sorry, I couldn't fetch the latest news right now."
            
    except Exception as e:
        return "I'm having trouble accessing the news right now. Please try again later."

def get_weather(city="New York"):
    """Fetch weather using free weather service"""
    try:
        # Use wttr.in free weather service without emojis
        url = f"https://wttr.in/{city}?format=%l:+%C+%t+humidity+%h+wind+%w"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            weather_data = response.text.strip()
            if "Unknown location" not in weather_data and weather_data:
                # Clean up the data
                weather_data = weather_data.replace(":", " -")
                return f"Weather: {weather_data}"
            else:
                return f"Could not find weather data for {city}"
        else:
            return f"Weather service unavailable for {city}"
            
    except Exception as e:
        print(f"Weather API Error: {e}")
        return f"Weather service error for {city}"

def chat_with_openai(user_text):
    """Use OpenAI for general conversation"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are STUDIO, an intelligent assistant."},
                {"role": "user", "content": user_text}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get weather for a city",
                        "parameters": {
                            "type": "object",
                            "properties": {"city": {"type": "string"}},
                            "required": ["city"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_latest_news",
                        "description": "Get news headlines",
                        "parameters": {
                            "type": "object",
                            "properties": {"query": {"type": "string"}},
                            "required": ["query"]
                        }
                    }
                }
            ],
            tool_choice="auto"
        )

        message = response.choices[0].message
        
        # --- If GPT replies normally ---
        if not message.tool_calls:
            return message.content

        # --- TOOL CALL ---
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        if tool_name == "get_weather":
            result = get_weather(**tool_args)
        elif tool_name == "get_latest_news":
            result = get_latest_news(**tool_args)
        # Remove unsupported navigation tools for now
        else:
            result = {"error": f"Unknown tool {tool_name}"}

        # --- Second GPT turn (final answer) ---
        final = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": user_text},
                message,
                {"role": "tool", "tool_call_id": tool_call.id, "name": tool_name, "content": str(result)}
            ]
        )

        return final.choices[0].message.content

    except Exception as e:
        return "I'm having some trouble getting live information right now."

def generate_reply(user_text):
    """
    Enhanced assistant logic with dynamic responses
    """
    if not user_text or user_text.strip() == "":
        return "I could not understand. Please repeat."

    text = user_text.lower().strip()
    
    # Check cache first for faster responses
    cache_key = text[:50]  # Use first 50 chars as key
    cached_response = response_cache.get(cache_key)
    if cached_response:
        return cached_response
    
    # Fast local responses for common queries
    quick_responses = {
        "how are you": "I'm running perfectly!",
        "what's your name": "I'm STUDIO, your voice assistant.",
        "who are you": "I'm STUDIO, your AI assistant.",
        "thank you": "You're welcome!",
        "thanks": "You're welcome!",
        "good morning": "Good morning! How can I help?",
        "good evening": "Good evening! What can I do for you?",
        "good night": "Good night! Sleep well!",
        "bye": "Goodbye! Have a great day!",
        "goodbye": "Goodbye! Take care!"
    }
    
    for phrase, response in quick_responses.items():
        if phrase in text:
            return response

    # ---- BASIC GREETINGS ----
    if any(word in text for word in ["hello", "hi", "hey"]):
        return "Hello! How can I assist you today?"

    # ---- IDENTITY ----
    if "name" in text:
        return "I am STUDIO, your intelligent voice assistant."

    # ---- MATH ---- (Check first to avoid conflicts)
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
        return "I can help with basic math. Try asking something like 'what is 2 plus 2?'"

    # ---- TIME ----
    if "time" in text and not has_numbers:
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."

    # ---- DATE ----
    if "date" in text or "today" in text:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."



    # ---- NEWS handled by GPT tools ----
    if "news" in text or "headline" in text:
        return chat_with_openai(user_text)

    # ---- WEATHER handled directly ----
    if "weather" in text:
        import re
        # Extract city from weather request
        city_patterns = [
            r"weather in ([a-zA-Z\s]+)",
            r"weather for ([a-zA-Z\s]+)",
            r"weather of ([a-zA-Z\s]+)",
            r"([a-zA-Z\s]+) weather"
        ]
        
        city = None
        for pattern in city_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                break
        
        if not city:
            city = "Mumbai"  # Default city
        
        return get_weather(city)

    # ---- MAPS/NAVIGATION ----
    if any(w in text for w in ["direction", "route", "navigate", "nearby", "traffic"]):
        # Extract destination
        import re
        patterns = [
            r"navigate to ([a-zA-Z\s,]+)",
            r"directions to ([a-zA-Z\s,]+)",
            r"route to ([a-zA-Z\s,]+)",
            r"go to ([a-zA-Z\s,]+)"
        ]
        
        destination = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                destination = match.group(1).strip()
                break
        
        if destination:
            maps_url = f"https://www.google.com/maps/search/{destination.replace(' ', '+')}"
            return {
                "type": "navigation",
                "message": f"Opening Google Maps for navigation to {destination}...",
                "redirect_url": maps_url,
                "destination": destination
            }
        else:
            return "Please specify a destination. Example: 'Navigate to Mumbai'"


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

    # ---- KNOWLEDGE QUESTIONS ----
    if "capital of" in text or "president of" in text or "largest" in text or "smallest" in text:
        return chat_with_openai(user_text)
    
    # ---- CAPABILITIES ----
    if any(word in text for word in ["help", "what can you do", "capabilities"]):
        return "I can help you with time, date, weather, latest news, basic math, jokes, and general conversation. What would you like to know?"

    # ---- DYNAMIC AI RESPONSE ----
    ai_response = chat_with_openai(user_text)
    
    # Cache the response for future use
    response_cache.set(cache_key, ai_response)
    
    return ai_response