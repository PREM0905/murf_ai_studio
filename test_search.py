from backend.simple_assistant import generate_reply
from backend.gemini_search import is_search_query

# Test cases for enhanced search functionality
test_cases = [
    # Should trigger search
    "artificial intelligence",
    "python programming", 
    "quantum physics",
    "machine learning",
    "blockchain technology",
    "what is AI?",
    "how to code",
    "search for cats",
    "find information about space",
    "tell me about history",
    
    # Should NOT trigger search (specific commands)
    "weather in Mumbai",
    "play music",
    "hello",
    "good morning",
    "navigate to Delhi",
    "latest news",
    "what time is it",
    "bye bye studio",
    
    # Edge cases
    "AI",
    "NASA",
    "COVID",
    "Bitcoin"
]

print("🔍 Testing Enhanced Search Detection\n")
print("=" * 60)

for i, test_query in enumerate(test_cases, 1):
    print(f"\n{i:2d}. Testing: '{test_query}'")
    
    # Test search detection
    is_search = is_search_query(test_query)
    print(f"    Search detected: {is_search}")
    
    # Test full response
    response = generate_reply(test_query)
    
    if isinstance(response, dict):
        response_type = response.get('type', 'unknown')
        message = response.get('message', '')[:80] + "..." if len(response.get('message', '')) > 80 else response.get('message', '')
        print(f"    Response type: {response_type}")
        print(f"    Message: {message}")
        
        if response_type == 'search':
            print(f"    ✅ SEARCH - Will redirect to Google")
        elif response_type in ['navigation', 'music']:
            print(f"    ✅ {response_type.upper()} - Handled as command")
        else:
            print(f"    ✅ {response_type.upper()} - Other response")
    else:
        print(f"    Response: {str(response)[:80]}...")
        if is_search:
            print(f"    ❌ Expected search but got text response")
        else:
            print(f"    ✅ TEXT - Handled as expected")

print("\n" + "=" * 60)
print("🎯 Test Summary:")
print("✅ = Working as expected")
print("❌ = Needs attention")
print("\nExpected behavior:")
print("- General topics should trigger search & redirect")
print("- Specific commands should be handled directly")
print("- Greetings should get greeting responses")