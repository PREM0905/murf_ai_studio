# backend/free_music.py

import requests
import json
import os

def search_musicbrainz(query):
    """Free music search using MusicBrainz - No API key needed"""
    try:
        url = "https://musicbrainz.org/ws/2/recording"
        params = {
            'query': query,
            'fmt': 'json',
            'limit': 3
        }
        headers = {'User-Agent': 'VoiceAssistant/1.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data['recordings']:
            recording = data['recordings'][0]
            title = recording['title']
            artist = recording['artist-credit'][0]['name'] if recording.get('artist-credit') else 'Unknown'
            return f"That might be '{title}' by {artist}."
        else:
            return "I couldn't identify that song from the lyrics."
    except Exception as e:
        return "I'm having trouble identifying the song right now."

def search_lastfm(query):
    """Search using Last.fm API"""
    api_key = os.getenv("LASTFM_API_KEY")
    if not api_key:
        return search_musicbrainz(query)  # Fallback to free service
    
    try:
        url = "http://ws.audioscrobbler.com/2.0/"
        params = {
            'method': 'track.search',
            'track': query,
            'api_key': api_key,
            'format': 'json',
            'limit': 3
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['results']['trackmatches']['track']:
            track = data['results']['trackmatches']['track'][0]
            title = track['name']
            artist = track['artist']
            return f"That sounds like '{title}' by {artist}."
        else:
            return search_musicbrainz(query)  # Fallback
    except Exception as e:
        return search_musicbrainz(query)  # Fallback

def search_itunes(query):
    """Free music search using iTunes API - No API key needed"""
    try:
        url = "https://itunes.apple.com/search"
        params = {
            'term': query,
            'media': 'music',
            'entity': 'song',
            'limit': 3
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['results']:
            track = data['results'][0]
            title = track['trackName']
            artist = track['artistName']
            return f"That could be '{title}' by {artist}."
        else:
            return "I couldn't find that song."
    except Exception as e:
        return "I'm having trouble searching for music right now."

def identify_song_free(lyrics_or_title):
    """Main music identification using free services"""
    # Clean the input
    query = lyrics_or_title.strip()
    
    # Try iTunes first (most reliable and free)
    result = search_itunes(query)
    if "could be" in result:
        return result
    
    # Try Last.fm (if API key available)
    result = search_lastfm(query)
    if "sounds like" in result:
        return result
    
    # Fallback to MusicBrainz
    return search_musicbrainz(query)

def get_artist_info(artist_name):
    """Get artist information using free services"""
    try:
        # Use MusicBrainz for artist info
        url = "https://musicbrainz.org/ws/2/artist"
        params = {
            'query': artist_name,
            'fmt': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'VoiceAssistant/1.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data['artists']:
            artist = data['artists'][0]
            name = artist['name']
            country = artist.get('country', 'Unknown')
            begin_area = artist.get('begin-area', {}).get('name', 'Unknown')
            return f"{name} is an artist from {begin_area}, {country}."
        else:
            return f"I couldn't find information about {artist_name}."
    except Exception as e:
        return "I'm having trouble getting artist information right now."