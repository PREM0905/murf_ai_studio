import sys
import os
import urllib.parse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from integrations.music.soundcloud_search import search_soundcloud_track
from integrations.youtube.youtube_search import get_first_youtube_video

def get_music_sources(song_query):
    """Get music from multiple sources"""
    sources = {}
    
    # Try SoundCloud first (better autoplay)
    soundcloud_result = search_soundcloud_track(song_query)
    if soundcloud_result:
        sources['soundcloud'] = soundcloud_result
    
    # Try YouTube
    youtube_result = get_first_youtube_video(song_query)
    if isinstance(youtube_result, dict):
        sources['youtube'] = youtube_result
    elif isinstance(youtube_result, str):
        # Extract video ID from URL
        if 'watch?v=' in youtube_result:
            video_id = youtube_result.split('watch?v=')[1].split('&')[0]
            sources['youtube'] = {
                'url': youtube_result,
                'video_id': video_id,
                'title': song_query
            }
    
    return sources

def create_music_player_url(song_query, sources):
    """Create URL for instant music player"""
    base_url = "file:///c:/Users/Yash/OneDrive/Desktop/STUDIO_IITB/frontend/instant_player.html"
    params = {'song': song_query}
    
    # Add SoundCloud if available (priority for autoplay)
    if 'soundcloud' in sources:
        soundcloud = sources['soundcloud']
        params['soundcloud'] = soundcloud['embed_url']
        params['artist'] = soundcloud['artist']
        params['track'] = soundcloud['track']
    
    # Add YouTube if available
    if 'youtube' in sources:
        youtube = sources['youtube']
        params['youtube'] = youtube['video_id']
        if 'track' not in params:
            params['track'] = youtube.get('title', song_query)
    
    # Build URL with parameters
    param_string = urllib.parse.urlencode(params)
    return f"{base_url}?{param_string}"

def get_best_music_result(song_query):
    """Get the best music result with fallback options"""
    sources = get_music_sources(song_query)
    
    if not sources:
        # Fallback to YouTube search
        return f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"
    
    # Create player URL with all available sources
    player_url = create_music_player_url(song_query, sources)
    
    # Determine primary source for response
    if 'soundcloud' in sources:
        primary_source = "SoundCloud"
        song_title = f"{sources['soundcloud']['track']} by {sources['soundcloud']['artist']}"
    elif 'youtube' in sources:
        primary_source = "YouTube"
        song_title = sources['youtube'].get('title', song_query)
    else:
        primary_source = "Web"
        song_title = song_query
    
    return {
        'url': player_url,
        'sources': sources,
        'primary_source': primary_source,
        'song_title': song_title
    }