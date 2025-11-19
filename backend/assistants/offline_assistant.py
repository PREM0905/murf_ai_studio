import os
import re
import random
from datetime import datetime

def calculate_math(expression):
    """Safe math calculator"""
    try:
        expression = expression.replace("plus", "+").replace("minus", "-")
        expression = expression.replace("times", "*").replace("multiply", "*")
        expression = expression.replace("divided by", "/").replace("divide", "/")
        
        if re.match(r'^[\d+\-*/().\s]+$', expression):
            result = eval(expression)
            return f"Result: {result}"
        else:
            return "Invalid mathematical expression"
    except:
        return "Math calculation error"

def get_joke():
    """Get random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "What do you call a fake noodle? An impasta!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why did the math book look so sad? Because it had too many problems!"
    ]
    return random.choice(jokes)

def get_fact():
    """Get random fact"""
    facts = [
        "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old!",
        "A group of flamingos is called a 'flamboyance'.",
        "Octopuses have three hearts and blue blood.",
        "Bananas are berries, but strawberries aren't.",
        "Sharks have been around longer than trees."
    ]
    return random.choice(facts)

def flip_coin():
    """Flip a coin"""
    result = random.choice(["Heads", "Tails"])
    return f"Coin flip result: {result}"

def roll_dice(sides=6):
    """Roll dice"""
    result = random.randint(1, sides)
    return f"Dice roll ({sides}-sided): {result}"

def get_password(length=12):
    """Generate password"""
    import string
    chars = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(random.choice(chars) for _ in range(length))
    return f"Generated password: {password}"

def generate_reply(user_text):
    """Offline assistant that works without internet"""
    if not user_text:
        return "Please say something"
    
    text = user_text.lower().strip()
    
    # Greetings
    if any(f" {word} " in f" {text} " for word in ["hello", "hi", "hey"]) or text in ["hello", "hi", "hey"]:
        return "Hello! I'm STUDIO, your offline assistant. I can help with math, jokes, facts, time, and more!"
    
    # Math calculations
    if any(word in text for word in ["calculate", "math", "plus", "minus", "times", "divide"]) or any(op in text for op in ["+", "-", "*", "/"]):
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
        
        if not expression and any(op in text for op in ["+", "-", "*", "/"]):
            expression = text
        
        if expression:
            return calculate_math(expression)
        else:
            return "Please provide a mathematical expression. Example: 'Calculate 5 + 3'"
    
    # Password generation
    if "password" in text:
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
    
    # Joke
    if "joke" in text:
        return get_joke()
    
    # Fact
    if "fact" in text:
        return get_fact()
    
    # Time
    if "time" in text:
        return f"Current time: {datetime.now().strftime('%I:%M %p')}"
    
    # Date
    if "date" in text or "today" in text:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
    
    # Weather (offline message)
    if "weather" in text:
        return "Weather service requires internet connection. Try other features like math, jokes, or time!"
    
    # News (offline message)
    if "news" in text:
        return "News service requires internet connection. Try other features like math, jokes, or time!"
    
    # Navigation (offline message)
    if any(word in text for word in ["navigate", "directions", "route"]):
        return "Navigation requires internet connection. Try other features like math, jokes, or time!"
    
    # Help
    if "help" in text or "what can you do" in text:
        return """I'm your offline assistant! I can help with:
• Math: 'calculate 5 + 3'
• Password: 'generate password'
• Fun: 'tell me a joke', 'flip coin', 'roll dice'
• Facts: 'tell me a fact'
• Time & Date
• And more offline features!"""
    
    # Default
    return f"I heard: '{user_text}'. I'm working offline! Try math, jokes, facts, time, or say 'help' for all features."