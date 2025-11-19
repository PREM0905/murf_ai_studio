# backend/song_identifier.py

import os
import requests
import json
import re

def identify_with_audd(lyrics):
    """Identify song using AudD API - Free tier available"""
    api_key = os.getenv("AUDD_API_KEY")
    if not api_key:
        return None
    
    try:
        url = "https://api.audd.io/findLyrics/"
        data = {
            'api_token': api_key,
            'q': lyrics
        }
        
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        
        if result['status'] == 'success' and result['result']:
            song = result['result'][0]
            title = song['title']
            artist = song['artist']
            return f"That's '{title}' by {artist}"
    except:
        pass
    return None

def identify_with_musixmatch(lyrics):
    """Identify song using Musixmatch API"""
    api_key = os.getenv("MUSIXMATCH_API_KEY")
    if not api_key:
        return None
    
    try:
        url = "https://api.musixmatch.com/ws/1.1/track.search"
        params = {
            'apikey': api_key,
            'q_lyrics': lyrics,
            'page_size': 3,
            'page': 1,
            's_track_rating': 'desc'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['message']['header']['status_code'] == 200:
            tracks = data['message']['body']['track_list']
            if tracks:
                track = tracks[0]['track']
                title = track['track_name']
                artist = track['artist_name']
                return f"That sounds like '{title}' by {artist}"
    except:
        pass
    return None

def identify_with_chartlyrics(lyrics):
    """Free song identification using ChartLyrics API - No key needed"""
    try:
        # Clean lyrics for search
        clean_lyrics = re.sub(r'[^\w\s]', '', lyrics).strip()
        words = clean_lyrics.split()[:10]  # First 10 words
        search_term = ' '.join(words)
        
        url = "http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect"
        params = {
            'artist': '',
            'song': search_term
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200 and 'LyricSong' in response.text:
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            
            song_elem = root.find('.//LyricSong')
            artist_elem = root.find('.//LyricArtist')
            
            if song_elem is not None and artist_elem is not None:
                title = song_elem.text
                artist = artist_elem.text
                if title and artist:
                    return f"That might be '{title}' by {artist}"
    except:
        pass
    return None

def identify_with_lyrics_ovh(lyrics):
    """Free lyrics search using lyrics.ovh API - No key needed"""
    try:
        # Extract key phrases from lyrics
        words = lyrics.lower().split()
        key_phrases = []
        
        # Look for common song patterns
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            if len(phrase) > 10:
                key_phrases.append(phrase)
        
        if not key_phrases:
            key_phrases = [lyrics[:50]]
        
        # Search with the most distinctive phrase
        search_phrase = key_phrases[0] if key_phrases else lyrics
        
        # Use a simple search approach
        url = f"https://api.lyrics.ovh/v1/search/{search_phrase}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                result = data['data'][0]
                title = result.get('title', '')
                artist = result.get('artist', {}).get('name', '')
                if title and artist:
                    return f"That could be '{title}' by {artist}"
    except:
        pass
    return None

def identify_song_comprehensive(lyrics):
    """Comprehensive song identification using multiple APIs"""
    
    # Clean and prepare lyrics
    lyrics = lyrics.strip()
    if len(lyrics) < 5:
        return "Please provide more lyrics for better identification."
    
    # Try paid APIs first (if available)
    result = identify_with_audd(lyrics)
    if result:
        return result
    
    result = identify_with_musixmatch(lyrics)
    if result:
        return result
    
    # Try free APIs
    result = identify_with_chartlyrics(lyrics)
    if result:
        return result
    
    result = identify_with_lyrics_ovh(lyrics)
    if result:
        return result
    
    # Fallback to existing free services
    from free_music import identify_song_free
    return identify_song_free(lyrics)

def extract_lyrics_from_text(text):
    """Extract potential lyrics from user input"""
    # Remove common phrases
    text = text.lower()
    remove_phrases = [
        "the song goes", "song that goes", "lyrics are", "lyrics go",
        "identify song", "what song", "find song", "song with lyrics"
    ]
    
    for phrase in remove_phrases:
        text = text.replace(phrase, "")
    
    # Clean up
    text = text.strip()
    text = re.sub(r'^["\']|["\']$', '', text)  # Remove quotes
    
    return text