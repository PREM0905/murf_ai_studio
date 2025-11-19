# backend/audio_song_identifier.py

import os
import requests
import base64

def identify_song_from_audio(audio_file_path):
    """Identify song from audio file using AudD API"""
    api_key = os.getenv("AUDD_API_KEY")
    if not api_key:
        return "I can identify songs from audio, but need AUDD_API_KEY configured."
    
    try:
        url = "https://api.audd.io/"
        
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        data = {
            'api_token': api_key,
            'audio': audio_b64,
            'return': 'apple_music,spotify'
        }
        
        response = requests.post(url, data=data, timeout=30)
        result = response.json()
        
        if result.get('status') == 'success' and result.get('result'):
            song_info = result['result']
            title = song_info.get('title', 'Unknown')
            artist = song_info.get('artist', 'Unknown')
            
            # Try to get more details
            album = song_info.get('album', '')
            release_date = song_info.get('release_date', '')
            
            response_text = f"I identified the song: '{title}' by {artist}"
            if album:
                response_text += f" from the album '{album}'"
            if release_date:
                response_text += f" ({release_date})"
            
            return response_text
        else:
            return "I couldn't identify this song. The audio might be too short, unclear, or it might be a regional song not in my database."
            
    except Exception as e:
        return "I'm having trouble identifying the song from audio right now. Please try again."

def identify_song_shazam_style(audio_file_path):
    """Alternative song identification using Shazam-like approach"""
    try:
        # For now, return a helpful message about audio identification
        return "Audio song identification is being processed. For better results, try saying the song lyrics like 'the song goes [lyrics here]' or tell me the song name directly."
    except Exception as e:
        return "I'm having trouble with audio song identification right now."

def handle_song_identification_request(transcript, audio_file_path=None):
    """Handle song identification from both text and audio"""
    
    # Check if user is asking for song identification
    text = transcript.lower().strip()
    
    # If user mentions song identification keywords
    if any(phrase in text for phrase in ["identify this song", "what song is this", "name this song", "recognize this song"]):
        if audio_file_path:
            return identify_song_from_audio(audio_file_path)
        else:
            return "I can identify songs! Try playing a song and saying 'identify this song', or tell me some lyrics by saying 'the song goes [lyrics here]'."
    
    # If user provides lyrics
    if any(phrase in text for phrase in ["song goes", "lyrics", "song that goes"]):
        from song_identifier import identify_song_comprehensive, extract_lyrics_from_text
        lyrics_part = extract_lyrics_from_text(text)
        return identify_song_comprehensive(lyrics_part)
    
    # If user just says song name or artist
    if any(word in text for word in ["song", "music", "track"]) and not any(phrase in text for phrase in ["play", "stop", "pause"]):
        # Try to identify from the spoken text
        from free_music import identify_song_free
        return identify_song_free(text)
    
    return None  # Not a song identification request