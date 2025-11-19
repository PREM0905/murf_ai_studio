import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistants.simple_assistant import generate_reply

user_text = "navigate to Delhi"
text = user_text.lower().strip()

print(f"Input: '{user_text}'")
print(f"Processed: '{text}'")

# Check each condition
print(f"Contains hello/hi/hey: {any(word in text for word in ['hello', 'hi', 'hey'])}")
print(f"Contains weather: {'weather' in text}")
print(f"Contains news: {'news' in text}")
print(f"Contains navigate/directions/route/go to: {any(word in text for word in ['navigate', 'directions', 'route', 'go to'])}")

# Test the actual function
result = generate_reply(user_text)
print(f"Result: {result}")