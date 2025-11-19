import sys
import os
import urllib.parse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from integrations.music.jiosaavn_music import get_instant_streaming_url
from integrations.youtube.youtube_search import get_first_youtube_video

def get_instant_music_url(song_query):
    """Get instant music player URL"""
    
    # Try JioSaavn first (has instant streaming)
    streaming_result = get_instant_streaming_url(song_query)
    
    if isinstance(streaming_result, dict):
        return {
            'url': streaming_result['url'],
            'song_title': streaming_result['song_title'],
            'primary_source': 'JioSaavn'
        }
    
    # Fallback to YouTube
    youtube_result = get_first_youtube_video(song_query)
    
    # Create instant player URL
    base_url = "file:///c:/Users/Yash/OneDrive/Desktop/STUDIO_IITB/frontend/instant_player.html"
    params = {'song': song_query}
    
    if isinstance(youtube_result, dict) and 'video_id' in youtube_result:
        params['youtube'] = youtube_result['video_id']
        song_title = youtube_result.get('title', song_query)
    else:
        # Fallback - extract video ID from URL
        if isinstance(youtube_result, str) and 'watch?v=' in youtube_result:
            video_id = youtube_result.split('watch?v=')[1].split('&')[0]
            params['youtube'] = video_id
            song_title = song_query
        else:
            # No video found, return search URL
            return f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"
    
    # Build instant player URL
    param_string = urllib.parse.urlencode(params)
    player_url = f"{base_url}?{param_string}"
    
    return {
        'url': player_url,
        'song_title': song_title,
        'primary_source': 'YouTube'
    }