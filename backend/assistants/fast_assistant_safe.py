import os
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def safe_import():
    """Safely import tools with fallbacks"""
    try:
        from tools.weather import get_weather
        from tools.fetch_news import get_latest_news
        from tools.maps_navigation import navigate_to
        return get_weather, get_latest_news, navigate_to
    except Exception as e:
        print(f"Import error: {e}")
        # Fallback functions
        def fallback_weather(city):
            return {"error": "Weather service unavailable"}
        def fallback_news(topic):
            return {"error": "News service unavailable"}
        def fallback_nav(dest):
            return {"error": "Navigation service unavailable"}
        return fallback_weather, fallback_news, fallback_nav

# Import tools safely
get_weather, get_latest_news, navigate_to = safe_import()

def extract_city_from_text(text):
    """Extract city name from user input"""
    patterns = [
        r"weather in ([a-zA-Z\s]+)",
        r"weather for ([a-zA-Z\s]+)", 
        r"weather of ([a-zA-Z\s]+)",
        r"temperature in ([a-zA-Z\s]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            return city.title()
    
    return None

def extract_news_topic(text):
    """Extract news topic from user input"""
    patterns = [
        r"news about ([a-zA-Z\s]+)",
        r"news on ([a-zA-Z\s]+)",
        r"latest news ([a-zA-Z\s]+)",
        r"news from ([a-zA-Z\s]+)",
        r"([a-zA-Z\s]+) news"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            topic = match.group(1).strip()
            return topic
    
    return "general"

def generate_reply(user_message):
    """Generate intelligent replies with safe error handling"""
    try:
        if not user_message or user_message.strip() == "":
            return "I could not understand. Please repeat."

        text = user_message.lower().strip()
        
        # Greeting responses
        if any(word in text for word in ["hello", "hi", "hey", "good morning", "good evening"]):
            return "Hello! I'm STUDIO, your intelligent assistant. I can help with weather, news, navigation, and general queries."
        
        # Time and date
        if "time" in text and "weather" not in text:
            return f"Current time: {datetime.now().strftime('%I:%M %p')}"
        if "date" in text or "today" in text and "weather" not in text:
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
        
        # Identity
        if "name" in text or "who are you" in text:
            return "I'm STUDIO, your intelligent voice and text assistant. I can help with weather reports, latest news, navigation, and answer general questions."
        
        # Weather handling
        if any(word in text for word in ["weather", "temperature", "climate"]):
            city = extract_city_from_text(text)
            if not city:
                # Try to extract any city name from the text
                words = text.split()
                for word in words:
                    if len(word) > 3 and word.isalpha():
                        city = word.title()
                        break
                if not city:
                    city = "Mumbai"  # Default city
            
            try:
                result = get_weather(city)
                
                if isinstance(result, dict):
                    if "error" in result:
                        return f"Sorry, I couldn't get weather information for {city}. Please try another city."
                    else:
                        return f"Weather in {result['city']}: {result['temp']}°C, {result['condition']}"
                else:
                    return str(result)
            except Exception as e:
                return f"Weather service is currently unavailable. Please try again later."
        
        # News handling
        if "news" in text:
            topic = extract_news_topic(text)
            try:
                result = get_latest_news(topic)
                
                if isinstance(result, dict):
                    if "error" in result:
                        return f"Sorry, I couldn't fetch news about {topic}. Please try again later."
                    else:
                        return f"Latest news: {result['headline']} (Source: {result['source']})"
                else:
                    return str(result)
            except Exception as e:
                return "News service is currently unavailable. Please try again later."
        
        # Simple Navigation handling
        if any(word in text for word in ["navigate", "directions", "route", "go to"]):
            destination_patterns = [
                r"navigate to ([a-zA-Z\s,]+)",
                r"directions to ([a-zA-Z\s,]+)",
                r"route to ([a-zA-Z\s,]+)",
                r"go to ([a-zA-Z\s,]+)"
            ]
            
            destination = None
            for pattern in destination_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    destination = match.group(1).strip()
                    break
            
            if destination:
                try:
                    result = navigate_to(destination)
                    if isinstance(result, dict):
                        if "error" in result:
                            return f"Navigation service unavailable. You can search for '{destination}' on Google Maps."
                        else:
                            steps = "\n".join(result.get("steps", []))
                            return f"Navigation to {result['destination']}:\n{steps}"
                    else:
                        return str(result)
                except Exception as e:
                    return f"Navigation service unavailable. You can search for '{destination}' on Google Maps."
            else:
                return "Please specify a destination. Example: 'Navigate to Mumbai'"
        
        # Capabilities
        if any(phrase in text for phrase in ["what can you do", "help", "capabilities"]):
            return "I can help you with:\n• Weather reports for any city\n• Latest news on any topic\n• Navigation directions\n• Time and date information\n• General conversations\n\nTry asking: 'Weather in Delhi', 'News about technology', or 'Navigate to Mumbai'"
        
        # Math operations
        if any(word in text for word in ["calculate", "plus", "minus", "multiply", "divide"]) or any(op in text for op in ["+", "-", "*", "/"]):
            try:
                import re
                math_text = text.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
                numbers = re.findall(r'\d+(?:\.\d+)?', math_text)
                operators = re.findall(r'[+\-*/]', math_text)
                
                if len(numbers) >= 2 and len(operators) >= 1:
                    expr = f"{numbers[0]} {operators[0]} {numbers[1]}"
                    result = eval(expr)
                    return f"The answer is {result}"
            except:
                pass
            return "I can help with basic math. Try: 'What is 5 plus 3?'"
        
        # Default response
        return f"I understand you said: '{user_message}'. I can help with weather reports, news updates, navigation, and general questions. What would you like to know?"
        
    except Exception as e:
        print(f"Error in generate_reply: {e}")
        return "I'm experiencing some technical difficulties. Please try again or ask something else."