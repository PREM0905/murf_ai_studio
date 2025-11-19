import os
import requests

def get_weather(city: str):
    """Fetch weather using OpenWeatherMap API"""
    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        return {"error": "Missing WEATHER_API_KEY"}

    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={api_key}&units=metric"
        )

        resp = requests.get(url, timeout=10)
        data = resp.json()

        if resp.status_code == 200 and "main" in data:
            return {
                "city": data["name"],
                "temp": round(data["main"]["temp"]),
                "condition": data["weather"][0]["description"]
            }
        else:
            return {"error": f"Weather data not found for {city}"}

    except Exception as e:
        return {"error": f"Weather service error: {str(e)}"}