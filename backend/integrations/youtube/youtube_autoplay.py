import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_youtube_autoplay_url(song_query):
    """Get YouTube URL that will autoplay"""
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
                    # Create a data URL that will auto-redirect and play
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Playing: {song_query}</title>
                        <style>
                            body {{ 
                                background: #000; 
                                color: #fff; 
                                font-family: Arial; 
                                text-align: center; 
                                padding: 50px; 
                            }}
                        </style>
                    </head>
                    <body>
                        <h2>🎵 Playing: {song_query}</h2>
                        <p>Redirecting to YouTube...</p>
                        <script>
                            setTimeout(() => {{
                                window.location.href = 'https://www.youtube.com/watch?v={video_id}&autoplay=1';
                            }}, 1000);
                        </script>
                    </body>
                    </html>
                    """
                    return f"data:text/html;charset=utf-8,{html_content}"
        
        # Fallback to search
        return f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"
        
    except Exception as e:
        print(f"[YOUTUBE ERROR]: {e}")
        return f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"