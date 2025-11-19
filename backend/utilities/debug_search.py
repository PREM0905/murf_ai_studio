import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.search.gemini_search import is_search_query

# Debug the failing cases
test_cases = ["machine learning", "tell me about history"]

for query in test_cases:
    print(f"\nDebugging: '{query}'")
    
    text_lower = query.lower()
    print(f"Lowercase: '{text_lower}'")
    
    # Check excluded keywords
    excluded_keywords = ["weather", "news", "navigate", "route", "time", "date", "help", "play", "song", "music", 
                        "hello", "hi", "hey", "good morning", "good afternoon", "good evening", "good night", 
                        "bye", "goodbye", "thanks", "thank you"]
    
    is_excluded = any(keyword in text_lower for keyword in excluded_keywords)
    print(f"Is excluded: {is_excluded}")
    
    if is_excluded:
        for keyword in excluded_keywords:
            if keyword in text_lower:
                print(f"  Excluded by: '{keyword}'")
    
    # Check search keywords
    search_keywords = [
        "search", "find", "look up", "tell me about", "what is", "who is", 
        "how to", "explain", "learn about", "information about", "help me understand",
        "research", "study", "explore", "discover", "show me", "teach me",
        "definition of", "meaning of", "about"
    ]
    
    has_search_keyword = any(keyword in text_lower for keyword in search_keywords)
    print(f"Has search keyword: {has_search_keyword}")
    
    if has_search_keyword:
        for keyword in search_keywords:
            if keyword in text_lower:
                print(f"  Found keyword: '{keyword}'")
    
    has_question_mark = "?" in query
    print(f"Has question mark: {has_question_mark}")
    
    result = is_search_query(query)
    print(f"Final result: {result}")