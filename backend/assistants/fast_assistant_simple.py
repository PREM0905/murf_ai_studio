import sys
import os
import re
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import tools directly
from tools.weather import get_weather
from tools.fetch_news import get_latest_news
from tools.maps_navigation import navigate_to
from integrations.navigation.maps_navigation import get_directions, find_nearby, search_location

def extract_city_from_text(text):
    """Extract city name from user input"""
    patterns = [
        r"weather in ([a-zA-Z\s]+)",
        r"weather for ([a-zA-Z\s]+)", 
        r"weather of ([a-zA-Z\s]+)",
        r"temperature in ([a-zA-Z\s]+)",
        r"how.*weather.*in ([a-zA-Z\s]+)",
        r"what.*weather.*([a-zA-Z\s]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            # Clean up common words
            city = re.sub(r'\b(today|now|currently|right|now)\b', '', city, flags=re.IGNORECASE).strip()
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
            # Clean up common words
            topic = re.sub(r'\b(latest|today|current|recent)\b', '', topic, flags=re.IGNORECASE).strip()
            return topic
    
    return "general"

def generate_reply(user_message):
    """Generate intelligent replies with direct tool integration"""
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
        
        print(f"[WEATHER] Fetching weather for: {city}")
        result = get_weather(city)
        
        if isinstance(result, dict):
            if "error" in result:
                return f"Sorry, I couldn't get weather information for {city}. {result['error']}"
            else:
                return f"Weather in {result['city']}: {result['temp']}°C, {result['condition']}"
        else:
            return str(result)
    
    # News handling
    if "news" in text:
        topic = extract_news_topic(text)
        print(f"[NEWS] Fetching news for topic: {topic}")
        result = get_latest_news(topic)
        
        if isinstance(result, dict):
            if "error" in result:
                return f"Sorry, I couldn't fetch news about {topic}. {result['error']}"
            else:
                return f"Latest news: {result['headline']} (Source: {result['source']})"
        else:
            return str(result)
    
    # Enhanced Navigation handling
    if any(word in text for word in ["navigate", "directions", "route", "go to", "drive to", "how to get"]):
        # Check for directions between two places
        direction_patterns = [
            r"directions from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)",
            r"route from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)",
            r"how to get from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)",
            r"drive from ([a-zA-Z\s,]+) to ([a-zA-Z\s,]+)"
        ]
        
        origin = None
        destination = None
        
        for pattern in direction_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                origin = match.group(1).strip()
                destination = match.group(2).strip()
                break
        
        if origin and destination:
            print(f"[DIRECTIONS] From {origin} to {destination}")
            result = get_directions(origin, destination)
            
            if isinstance(result, dict):
                if "error" in result:
                    return f"Sorry, I couldn't get directions from {origin} to {destination}. {result['error']}"
                else:
                    response = f"Directions from {result['origin']} to {result['destination']}:\n"
                    response += f"Distance: {result.get('distance', 'N/A')}\n"
                    response += f"Duration: {result.get('duration', 'N/A')}\n"
                    if 'steps' in result:
                        response += "\nRoute steps:\n" + "\n".join(result['steps'][:5])
                    response += f"\n\nView full route: {result.get('maps_url', '')}"
                    return response
        else:
            # Single destination navigation
            destination_patterns = [
                r"navigate to ([a-zA-Z\s,]+)",
                r"directions to ([a-zA-Z\s,]+)",
                r"route to ([a-zA-Z\s,]+)",
                r"go to ([a-zA-Z\s,]+)",
                r"drive to ([a-zA-Z\s,]+)"
            ]
            
            for pattern in destination_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    destination = match.group(1).strip()
                    break
            
            if destination:
                print(f"[NAVIGATION] To {destination}")
                result = navigate_to(destination)
                if isinstance(result, dict):
                    steps = "\n".join(result.get("steps", []))
                    return f"Navigation to {result['destination']}:\n{steps}\n\nFor detailed directions, try: 'directions from [your location] to {destination}'"
                else:
                    return str(result)
        
        return "Please specify a destination. Examples:\n• 'Navigate to Mumbai'\n• 'Directions from Delhi to Mumbai'\n• 'Route from my location to airport'"
    
    # Find nearby places
    if any(phrase in text for phrase in ["find nearby", "near me", "closest", "find restaurants", "find hotels"]):
        location = "current location"
        place_type = "restaurant"
        
        # Extract location
        location_patterns = [
            r"near ([a-zA-Z\s,]+)",
            r"in ([a-zA-Z\s,]+)",
            r"around ([a-zA-Z\s,]+)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                break
        
        # Extract place type
        if "restaurant" in text or "food" in text or "eat" in text:
            place_type = "restaurant"
        elif "hotel" in text or "stay" in text:
            place_type = "hotel"
        elif "gas" in text or "fuel" in text or "petrol" in text:
            place_type = "gas station"
        elif "hospital" in text or "medical" in text:
            place_type = "hospital"
        elif "atm" in text or "bank" in text:
            place_type = "atm"
        elif "pharmacy" in text or "medicine" in text:
            place_type = "pharmacy"
        
        print(f"[NEARBY] Finding {place_type} near {location}")
        result = find_nearby(location, place_type)
        
        if isinstance(result, dict):
            if "error" in result:
                return f"Sorry, I couldn't find {place_type} near {location}. {result['error']}"
            else:
                response = f"Found {place_type}s near {result['location']}:\n\n"
                for i, place in enumerate(result.get('results', [])[:3], 1):
                    response += f"{i}. {place['name']}\n"
                    response += f"   Rating: {place['rating']}\n"
                    response += f"   Address: {place['address']}\n\n"
                response += f"View on map: {result.get('maps_url', '')}"
                return response
        
        return f"I can help you find places nearby. Try: 'Find restaurants near Mumbai' or 'Hotels in Delhi'"
    
    # Search for specific locations
    if any(phrase in text for phrase in ["where is", "location of", "find location", "search for"]):
        search_patterns = [
            r"where is ([a-zA-Z\s,]+)",
            r"location of ([a-zA-Z\s,]+)",
            r"find location ([a-zA-Z\s,]+)",
            r"search for ([a-zA-Z\s,]+)"
        ]
        
        query = None
        for pattern in search_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                break
        
        if query:
            print(f"[SEARCH] Looking for {query}")
            result = search_location(query)
            
            if isinstance(result, dict):
                if "error" in result:
                    return f"Sorry, I couldn't find information about {query}. {result['error']}"
                else:
                    response = f"Found: {result['name']}\n"
                    response += f"Address: {result['address']}\n"
                    if result.get('rating') != 'N/A':
                        response += f"Rating: {result['rating']}\n"
                    response += f"\nView on map: {result.get('maps_url', '')}"
                    return response
        
        return "Please specify what you're looking for. Example: 'Where is Taj Mahal?' or 'Location of Mumbai Airport'"
    
    # Capabilities
    if any(phrase in text for phrase in ["what can you do", "help", "capabilities"]):
        return "I can help you with:\n• Weather reports for any city\n• Latest news on any topic\n• Navigation and directions\n• Find nearby places\n• Location search\n• Time and date information\n• General conversations\n\nTry asking: 'Weather in Delhi', 'News about technology', or 'Directions to Mumbai'"
    
    # Math operations
    if any(word in text for word in ["calculate", "plus", "minus", "multiply", "divide"]) or any(op in text for op in ["+", "-", "*", "/"]):
        try:
            # Simple math evaluation
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
    
    # Default response with suggestions
    return f"I understand you said: '{user_message}'. I can help with weather reports, news updates, navigation, location search, and general questions. What would you like to know?"