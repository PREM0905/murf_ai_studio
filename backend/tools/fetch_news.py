import os
import requests

def get_latest_news(topic: str):
    """Fetch latest news via NewsAPI"""
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        return {"error": "Missing NEWS_API_KEY"}

    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={topic}&sortBy=publishedAt&apiKey={api_key}"
    )

    resp = requests.get(url).json()

    if "articles" not in resp or len(resp["articles"]) == 0:
        return {"error": "No news found"}

    article = resp["articles"][0]

    return {
        "headline": article["title"],
        "source": article["source"]["name"],
        "url": article["url"]
    }