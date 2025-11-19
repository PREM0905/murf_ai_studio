import requests
import urllib.parse

def search_jiosaavn_track(song_query):
    """Search JioSaavn for a track"""
    try:
        # JioSaavn API search
        search_url = "https://www.jiosaavn.com/api.php"
        params = {
            'p': '1',
            'q': song_query,
            'n': '1',
            '_format': 'json',
            '_marker': '0',
            'api_version': '4',
            'ctx': 'web6dot0'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('results') and len(data['results']) > 0:
                track = data['results'][0]
                
                return {
                    'track_id': track.get('id', ''),
                    'title': track.get('title', ''),
                    'artist': track.get('more_info', {}).get('artistMap', {}).get('primary_artists', [{}])[0].get('name', ''),
                    'preview_url': track.get('more_info', {}).get('320kbps', ''),
                    'jiosaavn_url': track.get('perma_url', ''),
                    'album_cover': track.get('image', '').replace('150x150', '500x500')
                }
    
    except Exception as e:
        print(f"[JIOSAAVN ERROR]: {e}")
    
    return None

def get_instant_streaming_url(song_query):
    """Get instant streaming music URL"""
    
    # Try JioSaavn first
    jiosaavn_result = search_jiosaavn_track(song_query)
    
    if jiosaavn_result and jiosaavn_result['preview_url']:
        # Create instant player URL
        base_url = "file:///c:/Users/Yash/OneDrive/Desktop/STUDIO_IITB/frontend/streaming_player.html"
        params = {
            'song': song_query,
            'title': jiosaavn_result['title'],
            'artist': jiosaavn_result['artist'],
            'stream_url': jiosaavn_result['preview_url'],
            'cover': jiosaavn_result['album_cover'],
            'source': 'JioSaavn'
        }
        
        param_string = urllib.parse.urlencode(params)
        player_url = f"{base_url}?{param_string}"
        
        return {
            'url': player_url,
            'song_title': f"{jiosaavn_result['title']} by {jiosaavn_result['artist']}",
            'primary_source': 'JioSaavn'
        }
    
    # Fallback to YouTube search
    return f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"