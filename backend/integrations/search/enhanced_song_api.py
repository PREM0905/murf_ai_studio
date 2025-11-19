# backend/enhanced_song_api.py

import os
import requests
import json

def identify_hindi_english_song(lyrics_or_title):
    """Enhanced song identification for Hindi and English songs"""
    
    # Clean input
    query = lyrics_or_title.strip().lower()
    
    # Try multiple approaches
    result = try_genius_api(query)
    if result:
        return result
    
    result = try_musixmatch_api(query)
    if result:
        return result
    
    result = try_free_song_apis(query)
    if result:
        return result
    
    return get_fallback_song_response(query)

def try_genius_api(query):
    """Try Genius API for song identification"""
    api_key = os.getenv("GENIUS_API_KEY")
    if not api_key:
        return None
    
    try:
        url = "https://api.genius.com/search"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {"q": query}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        
        if data.get('response', {}).get('hits'):
            song = data['response']['hits'][0]['result']
            title = song.get('title', '')
            artist = song.get('primary_artist', {}).get('name', '')
            if title and artist:
                return f"That's '{title}' by {artist}"
    except:
        pass
    return None

def try_musixmatch_api(query):
    """Try Musixmatch API for song identification"""
    api_key = os.getenv("MUSIXMATCH_API_KEY")
    if not api_key:
        return None
    
    try:
        url = "https://api.musixmatch.com/ws/1.1/track.search"
        params = {
            'apikey': api_key,
            'q_lyrics': query,
            'page_size': 3,
            'page': 1,
            's_track_rating': 'desc'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('message', {}).get('header', {}).get('status_code') == 200:
            tracks = data.get('message', {}).get('body', {}).get('track_list', [])
            if tracks:
                track = tracks[0]['track']
                title = track.get('track_name', '')
                artist = track.get('artist_name', '')
                if title and artist:
                    return f"That sounds like '{title}' by {artist}"
    except:
        pass
    return None

def try_free_song_apis(query):
    """Try free song identification services"""
    try:
        # iTunes API (free)
        url = "https://itunes.apple.com/search"
        params = {
            'term': query,
            'media': 'music',
            'entity': 'song',
            'limit': 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('results'):
            for result in data['results']:
                title = result.get('trackName', '')
                artist = result.get('artistName', '')
                if title and artist:
                    # Check if query matches
                    if any(word in title.lower() for word in query.split()[:3]):
                        return f"That could be '{title}' by {artist}"
    except:
        pass
    return None

def get_fallback_song_response(query):
    """Fallback response for song identification"""
    
    # Common Hindi/English songs database
    song_database = {
        "tum hi ho": "Tum Hi Ho by Arijit Singh",
        "shape of you": "Shape of You by Ed Sheeran",
        "despacito": "Despacito by Luis Fonsi",
        "perfect": "Perfect by Ed Sheeran",
        "someone like you": "Someone Like You by Adele",
        "hello": "Hello by Adele",
        "rolling in the deep": "Rolling in the Deep by Adele",
        "bohemian rhapsody": "Bohemian Rhapsody by Queen",
        "imagine": "Imagine by John Lennon",
        "yesterday": "Yesterday by The Beatles",
        "let it be": "Let It Be by The Beatles",
        "hotel california": "Hotel California by Eagles",
        "stairway to heaven": "Stairway to Heaven by Led Zeppelin",
        "sweet child o mine": "Sweet Child O' Mine by Guns N' Roses",
        "we are the champions": "We Are the Champions by Queen",
        "don't stop believin": "Don't Stop Believin' by Journey",
        "billie jean": "Billie Jean by Michael Jackson",
        "thriller": "Thriller by Michael Jackson",
        "beat it": "Beat It by Michael Jackson",
        "like a prayer": "Like a Prayer by Madonna",
        "sweet dreams": "Sweet Dreams by Eurythmics",
        "karma chameleon": "Karma Chameleon by Culture Club",
        "kal ho naa ho": "Kal Ho Naa Ho by Sonu Nigam",
        "kabira": "Kabira by Tochi Raina",
        "raabta": "Raabta by Arijit Singh",
        "gerua": "Gerua by Arijit Singh & Antara Mitra",
        "janam janam": "Janam Janam by Arijit Singh",
        "ae dil hai mushkil": "Ae Dil Hai Mushkil by Arijit Singh"
    }
    
    # Check for matches
    for key, song in song_database.items():
        if key in query or any(word in query for word in key.split()):
            return f"That sounds like '{song}'"
    
    # Generic response
    return f"I couldn't identify that specific song. For better results, try saying 'the song goes [lyrics]' or 'what song is [song title]'. I work best with popular Hindi and English songs."

def enhanced_song_handler(user_query):
    """Main handler for song identification"""
    query = user_query.lower().strip()
    
    # Extract lyrics or song info
    if "song goes" in query:
        lyrics = query.split("song goes")[-1].strip()
        return identify_hindi_english_song(lyrics)
    elif "lyrics" in query:
        lyrics = query.replace("lyrics", "").replace("are", "").strip()
        return identify_hindi_english_song(lyrics)
    elif "what song" in query:
        song_part = query.replace("what song", "").replace("is", "").strip()
        return identify_hindi_english_song(song_part)
    else:
        return identify_hindi_english_song(query)