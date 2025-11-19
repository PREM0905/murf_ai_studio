import os
import requests
import re
import random
import json
import base64
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_weather_simple(city):
    """Get weather information"""
    try:
        url = f"http://wttr.in/{city}?format=%l:+%C+%t"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            weather = response.text.strip()
            if weather and "Unknown" not in weather:
                weather = weather.replace(":", " -")
                return f"Weather: {weather}"
            else:
                return f"Could not find weather for {city}"
        else:
            return f"Weather service unavailable for {city}"
    except Exception as e:
        return f"Weather error for {city}"

def get_news_simple(topic):
    """Get latest news"""
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

def calculate_math(expression):
    """Safe math calculator"""
    try:
        # Clean expression
        expression = expression.replace("plus", "+").replace("minus", "-")
        expression = expression.replace("times", "*").replace("multiply", "*")
        expression = expression.replace("divided by", "/").replace("divide", "/")
        expression = expression.replace("power", "**").replace("squared", "**2")
        
        # Only allow safe characters
        if re.match(r'^[\d+\-*/().\s]+$', expression):
            result = eval(expression)
            return f"Result: {result}"
        else:
            return "Invalid mathematical expression"
    except:
        return "Math calculation error"

def get_random_fact():
    """Get random interesting fact"""
    facts = [
        "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old!",
        "A group of flamingos is called a 'flamboyance'.",
        "Octopuses have three hearts and blue blood.",
        "Bananas are berries, but strawberries aren't.",
        "A day on Venus is longer than its year.",
        "Sharks have been around longer than trees.",
        "The human brain uses about 20% of the body's total energy.",
        "There are more possible games of chess than atoms in the observable universe."
    ]
    return random.choice(facts)

