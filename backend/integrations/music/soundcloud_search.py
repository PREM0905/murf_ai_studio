import requests
import re

def search_soundcloud_track(song_query):
    """Search SoundCloud for a track and return embed URL"""
    try:
        # SoundCloud search URL
        search_url = f"https://soundcloud.com/search?q={song_query.replace(' ', '%20')}"
        
        # Get search results page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Extract first track URL from HTML
            track_pattern = r'soundcloud\.com/([^/]+)/([^"?\s]+)'
            matches = re.findall(track_pattern, response.text)
            
            if matches:
                artist, track = matches[0]
                track_url = f"https://soundcloud.com/{artist}/{track}"
                
                # Create embed URL with autoplay
                embed_url = f"https://w.soundcloud.com/player/?url={track_url}&auto_play=true&hide_related=true&show_comments=false&show_user=true&show_reposts=false&show_teaser=false"
                
                return {
                    'embed_url': embed_url,
                    'track_url': track_url,
                    'artist': artist.replace('-', ' ').title(),
                    'track': track.replace('-', ' ').title()
                }
    
    except Exception as e:
        print(f"[SOUNDCLOUD ERROR]: {e}")
    
    return None