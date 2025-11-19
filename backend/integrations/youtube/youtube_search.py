import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_first_youtube_video(song_query):
    """Get the first YouTube video for a song query"""
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    try:
        if api_key:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': song_query,
                'type': 'video',
                'maxResults': 1,
                'key': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    video_id = data['items'][0]['id']['videoId']
                    title = data['items'][0]['snippet']['title']
                    # Return video info for frontend to handle
                    return {
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "video_id": video_id,
                        "title": title
                    }
        
        # Fallback to search
        return f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"
        
    except Exception as e:
        print(f"[YOUTUBE ERROR]: {e}")
        return f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"