def get_joke():
    """Get random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "What do you call a fake noodle? An impasta!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why did the math book look so sad? Because it had too many problems!",
        "What's the best thing about Switzerland? I don't know, but the flag is a big plus!",
        "Why don't programmers like nature? It has too many bugs!"
    ]
    return random.choice(jokes)

def get_quote():
    """Get inspirational quote"""
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Life is what happens to you while you're busy making other plans. - John Lennon",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "It is during our darkest moments that we must focus to see the light. - Aristotle",
        "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
        "The only impossible journey is the one you never begin. - Tony Robbins"
    ]
    return random.choice(quotes)

def get_password(length=12):
    """Generate secure password"""
    import string
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(chars) for _ in range(length))
    return f"Generated password: {password}"

def flip_coin():
    """Flip a coin"""
    result = random.choice(["Heads", "Tails"])
    return f"Coin flip result: {result}"

def roll_dice(sides=6):
    """Roll dice"""
    result = random.randint(1, sides)
    return f"Dice roll ({sides}-sided): {result}"

def get_color_info(color):
    """Get color information"""
    colors = {
        "red": "Red is associated with energy, passion, and strength. Hex: #FF0000",
        "blue": "Blue represents trust, loyalty, and wisdom. Hex: #0000FF",
        "green": "Green symbolizes nature, growth, and harmony. Hex: #00FF00",
        "yellow": "Yellow represents happiness, optimism, and creativity. Hex: #FFFF00",
        "purple": "Purple is associated with luxury, creativity, and mystery. Hex: #800080",
        "orange": "Orange represents enthusiasm, creativity, and warmth. Hex: #FFA500",
        "black": "Black symbolizes elegance, power, and sophistication. Hex: #000000",
        "white": "White represents purity, simplicity, and cleanliness. Hex: #FFFFFF"
    }
    return colors.get(color.lower(), f"I don't have information about the color {color}")

def convert_units(value, from_unit, to_unit):
    """Convert between units"""
    conversions = {
        ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        ("meters", "feet"): lambda x: x * 3.28084,
        ("feet", "meters"): lambda x: x / 3.28084,
        ("kg", "pounds"): lambda x: x * 2.20462,
        ("pounds", "kg"): lambda x: x / 2.20462,
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x / 0.621371
    }
    
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](float(value))
        return f"{value} {from_unit} = {result:.2f} {to_unit}"
    else:
        return f"Cannot convert from {from_unit} to {to_unit}"

def get_zodiac_sign(month, day):
    """Get zodiac sign"""
    zodiac_signs = [
        (1, 20, "Capricorn"), (2, 19, "Aquarius"), (3, 21, "Pisces"),
        (4, 20, "Aries"), (5, 21, "Taurus"), (6, 21, "Gemini"),
        (7, 23, "Cancer"), (8, 23, "Leo"), (9, 23, "Virgo"),
        (10, 23, "Libra"), (11, 22, "Scorpio"), (12, 22, "Sagittarius")
    ]
    
    for end_month, end_day, sign in zodiac_signs:
        if (month == end_month and day <= end_day) or (month == end_month - 1 and day > end_day):
            return f"Your zodiac sign is {sign}"
    
    return "Capricorn"  # Default for late December

def generate_reply(user_text):
    """Super assistant with many features"""
    if not user_text:
        return "Please say something"
    
    text = user_text.lower().strip()
    
    # Greetings
    if any(f" {word} " in f" {text} " for word in ["hello", "hi", "hey"]) or text in ["hello", "hi", "hey"]:
        return "Hello! I'm STUDIO, your super assistant. I can help with weather, news, navigation, math, jokes, facts, and much more!"
    
    # Weather
    if "weather" in text:
        city = "Mumbai"
        if " in " in text:
            parts = text.split(" in ")
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
        
        # Route from X to Y
        route_patterns = [
            r"route from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)",
            r"directions from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)",
            r"navigate from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)"
        ]
        
        for pattern in route_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                origin = match.group(1).strip().title()
                destination = match.group(2).strip().title()
                maps_url = f"https://www.google.com/maps/dir/{origin.replace(' ', '+')}/{destination.replace(' ', '+')}"
                return {
                    "type": "navigation",
                    "message": f"Route from {origin} to {destination}:\n1. Calculating route...\n2. Estimating travel time...\n3. Opening directions...\n\nGoogle Maps: {maps_url}",
                    "redirect_url": maps_url,
                    "destination": f"{origin} to {destination}"
                }
        
        # Single destination
        destination_patterns = [
            r"navigate to ([a-zA-Z\s,]+)",
            r"directions to ([a-zA-Z\s,]+)",
            r"go to ([a-zA-Z\s,]+)"
        ]
        
        for pattern in destination_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                destination = match.group(1).strip().title()
                maps_url = f"https://www.google.com/maps/search/{destination.replace(' ', '+')}"
                return {
                    "type": "navigation",
                    "message": f"Navigation to {destination}:\n1. Opening Google Maps...\n2. Finding best route...\n3. Navigation ready!\n\nGoogle Maps: {maps_url}",
                    "redirect_url": maps_url,
                    "destination": destination
                }
        
        return "Please specify destination. Examples: 'Navigate to Mumbai' or 'Route from Delhi to Mumbai'"
    
    # Math calculations
    if any(word in text for word in ["calculate", "math", "plus", "minus", "times", "divide"]) or any(op in text for op in ["+", "-", "*", "/"]):
        # Extract mathematical expression
        math_patterns = [
            r"calculate (.+)",
            r"what is (.+)",
            r"solve (.+)"
        ]
        
        expression = None
        for pattern in math_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                expression = match.group(1).strip()
                break
        
        if not expression:
            # Try to find math in the text
            if any(op in text for op in ["+", "-", "*", "/"]):
                expression = text
        
        if expression:
            return calculate_math(expression)
        else:
            return "Please provide a mathematical expression. Example: 'Calculate 5 + 3'"
    
    # Unit conversions
    if "convert" in text:
        convert_pattern = r"convert (\d+\.?\d*) (\w+) to (\w+)"
        match = re.search(convert_pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1)
            from_unit = match.group(2)
            to_unit = match.group(3)
            return convert_units(value, from_unit, to_unit)
        else:
            return "Please specify conversion. Example: 'Convert 100 celsius to fahrenheit'"
    
    # Password generation
    if "password" in text or "generate password" in text:
        length_match = re.search(r"(\d+)", text)
        length = int(length_match.group(1)) if length_match else 12
        return get_password(length)
    
    # Coin flip
    if "flip coin" in text or "coin flip" in text:
        return flip_coin()
    
    # Dice roll
    if "roll dice" in text or "dice roll" in text:
        sides_match = re.search(r"(\d+)", text)
        sides = int(sides_match.group(1)) if sides_match else 6
        return roll_dice(sides)
    
    # Color information
    if "color" in text and any(color in text for color in ["red", "blue", "green", "yellow", "purple", "orange", "black", "white"]):
        for color in ["red", "blue", "green", "yellow", "purple", "orange", "black", "white"]:
            if color in text:
                return get_color_info(color)
    
    # Random fact
    if "fact" in text or "tell me something interesting" in text:
        return get_random_fact()
    
    # Joke
    if "joke" in text:
        return get_joke()
    
    # Quote
    if "quote" in text or "inspire me" in text:
        return get_quote()
    
    # Time
    if "time" in text:
        return f"Current time: {datetime.now().strftime('%I:%M %p')}"
    
    # Date
    if "date" in text or "today" in text:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
    
    # Day of week
    if "what day" in text:
        return f"Today is {datetime.now().strftime('%A')}"
    
    # Help
    if "help" in text or "what can you do" in text:
        return """I'm your super assistant! I can help with:
• Weather: 'weather in Mumbai'
• News: 'news about technology'
• Navigation: 'navigate to Delhi'
• Math: 'calculate 5 + 3'
• Conversions: 'convert 100 celsius to fahrenheit'
• Password: 'generate password'
• Fun: 'tell me a joke', 'flip coin', 'roll dice'
• Facts: 'tell me a fact'
• Quotes: 'inspire me'
• Colors: 'tell me about red color'
• Time & Date
And much more!"""
    
    # Default
    return f"I heard: '{user_text}'. I'm your super assistant with many features! Try asking for weather, news, math, jokes, facts, or say 'help' to see all features."