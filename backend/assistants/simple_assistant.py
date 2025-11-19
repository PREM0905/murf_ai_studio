import sys
import os
import requests
import re
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.search.gemini_search import search_with_gemini, is_search_query
from integrations.music.simple_music import get_instant_music_url

load_dotenv()

def get_weather_simple(city):
    """Simple weather function using free service"""
    try:
        # Use wttr.in free service with simple format
        url = f"http://wttr.in/{city}?format=%l:+%C+%t"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            weather = response.text.strip()
            if weather and "Unknown" not in weather:
                # Clean up the response
                weather = weather.replace(":", " -")
                return f"Weather: {weather}"
            else:
                return f"Could not find weather for {city}"
        else:
            return f"Weather service unavailable for {city}"
    except Exception as e:
        return f"Weather error for {city}"

def get_news_simple(topic):
    """Simple news function"""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "News service unavailable"
    
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {'apiKey': api_key, 'country': 'us', 'pageSize': 1}
        if topic != "general":
            params['q'] = topic
            
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('articles'):
            article = data['articles'][0]
            return f"Latest: {article['title']} - {article['source']['name']}"
        else:
            return "No news found"
    except:
        return "News service unavailable"

def generate_reply(user_text):
    """Simple working assistant"""
    if not user_text:
        return "Please say something"
    
    text = user_text.lower().strip()
    
    # Personal questions about creator
    creator_names = ["yash", "yash shay", "yash sahai", "yash sahay", "prem"]
    if any(name in text for name in creator_names):
        if any(word in text for word in ["who is", "who's", "tell me about", "about"]):
            return "He is the one who created me. I am his personal assistant."
    
    # Personal questions about designer
    designer_names = ["adi", "aditya", "aditya panwar"]
    if any(name in text for name in designer_names):
        if any(word in text for word in ["who is", "who's", "tell me about", "about"]):
            return "Aditya Panwar is my talented designer who crafted my beautiful user interface and visual identity. He created the stunning reactor-style design with glowing cyan elements, smooth animations, and futuristic aesthetics that make me look like a real AI from science fiction. Aditya designed my dual-mode interface, the elegant message panels, the pulsing reactor core, and all the visual effects that bring me to life. His design expertise made me not just functional, but visually impressive and user-friendly. He's a creative genius who transformed code into art!"
    
    # Shutdown commands (check before greetings)
    shutdown_phrases = [
        "bye bye studio", "please shut down", 
        "shutdown studio", "close studio", "turn off studio",
        "exit studio", "quit studio", "goodbye studio"
    ]
    
    if any(phrase in text for phrase in shutdown_phrases):
        return {
            "type": "shutdown",
            "message": "Thank you for using STUDIO! Shutting down now. Goodbye!",
            "action": "close_window"
        }
    
    # Music/Song requests (check before greetings)
    music_keywords = ["play", "song", "music", "listen to", "put on"]
    if any(keyword in text for keyword in music_keywords):
        # Extract song name
        song_query = text
        
        # Clean up common phrases
        cleanup_phrases = ["play", "song", "music", "listen to", "put on", "the song", "a song"]
        for phrase in cleanup_phrases:
            song_query = song_query.replace(phrase, "").strip()
        
        if song_query:
            # Get instant music player
            music_result = get_instant_music_url(song_query)
            
            if isinstance(music_result, dict):
                return {
                    "type": "music",
                    "message": f"Playing '{song_query}'. Opening instant player...",
                    "redirect_url": music_result["url"],
                    "song": song_query
                }
            else:
                return {
                    "type": "music",
                    "message": f"Searching for '{song_query}'. Opening YouTube...",
                    "redirect_url": music_result,
                    "song": song_query
                }
        else:
            return "Please specify which song you'd like to play."
    
    # Comprehensive greetings
    greetings = {
        # Basic greetings
        "hello": "Hello! How can I assist you today?",
        "hi": "Hi there! What can I do for you?",
        "hey": "Hey! I'm here to help.",
        "hola": "Hola! How may I help you?",
        "namaste": "Namaste! I'm at your service.",
        
        # Morning greetings
        "good morning": "Good morning! Hope you have a wonderful day ahead!",
        "morning": "Good morning! Ready to start the day?",
        
        # Afternoon greetings
        "good afternoon": "Good afternoon! How's your day going?",
        "afternoon": "Good afternoon! What can I help you with?",
        
        # Evening greetings
        "good evening": "Good evening! How can I assist you tonight?",
        "evening": "Good evening! What do you need help with?",
        
        # Night greetings
        "good night": "Good night! Sweet dreams and rest well!",
        "goodnight": "Good night! Sleep tight!",
        "night": "Good night! Have a peaceful sleep!",
        
        # Farewells
        "bye": "Goodbye! Take care and see you soon!",
        "goodbye": "Goodbye! It was great helping you!",
        "see you": "See you later! Have a great time!",
        "take care": "You take care too! Stay safe!",
        "farewell": "Farewell! Until we meet again!",
        
        # Casual greetings
        "what's up": "Not much, just here to help you! What's up with you?",
        "whats up": "Not much, just here to help you! What's up with you?",
        "howdy": "Howdy! What can I do for you today?",
        "yo": "Yo! What do you need?",
        
        # Polite greetings
        "greetings": "Greetings! I'm pleased to assist you.",
        "salutations": "Salutations! How may I be of service?"
    }
    
    # Check for greetings (exact matches or word boundaries)
    import re
    for greeting, response in greetings.items():
        # Use word boundaries to avoid false matches like 'hi' in 'machine learning'
        if re.search(r'\b' + re.escape(greeting) + r'\b', text) or text == greeting:
            return response
    
    # Weather
    if "weather" in text:
        # Extract city
        city = "Mumbai"  # default
        if " in " in text:
            parts = text.split(" in ")
            if len(parts) > 1:
                city = parts[1].strip().title()
        elif " for " in text:
            parts = text.split(" for ")
            if len(parts) > 1:
                city = parts[1].strip().title()
        
        return get_weather_simple(city)
    
    # News
    if "news" in text:
        topic = "general"
        if "about" in text:
            parts = text.split("about")
            if len(parts) > 1:
                topic = parts[1].strip()
        
        return get_news_simple(topic)
    
    # Navigation
    if any(word in text for word in ["navigate", "directions", "route", "go to", "from"]):
        import re
        
        # Check for route from X to Y
        route_patterns = [
            r"route from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)",
            r"directions from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)",
            r"navigate from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)",
            r"go from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)",
            r"how to go from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)"
        ]
        
        origin = None
        destination = None
        
        # Check for origin-destination patterns first
        for pattern in route_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                origin = match.group(1).strip().title()
                destination = match.group(2).strip().title()
                break
        
        if origin and destination:
            # Route from origin to destination
            maps_url = f"https://www.google.com/maps/dir/{origin.replace(' ', '+')}/{destination.replace(' ', '+')}"
            return {
                "type": "navigation",
                "message": f"Finding route from {origin} to {destination}. Redirecting to Google Maps...",
                "redirect_url": maps_url,
                "destination": f"{origin} to {destination}"
            }
        else:
            # Single destination patterns
            destination_patterns = [
                r"navigate to ([a-zA-Z\s,]+)",
                r"directions to ([a-zA-Z\s,]+)",
                r"route to ([a-zA-Z\s,]+)",
                r"go to ([a-zA-Z\s,]+)"
            ]
            
            for pattern in destination_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    destination = match.group(1).strip().title()
                    break
            
            if destination:
                maps_url = f"https://www.google.com/maps/search/{destination.replace(' ', '+')}"
                return {
                    "type": "navigation",
                    "message": f"Navigating to {destination}. Redirecting to Google Maps...",
                    "redirect_url": maps_url,
                    "destination": destination
                }
            else:
                return "Please specify destination. Examples:\n• 'Navigate to Mumbai'\n• 'Route from Delhi to Mumbai'"
    
    # Time
    if "time" in text:
        return f"Current time: {datetime.now().strftime('%I:%M %p')}"
    
    # Date
    if "date" in text or "today" in text:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
    

    
    # About STUDIO
    if any(phrase in text for phrase in ["what are you", "who are you", "about studio", "what is studio"]):
        return "I am STUDIO - an advanced AI voice assistant created by Yash Sahay. I'm a comprehensive intelligent system with voice recognition, text-to-speech, wake word detection, music playback, weather reports, news updates, navigation, and AI-powered search capabilities. I can understand natural language, process voice commands, play music from YouTube Music, provide real-time weather information, fetch latest news, navigate locations using Google Maps, search and learn using Gemini AI, and have natural conversations. I feature a beautiful reactor-style interface designed by Aditya Panwar, with dual voice and text modes, wake word activation by saying 'Studio', and seamless integration of multiple AI services. I represent the cutting edge of personal AI assistant technology!"
    
    # Help
    if "help" in text or "what can you do" in text:
        return "I can help with:\n• Weather: 'weather in Mumbai'\n• News: 'news about technology'\n• Navigation: 'navigate to Delhi'\n• Routes: 'route from Mumbai to Delhi'\n• Music: 'play Despacito'\n• Search & Learn: 'tell me about AI' or 'what is quantum physics?'\n• Wake word: Say 'Studio' for hands-free activation\n• Time and date\n• Personal conversations and much more!"
    
    # Search & Learn with Gemini AI
    if is_search_query(user_text):
        result = search_with_gemini(user_text)
        return {
            "type": "search",
            "message": result["answer"],
            "redirect_url": result["search_url"],
            "query": user_text
        }
    
    # Default
    return f"I heard: '{user_text}'. Try asking about weather, news, navigation, search queries, or time!"