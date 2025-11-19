import requests
import urllib.parse

def search_deezer_track(song_query):
    """Search Deezer for a track"""
    try:
        # Deezer API search
        search_url = "https://api.deezer.com/search"
        params = {
            'q': song_query,
            'limit': 1
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                track = data['data'][0]
                
                return {
                    'track_id': track['id'],
                    'title': track['title'],
                    'artist': track['artist']['name'],
                    'preview_url': track['preview'],  # 30-second preview
                    'deezer_url': track['link'],
                    'album_cover': track['album']['cover_medium']
                }
    
    except Exception as e:
        print(f"[DEEZER ERROR]: {e}")
    
    return None

def get_deezer_player_url(song_query):
    """Get Deezer player URL with instant playback"""
    
    # Search Deezer
    deezer_result = search_deezer_track(song_query)
    
    if deezer_result:
        # Create instant player URL with Deezer embed
        base_url = "file:///c:/Users/Yash/OneDrive/Desktop/STUDIO_IITB/frontend/deezer_player.html"
        params = {
            'song': song_query,
            'track_id': deezer_result['track_id'],
            'title': deezer_result['title'],
            'artist': deezer_result['artist'],
            'preview_url': deezer_result['preview_url'],
            'deezer_url': deezer_result['deezer_url'],
            'cover': deezer_result['album_cover']
        }
        
        param_string = urllib.parse.urlencode(params)
        player_url = f"{base_url}?{param_string}"
        
        return {
            'url': player_url,
            'song_title': f"{deezer_result['title']} by {deezer_result['artist']}",
            'primary_source': 'Deezer'
        }
    
    # Fallback to YouTube search if Deezer fails
    return f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"