import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

def get_spotify_access_token():
    """Get Spotify access token using client credentials"""
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        return None
    
    try:
        # Encode credentials
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        response = requests.post('https://accounts.spotify.com/api/token', 
                               headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            return response.json().get('access_token')
        
    except Exception as e:
        print(f"[SPOTIFY AUTH ERROR]: {e}")
    
    return None

def search_spotify_track(song_query):
    """Search for a track on Spotify"""
    access_token = get_spotify_access_token()
    
    if not access_token:
        return None
    
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'q': song_query,
            'type': 'track',
            'limit': 1
        }
        
        response = requests.get('https://api.spotify.com/v1/search', 
                              headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            tracks = data.get('tracks', {}).get('items', [])
            
            if tracks:
                track = tracks[0]
                return {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'spotify_url': track['external_urls']['spotify'],
                    'preview_url': track.get('preview_url'),
                    'web_player_url': f"https://open.spotify.com/embed/track/{track['id']}"
                }
    
    except Exception as e:
        print(f"[SPOTIFY SEARCH ERROR]: {e}")
    
    return None