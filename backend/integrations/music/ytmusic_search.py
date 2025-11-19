import requests
import re
import urllib.parse

def search_youtube_music(song_query):
    """Search YouTube Music for a song"""
    try:
        # YouTube Music search URL
        search_url = f"https://music.youtube.com/search?q={urllib.parse.quote(song_query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Extract video ID from YouTube Music page
            video_id_pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
            matches = re.findall(video_id_pattern, response.text)
            
            if matches:
                video_id = matches[0]
                
                # Create YouTube Music URLs
                ytmusic_url = f"https://music.youtube.com/watch?v={video_id}"
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1"
                
                return {
                    'video_id': video_id,
                    'ytmusic_url': ytmusic_url,
                    'youtube_url': youtube_url,
                    'embed_url': embed_url,
                    'title': song_query
                }
    
    except Exception as e:
        print(f"[YTMUSIC ERROR]: {e}")
    
    return None

def get_ytmusic_player_url(song_query):
    """Get YouTube Music player URL with fallback"""
    
    # Try YouTube Music search first
    ytmusic_result = search_youtube_music(song_query)
    
    if ytmusic_result:
        return {
            'ytmusic_url': ytmusic_result['ytmusic_url'],
            'youtube_url': ytmusic_result['youtube_url'],
            'embed_url': ytmusic_result['embed_url'],
            'video_id': ytmusic_result['video_id'],
            'title': song_query,
            'source': 'YouTube Music'
        }
    
    # Fallback to regular YouTube search
    return f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"