import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

def search_with_gemini(query):
    """Use Gemini AI to answer search queries and generate targeted search URLs"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Create targeted search URL based on query type
    search_url = create_targeted_search_url(query)
    
    if not api_key:
        return {
            "answer": f"I'd be happy to help you search for '{query}'. Opening the best results for you.",
            "search_url": search_url
        }
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [{
                "parts": [{
                    "text": f"Answer this search query concisely in 2-3 sentences: {query}"
                }]
            }]
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            answer = result["candidates"][0]["content"]["parts"][0]["text"]
            
            return {
                "answer": answer.strip(),
                "search_url": search_url
            }
        else:
            return {
                "answer": f"Here's what I found about '{query}'. Opening detailed results now.",
                "search_url": search_url
            }
            
    except Exception as e:
        print(f"[GEMINI ERROR]: {e}")
        return {
            "answer": f"I'll help you search for '{query}'. Opening targeted results now.",
            "search_url": search_url
        }

def create_targeted_search_url(query):
    """Create targeted search URLs based on query content"""
    query_lower = query.lower()
    encoded_query = urllib.parse.quote(query)
    
    # Educational content - prioritize educational sites
    if any(word in query_lower for word in ["what is", "how to", "explain", "learn", "tutorial", "guide"]):
        return f"https://www.google.com/search?q={encoded_query}+tutorial+guide+explanation&tbm="
    
    # Programming/coding queries
    if any(word in query_lower for word in ["python", "javascript", "coding", "programming", "code", "algorithm"]):
        return f"https://www.google.com/search?q={encoded_query}+tutorial+documentation+examples"
    
    # Scientific/technical topics
    if any(word in query_lower for word in ["quantum", "physics", "chemistry", "biology", "science", "research"]):
        return f"https://www.google.com/search?q={encoded_query}+explanation+research+academic"
    
    # Technology topics
    if any(word in query_lower for word in ["ai", "artificial intelligence", "machine learning", "technology", "computer"]):
        return f"https://www.google.com/search?q={encoded_query}+explanation+guide+overview"
    
    # Default: enhanced search with helpful terms
    return f"https://www.google.com/search?q={encoded_query}+information+guide+overview"

def is_search_query(text):
    """Detect if the input is a search/learning query"""
    search_keywords = [
        "search", "find", "look up", "tell me about", "what is", "who is", 
        "how to", "explain", "learn about", "information about", "help me understand",
        "research", "study", "explore", "discover", "show me", "teach me",
        "definition of", "meaning of", "about"
    ]
    
    text_lower = text.lower()
    
    # Check for explicit search keywords
    has_search_keyword = any(keyword in text_lower for keyword in search_keywords)
    has_question_mark = "?" in text
    
    # Exclude specific commands that aren't search queries
    excluded_keywords = ["weather", "news", "navigate", "route", "time", "date", "help", "play", "song", "music"]
    greeting_keywords = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "good night", 
                        "bye", "goodbye", "thanks", "thank you"]
    
    # Check for exact word matches for greetings to avoid false positives
    import re
    is_excluded = any(keyword in text_lower for keyword in excluded_keywords)
    is_greeting = any(re.search(r'\b' + re.escape(keyword) + r'\b', text_lower) for keyword in greeting_keywords)
    
    # If it has search keywords or question mark, it's a search
    if (has_search_keyword or has_question_mark) and not is_excluded and not is_greeting:
        return True
    
    # If it's not excluded and doesn't match other patterns, treat as search
    # This catches general queries like "artificial intelligence", "python programming", etc.
    if not is_excluded and not is_greeting and len(text.strip()) > 3:
        return True
    
    return False