import sys
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load keys
load_dotenv()

# Import your tools
from tools.weather import get_weather
from tools.fetch_news import get_latest_news
from tools.maps_navigation import navigate_to

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_reply(user_message):
    """
    Main agent logic with function calling
    """
    try:
        # Define function schemas for OpenAI
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather information for a city",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city name to get weather for"
                            }
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_latest_news",
                    "description": "Get latest news about a topic",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The news topic to search for"
                            }
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "navigate_to",
                    "description": "Get navigation directions to a destination",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "destination": {
                                "type": "string",
                                "description": "The destination to navigate to"
                            }
                        },
                        "required": ["destination"]
                    }
                }
            }
        ]

        # First call to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}],
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # Check if tool calls were made
        if message.tool_calls:
            # Execute the tool call
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"[TOOL CALL] {function_name} with args: {function_args}")

            # Execute the appropriate function
            if function_name == "get_weather":
                tool_result = get_weather(**function_args)
            elif function_name == "get_latest_news":
                tool_result = get_latest_news(**function_args)
            elif function_name == "navigate_to":
                tool_result = navigate_to(**function_args)
            else:
                tool_result = {"error": "Unknown function"}

            # Second call with tool result
            messages = [
                {"role": "user", "content": user_message},
                message,
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(tool_result)
                }
            ]

            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )

            return final_response.choices[0].message.content

        else:
            # No tool call needed, return direct response
            return message.content

    except Exception as e:
        print(f"[ERROR] OpenAI API error: {e}")
        # Fallback to simple responses
        text = user_message.lower()
        
        if "weather" in text:
            if "mumbai" in text:
                return get_weather("Mumbai")
            else:
                return get_weather("New York")
        elif "news" in text:
            return get_latest_news("general")
        elif "hello" in text or "hi" in text:
            return "Hello! I'm STUDIO, your assistant. I can help with weather, news, and general questions."
        else:
            return f"I understand you said: '{user_message}'. I can help with weather, news, and general queries."